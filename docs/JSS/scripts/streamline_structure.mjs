import fs from 'node:fs';
const p='docs/JSS/main.tex';let t=fs.readFileSync(p,'utf8');
const implStart=t.indexOf('\\subsection{Implementation and Its Correspondence');
const implEnd=t.indexOf('\\section{Evaluation Results}',implStart);
let impl=t.slice(implStart,implEnd);
const inference=impl.match(/\\emph\{LLM inference\.\}[\s\S]*?(?=\n\n)/)[0];
const short=String.raw`\subsection{Implementation and inference settings}\label{sec:implementation}
All workflows use \code{LocalizationController.run} in the \code{morph_fl} Python package. A workflow is a configuration, not an independently implemented agent. Appendix~\ref{app:code-correspondence} maps the algorithm to source modules and records the integrity checks and executable example scripts. The shared implementation improves control of engineering differences but limits conclusions about an independently designed unstructured agent.

`+inference+'\n\n';
impl=impl.replace('\\subsection{Implementation and Its Correspondence to Algorithm~\\ref{alg:controller}}\\label{sec:implementation}','\\subsection{Code correspondence and operational checks}\\label{app:code-correspondence}');
impl=impl.replace(inference,'');
t=t.slice(0,implStart)+short+t.slice(implEnd);
const tableStart=t.lastIndexOf('\\begin{table}',t.indexOf('\\label{tab:variants}'));
const tableEnd=t.indexOf('\\end{table}',tableStart)+'\\end{table}'.length;
const catalog=t.slice(tableStart,tableEnd);
t=t.slice(0,tableStart)+t.slice(tableEnd);
t=t.replace('Table~\\ref{tab:variants} lists the configurations','The catalog in Appendix~\\ref{app:configuration-catalog} lists the configurations');
const insert=t.indexOf('\\subsection{Evidence and reproduction map}');
const extra='\\subsection{Configuration catalog}\\label{app:configuration-catalog}\nThe catalog distinguishes implemented primary comparisons from planned side-study configurations whose matched results are unavailable. It does not claim that the planned side studies were completed.\n\n'+catalog+'\n\n'+impl+'\n';
t=t.slice(0,insert)+extra+t.slice(insert);
t=t.replace('\\section{Conclusion}\\label{sec:conclusion}','\\FloatBarrier\n\\section{Conclusion}\\label{sec:conclusion}');
fs.writeFileSync(p,t);
console.log('Moved implementation mapping and unmeasured configuration catalog to appendix.');

