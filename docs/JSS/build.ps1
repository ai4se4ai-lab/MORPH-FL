$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw "First LaTeX pass failed" }
    & bibtex main
    if ($LASTEXITCODE -ne 0) { throw "BibTeX failed" }
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw "Second LaTeX pass failed" }
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw "Final LaTeX pass failed" }
} finally { Pop-Location }

