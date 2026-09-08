from pathlib import Path
import re,json,hashlib

root=Path('D:/初稿/latex-paper')
out=Path('D:/初稿/修改/Table17_19表头候选_20260909')
out.mkdir(parents=True,exist_ok=True)
source17=(root/'tables/table_4_10.tex').read_text(encoding='utf-8')
source19=(root/'tables/table_4_12.tex').read_text(encoding='utf-8')
t17=source17.replace(r'Multi-scale\newline DSConv','DSConv')
assert t17!=source17
t19=source19.replace(r'\begin{tabularx}{\linewidth}{@{\extracolsep{\fill}}L{2.30}C{0.65}C{0.65}C{0.65}C{0.55}C{0.55}C{0.55}C{1.275}C{1.275}C{1.275}C{1.275}@{}}',r'\setlength{\tabcolsep}{2pt}'+'\n'+r'\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lcccccccccc@{}}')
assert t19!=source19
t19=t19.replace(r'\end{tabularx}',r'\end{tabular*}')
t19=t19.replace(r'@{\extracolsep{\fill}}lcccccccccc@{}',r'@{\extracolsep{\fill}}p{70pt}'+''.join(r'>{\centering\arraybackslash}p{'+str(w)+r'pt}' for w in [28,28,28,25,25,25,42,62,43,50])+r'@{}')
for a,b in [(r'\makecell{Training\\hyperparameters}','Training hyperparameters'),(r'\makecell{Model\\hyperparameters}','Model hyperparameters'),(r'\makecell{FLOPs\\(Million)}','FLOPs (M)'),(r'\makecell{Training\\time (s)}','Training time (s)'),(r'\makecell{Storage\\size (KB)}','Storage (KB)')]:
 assert a in t19
 t19=t19.replace(a,b)
for src,variant in [(source17,t17),(source19,t19)]:
 assert src.split(r'\midrule')[1].split(r'\bottomrule')[0]==variant.split(r'\midrule')[1].split(r'\bottomrule')[0]
(out/'table17_candidate.tex').write_text(t17,encoding='utf-8')
(out/'table19_candidate.tex').write_text(t19,encoding='utf-8')
content=r'''\documentclass[UTF8,11pt]{ctexart}
\input{preamble}
\begin{document}
\noindent\textbf{Table 17 与 Table 19：表头排版候选}\par
\noindent 正式稿尚未修改。沿用原字号与总宽度，保留全部数值和原有加粗。\par
\setcounter{table}{16}
'''+t17.replace(r'\begin{table}',r'\begin{table}[H]')+r'''
\vspace{7mm}
\setcounter{table}{18}
'''+t19.replace(r'\begin{table}',r'\begin{table}[H]')+r'''
\end{document}
'''
(out/'table_headers_preview.tex').write_text(content,encoding='utf-8')
(out/'source_hashes.json').write_text(json.dumps({str(root/'tables/table_4_10.tex'):hashlib.sha256((root/'tables/table_4_10.tex').read_bytes()).hexdigest(),str(root/'tables/table_4_12.tex'):hashlib.sha256((root/'tables/table_4_12.tex').read_bytes()).hexdigest()},indent=2),encoding='utf-8')
print('Prepared two table candidates; data bodies unchanged.')
