$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
  & 'D:\latex\texlive\2025\bin\windows\latexmk.exe' -xelatex -interaction=nonstopmode -file-line-error -outdir=build main.tex
  Copy-Item -LiteralPath (Join-Path $projectRoot 'build\main.pdf') -Destination (Join-Path $projectRoot 'output\pdf\thesis_typeset.pdf') -Force
}
finally {
  Pop-Location
}
