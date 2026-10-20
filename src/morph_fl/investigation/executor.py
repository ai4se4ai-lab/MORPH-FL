"""Deterministic static probes and explicitly registered container-only procedures.

LLMs choose registered procedure IDs; they cannot execute arbitrary host commands.
Test/trace/counterfactual procedures are supplied by the experiment owner and
run in an Apptainer image with a read-only source tree and a writable results
mount. Dynamic execution is opt-in; absent configuration is an explicit result.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import signal
import subprocess
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path

from morph_fl.domain import Evidence, Probe, SourceLocation, identity
from morph_fl.infrastructure.artifacts import ArtifactStore


@dataclass(frozen=True)
class SandboxConfig:
    image: str
    image_sha256: str
    procedures: dict[str, list[str]] = field(default_factory=dict)
    timeout_seconds: int = 120
    executable: str = "apptainer"

    def validate(self) -> None:
        image = Path(self.image)
        if not image.is_file() or not self.image_sha256:
            raise ValueError("A pinned sandbox image is required")
        with image.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != self.image_sha256:
            raise ValueError("Sandbox image digest differs")
        if self.timeout_seconds < 1:
            raise ValueError("Sandbox timeout must be positive")
        for command in self.procedures.values():
            if not command or not all(isinstance(arg, str) for arg in command):
                raise ValueError("Procedures must be nonempty argv lists")


class ProbeExecutor:
    def __init__(
        self,
        root: Path,
        revision: str,
        artifacts: ArtifactStore,
        sandbox: SandboxConfig | None = None,
    ):
        self.root = root.resolve()
        self.revision = revision
        self.artifacts = artifacts
        self.sandbox = sandbox
        if sandbox:
            sandbox.validate()

    def execute(self, probe: Probe, timeout_seconds: float | None = None) -> Evidence:
        path = (self.root / probe.path).resolve()
        if not path.is_relative_to(self.root) or not path.is_file() or path.suffix != ".py":
            raise ValueError("Probe source must be a Python file within the repository")
        text = path.read_text(errors="replace")
        digest = hashlib.sha256(text.encode()).hexdigest()
        line = int(probe.parameters.get("line", 1))
        lines = text.splitlines()
        if not 1 <= line <= len(lines):
            raise ValueError("Probe line outside source")
        location = SourceLocation(probe.path, line, line, self.revision, digest)
        if probe.kind == "source_quote":
            quote = probe.parameters.get("quote")
            if not isinstance(quote, str) or not quote.strip():
                raise ValueError("A source probe needs a nonempty quote")
            observation = dict(
                matched=quote in lines[line - 1], actual_line=lines[line - 1], quote=quote
            )
        elif probe.kind == "ast_query":
            query = probe.parameters.get("query", {})
            allowed = {"Call", "Assign", "Return", "Attribute", "Name", "FunctionDef", "Compare"}
            if query.get("node_type") not in allowed:
                raise ValueError("AST query requires an allowed node type")
            tree = ast.parse(text)
            matches = [
                dict(line=n.lineno, source=ast.unparse(n))
                for n in ast.walk(tree)
                if type(n).__name__ == query["node_type"]
                and (not query.get("contains") or query["contains"] in ast.unparse(n))
            ]
            observation = dict(matched=bool(matches), matches=matches)
        elif probe.kind == "counterfactual":
            baseline_id = probe.parameters.get("baseline_procedure_id")
            if not baseline_id:
                observation = dict(
                    blocked=True, reason="Counterfactual requires a registered baseline procedure"
                )
            else:
                baseline_parameters = dict(probe.parameters, procedure_id=baseline_id)
                baseline_parameters.pop("test_code", None)
                baseline = replace(probe, kind="test", parameters=baseline_parameters)
                half = timeout_seconds / 2 if timeout_seconds else None
                before = self._dynamic(baseline, half)
                after = self._dynamic(probe, half)
                observation = dict(
                    after,
                    baseline=before,
                    blocked=bool(before.get("blocked") or after.get("blocked")),
                    timed_out=bool(before.get("timed_out") or after.get("timed_out")),
                )
        else:
            observation = self._dynamic(probe, timeout_seconds)
        procedure = dict(kind=probe.kind, parameters=probe.parameters, revision=self.revision)
        artifact, artifact_digest = self.artifacts.put(
            json.dumps(dict(observation=observation, procedure=procedure), sort_keys=True).encode()
        )
        # Same procedure/result/source is the same observation, even across agents.
        eid = identity((probe.path, digest, procedure, observation))
        return Evidence(
            eid, probe.id, location, probe.kind, observation, procedure, artifact, artifact_digest
        )

    def _dynamic(self, probe: Probe, timeout_seconds: float | None = None) -> dict:
        config = self.sandbox
        procedure_id = probe.parameters.get("procedure_id")
        if not config or procedure_id not in config.procedures:
            return dict(blocked=True, reason="No registered isolated procedure for this probe")
        if not shutil.which(config.executable):
            return dict(blocked=True, reason="Apptainer is unavailable")
        with tempfile.TemporaryDirectory(prefix="morph-probe-") as tmp:
            generated = probe.parameters.get("test_code")
            if generated is not None:
                if not isinstance(generated, str) or len(generated) > 100_000:
                    raise ValueError("Generated probe code is invalid or too large")
                (Path(tmp) / "generated_probe.py").write_text(generated)
            # A trusted inner launcher distinguishes container startup failures from test results.
            # Probe code cannot create this envelope before the container actually starts.
            runner = Path(tmp) / "runner.py"
            runner.write_text(
                "import json, subprocess, sys\n"
                "from pathlib import Path\n"
                "command=json.loads(Path('/results/command.json').read_text())\n"
                "with Path('/results/procedure.log').open('wb') as out:\n"
                "    result=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT)\n"
                "Path('/results/completed.json').write_text(json.dumps({'returncode':result.returncode}))\n"
            )
            (Path(tmp) / "command.json").write_text(json.dumps(config.procedures[procedure_id]))
            log = Path(tmp) / "process.log"
            command = [
                config.executable,
                "exec",
                "--containall",
                "--cleanenv",
                "--net",
                "--network",
                "none",
                "--bind",
                f"{self.root}:/workspace:ro",
                "--bind",
                f"{tmp}:/results:rw",
                "--pwd",
                "/workspace",
                config.image,
                "python3",
                "/results/runner.py",
            ]
            timed_out = False
            with log.open("wb") as stream:
                process = subprocess.Popen(
                    command,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp},
                    start_new_session=True,
                )
                try:
                    process.wait(
                        timeout=min(
                            config.timeout_seconds, timeout_seconds or config.timeout_seconds
                        )
                    )
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            envelope = Path(tmp) / "completed.json"
            completed = json.loads(envelope.read_text()) if envelope.exists() else {}
            procedure_log = Path(tmp) / "procedure.log"
            raw = (procedure_log.read_bytes() if procedure_log.exists() else b"") + log.read_bytes()
            output_path, output_digest = self.artifacts.put(raw)
            return dict(
                returncode=completed.get("returncode"),
                launcher_returncode=process.returncode,
                stdout=raw[-1_000_000:].decode(errors="replace"),
                timed_out=timed_out,
                output_artifact=output_path,
                output_digest=output_digest,
                image_sha256=config.image_sha256,
                procedure_id=procedure_id,
                assumptions=probe.prediction.assumptions,
                blocked=not envelope.exists() or process.returncode != 0,
            )
