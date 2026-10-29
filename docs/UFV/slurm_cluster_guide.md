# UFV Slurm GPU Cluster: Guide for AI Agents

This document describes the cluster architecture, hardware, storage, and rules for using it. Read it fully before taking any action. Items marked **(general Slurm practice)** are standard Slurm usage that is not stated in the source diagrams. Everything else comes directly from them.

---

## 0. Golden Rules (read first)

1. **The login/staging host is NOT a compute machine.** `slurm.soc.ufv.ca` is only for SSH entry, file staging, and job management. **Never run training, inference, data processing, `pip install` of large environments, or any heavy command directly on it.**
2. **All computation must go through Slurm**: `sbatch` (preferred), `srun`, or `salloc` + `srun`.
3. **Always request resources explicitly**, and as little as the job actually needs, because the cluster is shared.
4. **Always set `--time`.** If omitted, the job defaults to 4 hours. There is no maximum.
5. **Request GPUs with `--gres`.** Jobs without `--gres` get no GPU.
6. **Compute nodes cannot be reached by direct SSH.** Reach them only through Slurm, port forwarding, or the VPN (see section 6).
7. **Avoid many small files on `/home`.** Use Singularity `.sif` images for Python environments (see section 5).

---

## 1. Architecture Overview

```
Internet
   |
 [UFV firewall]
   |
slurm.soc.ufv.ca  (VM, room D240)
   - AD login / management / staging
   - Slurm controller
   - BeeGFS client (/home mount)
   |
   |  10 Gbps link
   v
Room K165 (physical rack)
   +------------------------------+----------------------------+
   | Slurm cluster (5 nodes)      | BeeGFS (28 TB parallel FS) |
   | node1 ... node5 (slurmd)     | Storage 1..5, RAID 5 each  |
   +------------------------------+----------------------------+
   (Slurm and BeeGFS run on the SAME 5 physical machines)

UFV Active Directory (AD)
   - Controls who may log in (AD group membership)
   - Synchronizes user IDs to the cluster
```

### Components

| Component | Location | Role |
|---|---|---|
| **Login / staging / controller** | VM in room **D240**, hostname `slurm.soc.ufv.ca` | AD login, management, file staging, runs the **Slurm controller**, mounts BeeGFS as a client at `/home` |
| **Slurm cluster** | Physical rack in room **K165** | 5 compute nodes (`node1` to `node5`) running `slurmd` |
| **BeeGFS** | Same rack in **K165**, same 5 machines | 28 TB parallel file system, mounted as `/home` |
| **UFV AD** | University directory | Authentication; access controlled by AD group membership; user IDs synchronized to the cluster |
| **Link** | Between D240 VM and K165 | 10 Gbps |

### Network and security

- The Slurm nodes are **entirely behind the UFV firewall** on a **separate private IP network**.
- Only the staging server `slurm.soc.ufv.ca` is the entry point from the Internet.
- Access is **controlled through AD group membership**. The user must have an AD account in the authorized group.

---

## 2. Compute Hardware

There is a single partition called **`main`** containing all five nodes. Resources are **shared** between users.

| Node | GPUs | GPU model | CPUs | RAM (diagram) | Slurm memory (MB) | GRES string |
|---|---|---|---|---|---|---|
| node1 | 1 | NVIDIA A30 | 32 | 64 GB | 63730 | `gpu:nvidia_a30:1`, `mps:nvidia_a30:100` |
| node2 | 3 | NVIDIA A30 | 64 | 96 GB | 95565 | `gpu:nvidia_a30:3`, `mps:nvidia_a30:300` |
| node3 | 3 | Quadro P5000 | 24 | 64 GB | 63730 | `gpu:p5000:3`, `mps:p5000:300` |
| node4 | 3 | Quadro P5000 | 24 | 64 GB | 63730 | `gpu:p5000:3`, `mps:p5000:300` |
| node5 | 4 | Quadro P5000 | 24 | 64 GB | 63730 | `gpu:p5000:4`, `mps:p5000:400` |

