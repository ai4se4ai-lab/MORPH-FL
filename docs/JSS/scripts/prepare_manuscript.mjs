import fs from 'node:fs';
import path from 'node:path';
const here=path.resolve(import.meta.dirname,'..');
const source=fs.readFileSync(path.join(here,'../TSE/main.tex'),'utf8');
const part=(a,b)=>source.slice(source.indexOf(a),source.indexOf(b));
const preamble=String.raw`% JSS revision: all measured inference uses frozen v12.
\documentclass[a4paper,fleqn]{cas-sc}
\usepackage[T1]{fontenc}
\usepackage[authoryear,round]{natbib}
\usepackage{amsmath,amsfonts,amssymb,algorithm,algpseudocode,placeins,array,textcomp,url,graphicx}
\usepackage{tikz,pgfplots,listings,booktabs,xcolor,tcolorbox}
\pgfplotsset{compat=1.17}
\usetikzlibrary{positioning,arrows.meta,fit,backgrounds,shapes.multipart,calc}
\tcbuselibrary{listings,skins}
\newcommand{\tool}{MORPH-FL}
\newcommand{\code}[1]{\texttt{\detokenize{#1}}}
\newcommand{\stereo}[1]{{\fontsize{6}{7}\selectfont\guillemotleft#1\guillemotright}}
\newcommand{\authoraction}[1]{\textbf{[AUTHOR TO PROVIDE: #1]}}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,columns=fullflexible,frame=single,numbers=left,numberstyle=\tiny,xleftmargin=1em}
\lstdefinestyle{morph}{language=Python,basicstyle=\ttfamily\scriptsize,columns=fullflexible,keepspaces=true,keywordstyle=\color{blue!55!black}\bfseries,commentstyle=\color{black!55}\itshape,stringstyle=\color{orange!65!black},showstringspaces=false,numbers=none,frame=none,xleftmargin=0pt,aboveskip=0pt,belowskip=0pt}
\newtcolorbox{codebox}{enhanced,colback=black!5,colframe=black!22,boxrule=.4pt,arc=2mm,left=3mm,right=2mm,top=1.2mm,bottom=1.2mm}
\makeatletter\providecommand\ext@lstlisting{lol}\makeatother
\begin{document}
\let\WriteBookmarks\relax
\shorttitle{Investigation state and context policies for fault localization}
\shortauthors{Babaei}
\title[mode=title]{MORPH-FL: An Exploratory Study of Evidence and Context Policies in LLM Fault Localization}
\author[1]{Majid Babaei}
\cormark[1]
\ead{ai4se4ai@gmail.com}
\affiliation[1]{organization={AI4SE4AI Lab; [AUTHOR TO PROVIDE: verified institutional affiliation and postal address]}}
\cortext[1]{Corresponding author. Identity, affiliation and contact details require final confirmation.}
\begin{abstract}
Large language model (LLM) agents investigating bug reports accumulate source observations, candidate explanations and dialogue in the same context. We present MORPH-FL, a Python fault-localization framework that separates these in four linked runtime models, projects requests from explicit views, and can reset dialogue while preserving observations and selected hypotheses. We compare its full adaptive workflow, continuous context, fixed resets and an observation-only view. A frozen, incomplete Qwen2.5-Coder-7B snapshot covers 139 SWE-bench Lite and 219 Verified issues with three seeds; a separate completed pilot covers 50 issues with two models and one seed. Full-workflow file Top-1 is 42.93\% and 46.58\%, differing from continuous context by $-0.24$ and $-0.15$ percentage points. Observation-only reaches 50.36\% and 55.56\%. In the pilot, DeepSeek-Coder-6.7B ends with grounded hypotheses on 47/50 issues under observation-only versus 6--7/50 under the other views, although all reach 40\% file Top-1 through rankings that can fall back to retrieval. Observation-only also takes longer on completed pilot cases. These are exploratory configuration comparisons: targets are unreviewed patch-change proxies, primary cohorts are completion-selected, and a prompt-growth defect affects richer views. The evidence establishes neither an adaptive-reset benefit nor the cause of the observation-only advantage. It motivates measuring investigation output and retrieval fallback alongside ranking accuracy when engineering bounded-context localization agents.
\end{abstract}
\begin{keywords}
Fault localization \sep Large language models \sep Context management \sep Models at runtime \sep Empirical software engineering \sep Reproducibility
\end{keywords}
\maketitle
\raggedbottom
`;
const intro=String.raw`
\section{Introduction}\label{sec:intro}
A bug report describes a failure at the point where a user encounters it. The code responsible may lie elsewhere in a repository. A developer connects the symptom to candidate locations, proposes explanations and checks them against source or execution evidence. Large language model (LLM) agents automate parts of this investigation: AutoFL uses repository tools to explain localization predictions, SoapFL organizes comprehension, navigation and confirmation, and Agentless narrows candidates before repair~\cite{autofl2024,soapfl2025,agentless2025}. Their practical usefulness depends on what they establish within an inference and inspection budget.

Context management becomes an engineering concern as calls accumulate. Dialogue mixes observed source facts, proposed mechanisms and the reasoning connecting them. Retaining it preserves useful facts and earlier mistakes; resetting it removes both. Long-context and multi-turn studies show that additional context can be difficult to use reliably~\cite{lostmiddle2024,distract2023,multiturn2025}. Those findings motivate explicit state management but do not determine which localization state an agent should see.

We distinguish three lifetimes. An observation records a check on a fixed source revision. A hypothesis remains conjectural even when a static check supports one of its predictions. Dialogue is the working medium in which investigators propose and interpret them. Externalizing observations and hypotheses allows requests to expose different views of the same state. It also makes a limitation visible that ranking accuracy alone can conceal: a workflow that produces no usable hypotheses may still return a plausible retrieval ranking.

We present \tool{}, an implementation of this separation for Python repositories. Four linked runtime models describe reported behavior, source structure, competing hypotheses and evidence. Each request projects these models and adds bounded source excerpts. A stagnation monitor can clear role dialogues and prune hypotheses to a score-and-diversity portfolio while retaining every recorded observation and the cumulative budget. The design draws on models at runtime and hypothesis-driven debugging~\cite{modelsruntime2009,zeller2009}. External state is established practice; the contribution is a concrete retention specification and an inspectable implementation for comparing context policies, rather than an assertion that dataclasses alone improve localization.

The empirical findings qualify the original design. The full adaptive workflow demonstrates no accuracy or token advantage over continuous context. Its strongest observed comparator is a control that shows the report and accessible observations, with the common instructions and source excerpts, while omitting hypotheses and dialogue. This \emph{observation-only view} still uses hypotheses internally for grounding, assessment and ranking. It does not summarize observations with another LLM. Interpreting it as a preferable projection is post hoc and requires confirmation.

We ask four questions bounded by the available evidence:
\begin{itemize}
\item \textbf{RQ1 (Ranking):} What file- and function-ranking outcomes do the workflows produce in the frozen Qwen snapshot?
\item \textbf{RQ2 (Investigation behavior):} How often do resets occur, and what can the available contrasts establish about context and retention?
\item \textbf{RQ3 (Resources):} What completed-case token and elapsed-time tradeoffs accompany observed ranking outcomes?
\item \textbf{RQ4 (Second-model sensitivity):} How do rankings and final hypothesis availability differ in the completed two-model pilot?
\end{itemize}

The primary snapshot contains 139 Lite and 219 Verified complete-case issues with Qwen2.5-Coder-7B, averaged over three seeds. These overlapping cohorts were selected by completion, not random sampling. File Top-1 is 42.93\%/46.58\% for the full workflow and 50.36\%/55.56\% for observation-only. A separate complete pilot uses 50 issues, Qwen and DeepSeek-Coder-6.7B, and one seed. DeepSeek finishes with grounded hypotheses on only 6--7/50 issues under richer views but 47/50 under observation-only, although all four have 40\% file Top-1. Retrieval fallback can therefore hide failed investigations.

The observed advantage has important limits. Observation-only jointly removes several fields and dialogue and disables reset pruning. A demonstrated ambiguity-duplication defect also grows richer requests; observation-only omits that field. No corrected-runtime inference comparison is available. Adaptive resets average about 0.27 per primary run, so exposure to their effects is limited. These findings support neither a causal explanation for the winning configuration nor a benefit from adaptive resetting.

The contributions are:
\begin{itemize}
\item An executable investigation-state design separating observations, conjectures and dialogue, with source provenance, scoped assessments and an explicit observation-preservation obligation at reset.
\item An exploratory comparison of context configurations, restricted external adaptations and retrieval controls, with matched denominators, paired descriptive effects and a separately reported complete two-model pilot.
\item A diagnostic account of rare reset exposure, empty hypothesis pools, retrieval fallback and prompt-growth confounding that limits what localization scores establish.
\item A reproducible evidence map connecting manuscript results to frozen predictions, labels, model pins and analysis procedures.
\end{itemize}

Section~\ref{sec:background} defines the task and example; Section~\ref{sec:approach} presents the architecture. Sections~\ref{sec:study} and~\ref{sec:results} describe the study and findings. Sections~\ref{sec:discussion}--\ref{sec:related} discuss implications, validity and related work. Section~\ref{sec:conclusion} concludes; the appendix records implementation and reproduction details.
`;
let body=part('\\section{Background and Motivating Example}','\\section{Discussion}');
body=body.replace('\\begin{IEEEdescription}[\\IEEEsetlabelwidth{I4}]','\\begin{description}').replace('\\end{IEEEdescription}','\\end{description}');
const replace=(oldText,newText)=>{if(!body.includes(oldText)) console.warn('Unmatched:',oldText.slice(0,80));body=body.replace(oldText,newText);};
replace('Their status cannot be confused (invariant I1 below)','Their declared status is kept separate by controller operations (invariant I1 below)');
replace('so the only ways to shorten it are to truncate it or to have an LLM summarize it, and either can drop a fact or turn a conjecture into one','and shortening it by truncation or summarization can drop facts or blur their status');
replace('Observations are identified by their content and are never modified or deleted','Observations are identified by their content; controller operations do not modify or delete them');
replace('No operation modifies or deletes an observation, and the evidence model rejects a changed observation under an existing identifier.','Controller operations neither modify nor delete observations. Insertion checks reject changed records under an existing identifier except for the originating probe identifier; nested result dictionaries are not deeply immutable (Appendix~\\ref{app:realization}).');
replace('The observations themselves remain visible in every request (I4).','Observations remain recorded (I4) and available to the next projection; I4 does not guarantee that every record fits the backend context window.');
replace('A reset is worth its cost only when the dialogue has stopped helping.','The reset policy is designed to act when observable progress stalls; whether this intervention is worth its cost is an empirical question.');
replace('\\textbf{RQ1 (Effectiveness).} How accurately does \\tool{} rank files and functions compared with other localization workflows? This tells whether the model-driven design costs or gains localization accuracy.','\\textbf{RQ1 (Ranking).} What file- and function-ranking outcomes do the workflows produce in the frozen Qwen snapshot?');
replace('\\textbf{RQ2 (Components).} How do model-based context construction, reset timing, and hypothesis retention affect the investigation? This isolates which retention decision drives the results.','\\textbf{RQ2 (Investigation behavior).} How often do resets occur, and what can the available workflow contrasts establish about context and retention?');
replace('\\textbf{RQ3 (Cost).} Which accuracy--cost tradeoffs do these policies produce? Equal token ceilings need not mean equal use.','\\textbf{RQ3 (Resources).} What completed-case token and elapsed-time tradeoffs accompany the observed outcomes?');
replace('\\textbf{RQ4 (Generalization).} Does the pattern hold for a second LLM? A retention policy that helps one LLM may hinder another.','\\textbf{RQ4 (Second-model sensitivity).} How do rankings and final hypothesis availability differ in the completed two-model pilot?');
replace('Each LLM workflow is run with five pinned open LLM families and three seeds, which gives','The larger planned study includes five pinned LLM families and three seeds, which would give');
replace('Every LLM run has the same limits:','The scored primary and pilot runs have these limits:');
replace('The eight component ablations of Table~\\ref{tab:variants}, a budget study, a misleading-clue study, and a reset-window study use','The larger planned protocol assigns the eight component ablations of Table~\\ref{tab:variants}, a budget study, a misleading-clue study, and a reset-window study to');
replace('The budget study reruns','The planned budget study would rerun');
replace('The reset-window study varies','The planned reset-window study would vary');
replace('All other comparisons are descriptive. In the single-seed pilot, proportions such as productive runs come with Wilson 95\\% score intervals~\\cite{wilson1927}, and paired file Top-1 outcomes are summarized by their discordant issues, the issues that one workflow localizes at rank one and the other does not.','All reported comparisons here are exploratory and descriptive. In the single-seed pilot, paired file Top-1 outcomes are summarized by discordant issues and the saved 2,000-draw repository-cluster bootstrap over 12 repositories. Final-pool availability is an operational process metric, not causal correctness; we do not use marginal interval nonoverlap as a paired test.');
replace('so its file accuracy says nothing about the investigation.','so a file hit does not establish that hypothesis-based investigation succeeded.');
replace('A difference between \\tool{} and these two configurations therefore comes from the content of the request and, for the observation-only view, from the absence of resets, which also means that its final ranking draws on an unpruned hypothesis pool; it does not come from how evidence is processed.','These are bundled workflow contrasts: prompt fields, serialization verbosity and dialogue differ, and observation-only also omits resets and pruning, changing the final hypothesis pool. Internal evidence processing is shared, but an accuracy difference cannot be attributed to one omitted field. All four workflows retain an evidence store; none isolates the benefit of observation retention against deleting it.');
replace('and all four intervals lie within about $\\pm1.5$\\,pp of zero.','and all four intervals lie within about $\\pm1.5$\\,pp of zero. These are small observed differences, not evidence of equivalence or noninferiority.');
replace('It is level with continuous context and fixed-interval resets:','Its observed rates are close to continuous context and fixed-interval resets:');
replace('The observation-only view, which shows the LLM only the report and the recorded observations, does clearly better.','The observation-only configuration has higher observed Top-1.');
replace('Against BM25, \\tool{} is clearly ahead on Verified','Against BM25, \\tool{} has a higher observed rate on Verified');
const crossStart=body.indexOf(' For context, CoSIL reports');
const crossEnd=body.indexOf('\n\n\\emph{Where the workflows differ.}',crossStart);
if(crossStart>=0&&crossEnd>crossStart) body=body.slice(0,crossStart)+body.slice(crossEnd);
replace('It matches continuous context and fixed-interval resets, but does not outperform the strongest comparator:','The observed full-minus-continuous differences are $-0.24$/$-0.15$\\,pp; no equivalence or superiority is established. Against the strongest observed comparator,');
replace('\\textbf{RQ2 asks how model-based context construction, reset timing, and hypothesis retention affect the investigation.}','\\textbf{RQ2 asks how often resets occur and what the contrasts can establish about context and retention.}');
replace('The small, uncertain difference from continuous context is therefore expected.','Most runs therefore offer no direct adaptive-reset exposure.');
replace('yet its file Top-1, Top-5, and Top-10 are identical to those of continuous context on both splits.','yet its aggregate file Top-1, Top-5, and Top-10 are identical to those of continuous context on both splits. Equal aggregates need not mean identical per-issue rankings.');
replace('Its advantage therefore comes mainly from what the LLM is shown: evidence is processed the same way, and the resets it omits are rare in \\tool{}\'s runs. This single contrast cannot tell which omission matters.','Its observed advantage belongs to this configuration bundle. Shared evidence processing does not identify a causal prompt effect, because prompt content, verbosity, dialogue and retention all differ, and the full view contains a known ambiguity-growth defect. This contrast cannot establish which omission matters.');
replace('resetting about once per run on average (fixed interval) leaves the file ranking unchanged.','fixed reset and continuous context have the same aggregate file metrics; this does not prove unchanged issue-level rankings.');
replace('Showing the LLM only the recorded observations, without hypotheses or dialogue, improves file Top-1 by 7--9\\,pp over \\tool{}\'s full projection.','The observation-only bundle has file Top-1 7--9\\,pp higher in the frozen comparison.');
replace('\\textbf{RQ4 asks whether the pattern holds for a second LLM.}','\\textbf{RQ4 asks about rankings and final hypothesis availability with a second LLM.}');
replace('With so few discordant issues this difference is not statistically reliable (exact two-sided McNemar $p=0.22$; repository-cluster bootstrap interval for the difference, 2,000 replicates over 12 repositories, $[-16,0]$\\,pp),','The descriptive full-minus-observation-only repository-cluster interval is $[-16,0]$\\,pp (2,000 draws over 12 repositories),');
replace('The two Wilson intervals, [6\\%, 24\\%] and [84\\%, 98\\%], are far apart.','The final-pool counts are process outcomes, not evidence that the hypotheses are causally correct.');
replace('\\emph{Why the views differ.}','\\emph{Output diagnostics and alternative explanations.}');
replace('so the difference lies in what the request asks the LLM to read, not in what it must write.','but common output requirements do not isolate the effects of input length, content, ambiguity duplication or pool retention.');
replace('With a second 7B-scale LLM, the advantage of the observation-only view appears as robustness rather than as file accuracy:','With the second 7B-scale LLM, observation-only has higher observed final-pool availability without a file-Top-1 gain:');
replace('Qwen2.5-Coder-7B shows the same 8\\,pp file Top-1 direction as in the primary snapshot. No context policy that carries dialogue outperforms another with either LLM.','Qwen shows the same direction as the primary snapshot, with overlapping evidence. These observations do not establish generalization, equivalence or a mechanism for the configuration difference.');
replace('on par with continuous context and fixed-interval resets.','with full-minus-continuous differences of $-0.24$/$-0.15$\\,pp, without an equivalence conclusion.');
replace('keeps most investigations productive (47 of 50 runs, against 6--7 of 50).','yields a nonempty final hypothesis pool on 47 of 50 runs, against 6--7 of 50; this is an operational output measure.');
body=body.replace('A run is productive when it ends with at least one grounded hypothesis; brackets give Wilson 95\\% intervals.','Nonempty final-pool counts measure operational output availability, not causal correctness.');
body=body.replace(/ \[(?:90,100|93,100|6,24|7,26|84,98)\]\\%/g,'');
body=body.replace('Productive & Resets','Nonempty & Resets').replace('runs & per run','final pool & per run');
const earlyDefect=String.raw`
\paragraph{Frozen implementation boundary.}
All scored inference uses frozen v12, not the later local ambiguity correction. In that runtime, repeated unresolved ambiguities can be appended to the behavior model and shown again, growing the richer requests. Observation-only omits that field. The defect is demonstrated on a trace; its prevalence and accuracy effect are not quantified. A regression-tested correction has no reported inference rerun. Consequently, the headline comparison includes a correctable implementation confound as well as bundled context changes.
`;
body=body.replace('\\subsection{Compared Configurations}',earlyDefect+'\n\\subsection{Compared Configurations}');
const discussion=String.raw`
\section{Discussion}\label{sec:discussion}
\subsection{What the evidence changes about the design}
The architecture combines persistent observations, competing hypotheses and adaptive dialogue resets. These have different evidence status. Record retention and provenance are inspectable implementation properties. Their accuracy benefit is not isolated, because every principal workflow retains evidence. Adaptive-reset benefit is also unestablished: resets are rare and matched trajectory studies are unavailable. Thus the contribution is an executable state-lifetime design and exploratory evidence, rather than a validated superior reset policy.

Observation-only was a planned control; interpreting it as preferable is post hoc. Several explanations fit its observed outcomes. Earlier hypotheses could anchor later proposals. Compact serialization and omitted fields could reduce prompt burden. Accepted outputs could contain more source-valid candidates. Omission of the defective behavior field could avoid artificial request growth. Its unpruned pool could also affect ranking. The available data do not separate these explanations. In particular, most full-view DeepSeek responses did not fail the output format: many accepted responses simply yielded few grounded hypotheses. A corrected-runtime comparison is necessary but will not alone isolate the other factors.

The model architecture makes interventions explicit. Omitting hypotheses from requests while retaining them internally is different from pruning them. Clearing dialogue is different from deleting observations. This precision is useful for designing the next study, but does not empirically validate the representation itself. No evidence-deletion control or independently implemented model-free agent is available here.

\subsection{Implications for engineering localization tools}
An intended user receives an unverified ranked shortlist with check provenance. Static support means the code exists or has a given structure; it does not show that it caused the reported execution. The results suggest measurement priorities rather than universal deployment advice:
\begin{itemize}
\item \emph{Expose retrieval fallback.} Report whether a ranking derives from live hypotheses or retrieval. DeepSeek's 40\% file Top-1 otherwise conceals mostly empty full-view investigations. Pair file hits with exact-function scores and final-pool availability.
\item \emph{Version prompt views as interfaces.} Record serialized fields, ambiguity growth, truncation, source visibility and output validity. Schema-valid output may still contain no source-valid candidate; invalid-response counts alone are insufficient.
\item \emph{Measure actual resources.} Common token ceilings do not equalize use, latency or output-list coverage. Observation-only takes longer on completed pilot cases (Table~\ref{tab:pilot-cost}); no developer-time or total-cost benefit is established.
\item \emph{Audit reset opportunities.} Count eligible plateaus and examine post-reset observations, retained/refuted hypotheses and ranking changes. A reset count alone is not evidence of recovery from a wrong explanation.
\end{itemize}

\begin{table}[t]
\caption{Completed-case pilot resources, 50 issues per row and seed 1. Tokens include actual input and output; seconds and tokens exclude interrupted/retried attempts.}\label{tab:pilot-cost}
\centering\small
\begin{tabular}{@{}llrr@{}}\toprule
LLM & Workflow & Mean tokens & Mean seconds\\\midrule
Qwen & Full adaptive & 28,257 & 93.6\\
 & Continuous & 27,574 & 89.5\\
 & Fixed reset & 29,114 & 94.7\\
 & Observation-only & 29,325 & 140.3\\\midrule
DeepSeek & Full adaptive & 29,197 & 55.0\\
 & Continuous & 27,912 & 48.3\\
 & Fixed reset & 29,553 & 53.8\\
 & Observation-only & 29,920 & 111.5\\\bottomrule
\end{tabular}
\end{table}

Real repositories provide scale and context, but no industrial deployment, developer study, causal diagnosis or repair-success experiment is reported. A larger LLM may use rich prompts differently. The observed small-model result is a reason to evaluate the local workflow, not a general instruction to discard reasoning.

\subsection{Next experiments}
First quantify duplicated ambiguities and audit the generation-to-grounding funnel on saved development traces. Distinguish malformed responses, valid-empty lists, invalid locations, pruning and budget termination. Validate separately versioned corrected views under matched serialization and budget. Then freeze the prompt/retention factors, primary estimand, feasible test family and clustering procedure before inspecting independent outcomes. A favorable rerun on these same pilot issues is development evidence.

Repeated-reset recovery needs sufficient intervention opportunities and an explicitly wrong initial lead, not merely more ordinary runs. Complete upstream localizers and an independent unstructured tool agent would strengthen comparison. Human label adjudication, untouched/decontaminated subjects, all-attempt resource accounting and developer/repair outcomes are separate extensions required for the corresponding stronger claims. Expanding the unchanged study alone would not resolve the known confounding.
`;
let threats=part('\\section{Threats to Validity}','\\section{Related Work}');
threats=threats.replace('The identical file rankings of continuous context and fixed-interval reset','The identical aggregate file metrics of continuous context and fixed-interval reset');
threats+=String.raw`
\paragraph{Validation history.}
On 28 October, synthetic regression checks exposed identity-validation gaps in model revision, sharding and protocol checks. The local checker was hardened; read-only metadata inspection found saved configurations consistent with frozen settings. This was not a fresh content-level validation of all predictions under the hardened checker. The release should rerun that complete validation while preserving original receipts. Operational record preservation is not deep immutability or a proof that all useful semantic information survives a reset.
`;
let related=part('\\section{Related Work}','\\section{Conclusion}');
related=related.replace('What it adds is a policy for keeping such a cycle productive across LLM context resets.','It adds an explicit retention/reset policy to that cycle; its productivity benefit remains unestablished.');
related=related.replace('and our results suggest that for small LLMs the observations alone carry much of the useful signal.','but the bundled contrast and known defect prevent attributing the observed advantage to that inversion.');
related+=String.raw`
\subsection{Recent JSS studies of LLM localization}
Xu et al.\ study the potential and limitations of LLM localization in novice programs~\cite{xu2026novice}. SHARE-RAG explicitly combines structure-aware and hypothesis-guided retrieval for novice-program fault localization~\cite{wu2026sharerag}. These are relevant connections to prompt sensitivity and explicit hypotheses, but their task differs from report-based localization in a pre-fix repository. Our question concerns within-investigation state lifetimes and prompt views, not the value of hypotheses in every localization setting. The present observation-only result therefore does not imply that hypothesis guidance generally harms localization. These comparisons use publisher abstracts and verified metadata; a full-text author check remains part of final literature verification.
`;
const conclusion=String.raw`
\section{Conclusion}\label{sec:conclusion}
\tool{} separates a localization investigation into runtime models of behavior, structure, hypotheses and evidence, allowing context to be rebuilt without relying on dialogue as its sole memory. Its implemented reset retains observations and a selected hypothesis portfolio under a cumulative budget. These properties specify what the system keeps; they do not establish a benefit from keeping or resetting it.

In the frozen Qwen snapshot the full workflow obtains file Top-1 of 42.93\% and 46.58\%, with small observed differences from continuous and fixed-reset workflows. Observation-only reaches 50.36\% and 55.56\%. In the complete pilot it yields final hypotheses on 47/50 DeepSeek issues versus 6--7/50 under richer views, while all four retain 40\% file Top-1 and observation-only takes longer. File accuracy can therefore conceal failed investigation behind retrieval fallback. Bundled prompt changes, a known prompt-growth defect, completion-selected cohorts and source-only patch proxies prevent stronger causal or deployment claims. Corrected, factor-isolating comparisons on independent subjects are needed before recommending a context policy.
`;
let appendix=part('\\section{Implementation Details}','\\end{document}');
const backmatter=String.raw`
\subsection{Evidence and reproduction map}\label{app:reproduction}
The immutable snapshot is in \code{docs/evaluation_assets/snapshot/}. Its labels, membership, predictions, tracker and manifest are hashed in \code{snapshot.json}. \code{docs/evaluation_assets/cohorts.json}, \code{summary.csv} and \code{paired_effects.csv} contain matched cohorts and scored aggregates. The root-relative script \code{docs/evaluation_assets/build_report.py} rebuilds snapshot metrics and figures with \code{src} on Python's module path, NumPy and Matplotlib installed. The JSS Node audit independently recomputes point estimates from frozen rankings and labels without model inference.

Pilot aggregates, scores, coverage and archived verification are in \code{experiments/pilot/results/analysis/}; selection/provenance are in \code{experiments/pilot/results/pilot.json}. Large raw prediction/audit archives were retained on the original infrastructure and must be deposited or durably linked in the release. \code{experiments/full/pins.json} records model/dataset revisions. Qwen and DeepSeek checkpoint commits are respectively \code{c03e6d358207e414f1eca0bb1891e29f1db0e242} and \code{e5d64addd26a6a1db0f9b863abf6ee3141936807}. Dataset commits are \code{6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2} (Lite) and \code{c104f840cc67f8b6eec6f759ebc8b2693d585d4a} (Verified).

Dependency ranges in \code{pyproject.toml} are not an exact evaluated environment. \authoraction{archive the frozen source/protocol digests, exact Python, PyTorch, Transformers, tokenizer, CUDA/driver and OS versions, dependency lock and clean-environment reproduction instructions.}

\section*{Data Availability}
The working repository identifies \url{https://github.com/ai4se4ai-lab/MORPH-FL} as the project location. Public accessibility and completeness of the evaluated-source/result archive have not been independently established in this revision. Local evidence and analysis are mapped in Appendix~\ref{app:reproduction}. \authoraction{provide the accessible replication-package URL and archival DOI, immutable evaluated code/protocol version, raw predictions and permissible audit traces, label-generation inputs, dependency lock and licenses.} No completed open archival deposit is claimed.

\section*{CRediT authorship contribution statement}
\authoraction{confirm the full author list and each author's applicable CRediT roles.}

\section*{Declaration of competing interests}
\authoraction{provide the verified competing-interest declaration or confirm no competing interests.}

\section*{Funding}
\authoraction{provide funder names, grant numbers and sponsor roles, or confirm no specific funding.}

\section*{Declaration of generative AI and AI-assisted technologies in the writing process}
OpenAI Codex assisted repository/evidence inspection, literature discovery, drafting, LaTeX preparation and simulated critical-review passes. The prior manuscript also records assistance from Claude (Anthropic) with restructuring, writing and result integration. The three review passes for this revision were AI-generated assessments requested by the author, not human or journal peer review. \authoraction{confirm the complete tool/version history, review and verify the manuscript, references and analyses, and finalize this declaration accepting full responsibility for submitted content.}

\bibliographystyle{cas-model2-names}
\bibliography{references}
\end{document}
`;
let text=preamble+intro+body+discussion+threats+related+conclusion+'\n\\appendix\n'+appendix+backmatter;
// Scale the two architecture diagrams from the IEEE full-width measure.
text=text.replace(/\\begin\{figure\*\}\[t\]\s*\\centering\s*\\begin\{tikzpicture\}/g,'\\begin{figure*}[t]\n\\centering\n\\resizebox{.98\\textwidth}{!}{%\n\\begin{tikzpicture}');
text=text.replace(/\\end\{tikzpicture\}\s*\\caption\{(Overview of|The investigation metamodel)/g,'\\end{tikzpicture}}\n\\caption{$1');
text=text.replaceAll('two-LLM pilot (Qwen2.5-Coder-7B and DeepSeek-Coder-6.7B, one seed)','two-LLM pilot (Qwen2.5-Coder-7B and DeepSeek-Coder-6.7B, one seed)');
fs.writeFileSync(path.join(here,'main.tex'),text);
fs.copyFileSync(path.join(here,'../TSE/references.bib'),path.join(here,'references.bib'));
console.log('Wrote main.tex:',text.length,'characters');

