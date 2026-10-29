import fs from 'node:fs';
const p='docs/JSS/main.tex';let t=fs.readFileSync(p,'utf8');
function section(a,b,text){const i=t.indexOf(a),j=t.indexOf(b,i+1);if(i<0||j<0)throw Error(a);t=t.slice(0,i)+text+'\n'+t.slice(j);}
section('\\begin{abstract}','\\begin{keywords}','\\input{sections/abstract.tex}');
section('We ask four questions bounded by the available evidence:','\\section{Background and Motivating Example}','\\input{sections/intro-evaluation.tex}');
section('\\section{Evaluation}\\label{sec:study}','\\section{Related Work}','\\input{sections/study.tex}\n\\input{sections/results.tex}\n\\input{sections/discussion.tex}\n\\input{sections/threats.tex}');
section('\\section{Conclusion}\\label{sec:conclusion}','\\appendix','\\input{sections/conclusion.tex}');
section('\\subsection{Configuration catalog}','\\subsection{Code correspondence and operational checks}','\\subsection{Configuration scope}\\label{app:configuration-catalog}\nTable~\\ref{tab:variants} defines all evaluated configurations. Additional implemented controls such as \\code{context_only}, \\code{single_hypothesis}, \\code{no_mde} and \\code{independent_agents} are outside the reported experiments; their presence in the library is not performance evidence.\n');
const a=t.indexOf('\\emph{Planned trajectory studies.}');if(a>=0){const b=t.indexOf('\\FloatBarrier',a);t=t.slice(0,a)+t.slice(b);}
section('\\subsection{Evidence and reproduction map}','\\section*{Data Availability}','\\input{sections/reproduction.tex}');
t=t.replace('The full adaptive workflow demonstrates no accuracy or token advantage over continuous context.','The full adaptive workflow demonstrates no file-Top-1 or token advantage over continuous context.');
t=t.replace('The thresholds are design parameters, not calibrated values; the planned reset-window study would vary the window size, and under the study budget the default thresholds rarely trigger a reset (Section~\\ref{sec:rq2}).','The thresholds are design parameters, not calibrated values. Exposure differs across models; Section~\\ref{sec:rq2} reports how often the default policy acts.');
t=t.replace('Section~\\ref{sec:rq1} reports how often the top file actually changes.','Section~\\ref{sec:rq1} reports changes in whether a patch target appears first, not necessarily the identity of the first-ranked file.');
t=t.replace('The primary evaluation uses source and AST probes only','The evaluation uses source and AST probes only');
fs.writeFileSync(p,t);console.log('Integrated completed-study sections.');

