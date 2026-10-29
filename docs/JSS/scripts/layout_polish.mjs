import fs from 'node:fs';
const p='docs/JSS/main.tex';let t=fs.readFileSync(p,'utf8');
t=t.replace('\\usepackage{tikz,pgfplots,listings,booktabs,xcolor,tcolorbox}','\\usepackage{tikz,pgfplots,listings,booktabs,xcolor,tcolorbox,seqsplit}\n\\hypersetup{hypertexnames=false,hidelinks}');
t=t.replace('\\newcommand{\\authoraction}', '\\newcommand{\\artifactpath}[1]{\\nolinkurl{#1}}\n\\newcommand{\\sourceid}[1]{\\texttt{\\seqsplit{#1}}}\n\\newcommand{\\authoraction}');
t=t.replaceAll('\\cite{','\\citep{');
const start=t.indexOf('\\subsection{Evidence and reproduction map}');
t=t.slice(0,start)+t.slice(start).replace(/\\code\{([a-f0-9]{40})\}/g,'\\sourceid{$1}').replace(/\\code\{((?:docs|experiments)\/[^}]+)\}/g,'\\artifactpath{$1}');
t=t.replace('rebuilds snapshot metrics and figures with','rebuilds snapshot metrics and figures after restoration of the truncated export, with');
fs.writeFileSync(p,t);
console.log('Applied citation and appendix line-breaking fixes.');

