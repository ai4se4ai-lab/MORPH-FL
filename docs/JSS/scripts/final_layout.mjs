import fs from 'node:fs';
const p='docs/JSS/main.tex';let t=fs.readFileSync(p,'utf8');
const a=t.indexOf('\\subsection{Models in Fault Localization and at Runtime}');
const b=t.indexOf('\\begin{table*}',a);
if(a<0||b<0)throw Error('related boundary');
const shorter=String.raw`\subsection{Models in Fault Localization and at Runtime}\label{sec:related_mde}
MDE research has localized faults in Simulink models and model transformations~\citep{simfl2016,mtspectrum2018}. In those settings the model is the artifact being debugged. Here the models describe an investigator of ordinary Python code. The closer lineage is models@run.time, which keeps explicit models to monitor and adapt a running system~\citep{modelsruntime2009}, and the monitor--analyze--plan--execute loop of autonomic computing~\citep{mapek2003}. \tool{} applies that pattern to investigation state and context. Its lightweight dataclasses, explicit checks and source links provide operational traceability without a dedicated transformation language or formal proof. Their value as a representation is not isolated by the available comparisons.

`;
t=t.slice(0,a)+shorter+t.slice(b);
t=t.replace('\\subsection{Evidence and reproduction map}', '\\FloatBarrier\n\\subsection{Evidence and reproduction map}');
fs.writeFileSync(p,t);