**Totals:** 14 GPUs (4 x A30 on node1 and node2, 10 x P5000 on node3 to node5), 168 CPUs.

Notes:
- The GPU model names visible in `sinfo` are `nvidia_a30` and `p5000`. Use these exact strings in `--gres`. The "P5000" being a Quadro P5000 is an inference from the name.
- GPUs on node2 to node5 show `(S:0-1)`, meaning they are spread across two CPU sockets.
- The node5 line in the source is truncated, but its GRES is clearly 4 GPUs and `mps:400`.
- The AI should pick a GPU type deliberately: the A30 is the newer and stronger card. The P5000 nodes offer more GPUs per node.

### Slurm configuration values (from `scontrol show conf`)

| Setting | Value | Meaning |
|---|---|---|
| `DefMemPerNode` | 15932 | Default memory is about 16 GB per node if `--mem` is not given |
| `MaxMemPerNode` | UNLIMITED | You may request up to the whole node's RAM |
| `DefaultTime` | 04:00:00 | Default job time limit is 4 hours |
| `MaxTime` | INFINITE | No maximum, but be considerate |
| `GresTypes` | gpu,mps | Two generic resource types: full GPUs and MPS fractions |

---

## 3. Storage: BeeGFS on `/home`

- **Capacity:** 28 TB, a parallel file system designed for HPC, AI/ML, and media workloads.
- **Mount point:** `/home`, identical on every node, so **stage once and use everywhere**.
- **Layout:** Files are striped across 5 storage targets (one per node), each backed by **RAID 5**.
- **Network:** Each storage node has 2 x 10 Gbps fiber links to a Cisco **C3850** switch. This could be upgraded to 2 x 25 Gbps with an RDMA switch.
- **Measured performance:** up to ~730 MB/s write and ~1.1 GB/s read. For a small number of large files this is about 2x faster than a RAID 0 SSD mirror on write.

### Pros
- Same file tree on all nodes automatically.
- Very fast for a small number of large files.
- Large combined space and reliable RAID 5 storage.

### Cons and what they mean for the AI
| Limitation | What to do |
|---|---|
| Only 5 stripes, so **many small files are slow** (e.g. Python environments with hundreds of module files) | Package environments as a **Singularity SIF** image (one large file) and run the job inside it. Avoid huge `venv` or `conda` trees on `/home` when possible. |
| Current network uses CPU for processing, which reduces CPU available to jobs | Be conservative with CPU requests. This is a hardware limitation. |
| BeeGFS runs on the **same nodes as Slurm**, which further reduces available resources | Expect shared load. Avoid wasteful I/O. |
| Staging server has only **1 x 10 Gbps** to storage and is a VM | File access from the login node is **slower** than from compute nodes. Do not do heavy I/O there. Move large data processing into jobs. |

---

## 4. Connecting and Submitting Jobs

### 4.1 Connect

```bash
ssh <ad_username>@slurm.soc.ufv.ca
```

- Credentials are the user's UFV AD credentials, and the account must be in the authorized AD group.
- This lands on the **staging / entry-point / management** host. From here you may run these Slurm commands:
  `sinfo`, `scontrol`, `squeue`, `salloc`, `srun`, `sbatch`, and others.
- Staging files (uploading code and data into `/home/<user>/`) is allowed on this host. Keep it light.

### 4.2 Inspect the cluster (safe on the login node)

```bash
sinfo -o "%10N %4c %6m %70G"      # nodes, CPUs, memory, GRES (the source example)
sinfo                             # partition and state overview  (general Slurm practice)
squeue -u $USER                   # your jobs                     (general Slurm practice)
scontrol show node node2          # detail for one node           (general Slurm practice)
```

Expected `sinfo` output:

```
NODELIST   CPUS MEMORY GRES
node1      32   63730  gpu:nvidia_a30:1,mps:nvidia_a30:100
node2      64   95565  gpu:nvidia_a30:3(S:0-1),mps:nvidia_a30:300(S:0-1)
node3      24   63730  gpu:p5000:3(S:0-1),mps:p5000:300(S:0-1)
node4      24   63730  gpu:p5000:3(S:0-1),mps:p5000:300(S:0-1)
node5      24   63730  gpu:p5000:4(S:0-1),mps:p5000:400(S:0-1)
```

### 4.3 Resource request options

| Need | Option | Example |
|---|---|---|
| Time limit | `--time=D-HH:MM:SS` | `--time=1-12:00:00` (1 day 12 hours) |
| Memory per node | `--mem=<MB>` | `--mem=25000` |
| Number of tasks | `-n` / `--ntasks` | `-n6` |
| Tasks per node | `--ntasks-per-node` | `--ntasks-per-node=3` |
| CPUs per task | `--cpus-per-task` | `--cpus-per-task=8` (general Slurm practice) |
| Full GPUs | `--gres=gpu:N` | `--gres=gpu:3` |
| Specific GPU model | `--gres=gpu:<type>:N` | `--gres=gpu:nvidia_a30:1` or `--gres=gpu:p5000:2` |
| Fraction of a GPU (MPS) | `--gres=mps:<percent>` | `--gres=mps:50` is half of one GPU; **100 = one full GPU** |

Important details:
- **Memory default is only ~16 GB.** Ask for more with `--mem` if needed. There is no upper cap except the node's physical RAM (63730 MB on node1, node3, node4 and node5; 95565 MB on node2).
- **No `--gres` means no GPU.**
- Use **MPS** for small jobs that do not need a whole GPU, so others can share.
- Do not request more than a node has (see the hardware table). For instance, at most 3 A30s on one node, and only 1 A30 on node1.

### 4.4 Batch job (preferred, non-interactive)

Save as `job.sh` in `/home/<user>/...` and submit with `sbatch job.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=my_gpu_job
#SBATCH --partition=main
#SBATCH --time=0-04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32000
#SBATCH --gres=gpu:1
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# Everything below runs on a COMPUTE node, not the login node.
hostname
nvidia-smi

# Example: run inside a Singularity image (recommended for Python envs)
# singularity exec --nv /home/<user>/envs/myenv.sif python train.py
python train.py
```

(`--partition`, `--output`, and `--error` are general Slurm practice. `--nv` is the standard Singularity flag for NVIDIA GPU access.)

Submit and monitor:

```bash
sbatch job.sh            # returns "Submitted batch job <JOBID>"
squeue -u $USER          # check status
scancel <JOBID>          # cancel
tail -f my_gpu_job_<JOBID>.out
```

### 4.5 Interactive work

The source example:

```bash
salloc -n6 --ntasks-per-node=3 --mem=25000    # allocate 6 tasks, 3 per node, 25000 MB
srun /bin/hostname | sort                     # runs on the allocated compute nodes
```

Output showed 3 tasks on `node1` and 3 tasks on `node2`. This shows tasks spreading across nodes, and that `srun` executes on compute nodes.

> **Warning:** After `salloc`, your shell is still on the **login node**. Only commands launched with `srun` run on compute nodes. For an interactive shell on a compute node with a GPU, use:
> ```bash
> srun --gres=gpu:1 --mem=16000 --time=01:00:00 --pty bash     # (general Slurm practice)
> ```
> After this, confirm with `hostname` that the output is `nodeN...` and **not** the login host before running anything heavy.

`squeue` format used in the source, with its example output:

```
squeue -o"%.7i %.9P %.8j %.8u %.2t %.10m %.6D %.3C %.10R"
 JOBID PARTITION   NAME  USER ST MIN_MEMORY NODES CPU NODELIST(REASON)
   516      main interact user  R     25000M     2   8 node[1-2]
```

Key: `ST` is job state (`R` = running), `NODES` = number of nodes, `CPU` = CPUs allocated, and `NODELIST(REASON)` shows where it runs.

---

## 5. Python Environments and Small-File Performance

- Many small files on BeeGFS (typical of `conda` or `venv` with hundreds of modules) is the file system's weak spot.
- Recommended solution from the source: use **large file-system image files, i.e. Singularity SIF files**. One big file is fast on BeeGFS.
- Stage the `.sif` once into `/home/<user>/`, and every node sees it.

---

## 6. Reaching Services on Compute Nodes (Jupyter, TensorBoard, etc.)

Compute nodes have **no direct SSH access** from outside. If a job runs a web service (e.g. Jupyter Notebook) on a port, choose one of:

**Option A: SSH port forwarding through the staging host** (general SSH practice)
```bash
ssh -L 8888:node3:8888 <ad_username>@slurm.soc.ufv.ca
# then open http://localhost:8888 on your own machine
```
(Replace `node3` with the node where the job is running, found via `squeue`.)

**Option B: SoC VPN.** Connect to the **SoC VPN** (the same VPN used for the OpenStack servers) to reach the private network directly.

The Jupyter server must run **inside a Slurm job** (via `sbatch` or `srun`), not on the login node.

---

## 7. Decision Checklist for the AI Agent

Before running ANY command, ask:

1. **Is this a light management command?** (`ls`, `cat`, `sinfo`, `squeue`, `sbatch`, `scancel`, small file edits or copies.) If yes, it may run on the login node.
2. **Is this compute, training, inference, large data processing, compiling, or environment building?** If yes, it must be wrapped in `sbatch` or `srun`.
3. **Does it need a GPU?** If yes, include `--gres=gpu:N` (or `--gres=mps:P`).
4. **Have I set** `--time`, `--mem`, and CPU count?
5. **Am I asking for only what is needed?** (shared cluster)
6. **For an interactive shell, did I verify with `hostname` that I am on a compute node?**
7. **Does the environment consist of lots of tiny files?** Prefer a Singularity SIF.

### Standard workflow

```
1. ssh <user>@slurm.soc.ufv.ca
2. Stage code and data into /home/<user>/        (visible on all nodes automatically)
3. sinfo / squeue                                (check availability)
4. Write job.sh with #SBATCH resource lines and a --gres GPU request
5. sbatch job.sh
6. squeue -u $USER                               (monitor)
7. Read the .out / .err files; fetch results from /home/<user>/
8. scancel <JOBID> if needed
```

### Do NOT

- Do not run `python train.py`, `nvidia-smi`-based workloads, or similar compute directly after SSH login.
- Do not try to SSH directly to `node1` to `node5`.
- Do not leave `salloc` allocations idle, since they block shared resources.
- Do not request all of the memory or GPUs "just in case".
- Do not omit `--time` on long jobs (the 4 hour default will kill them).

---

## 8. Quick Reference

| Item | Value |
|---|---|
| Entry host | `slurm.soc.ufv.ca` |
| Auth | UFV AD credentials and group membership |
| Partition | `main` |
| Nodes | node1 to node5 |
| GPUs | 4 x NVIDIA A30 (node1 has 1, node2 has 3), 10 x P5000 (node3 has 3, node4 has 3, node5 has 4) |
| GPU request | `--gres=gpu:N`, `--gres=gpu:nvidia_a30:N`, `--gres=gpu:p5000:N`, `--gres=mps:<percent>` |
| Shared storage | `/home` (BeeGFS, 28 TB, RAID 5) |
| Default time | 4 hours (`--time` to change, no max) |
| Default memory | ~16 GB per node (`--mem` to change, no cap) |
| Services access | SSH port forwarding via staging host, or SoC VPN |
| Small-file workaround | Singularity SIF images |

### Minor inconsistencies in the source (for awareness)
- The login host is written `slurm.soc.ufv.ca`, but the node hostnames in the example output appear as `nodeN.slurm.sc.ufv.ca`. Inside Slurm, use short names (`node1`, etc.).
- The diagram lists RAM as 64 GB and 96 GB, while Slurm reports 63730 MB and 95565 MB. This is the usable amount, so request at most the Slurm figure.
