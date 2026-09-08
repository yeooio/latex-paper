from pathlib import Path
from datetime import datetime
import re, shutil, hashlib, json

root=Path('D:/初稿/latex-paper')
backup=Path('D:/初稿/修改')/('Table14_15_16精简应用_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
files=['tables/table_4_7.tex','tables/table_4_8.tex','tables/table_4_9.tex']
before={f:(root/f).read_text(encoding='utf-8') for f in files}
chapfile=root/'chapters/chapter04.tex'
chapter=chapfile.read_text(encoding='utf-8')
anchor='两项输入健康指标。'
sentence='迁移实验结果为三次独立运行的平均值。'
assert chapter.count(anchor)==1 and sentence not in chapter

def parse_old(text):
    rows=[]
    for line in text.splitlines():
        if re.search(r'&\s*(?:\$R\^2\$|MAE|MAPE|RMSE)\s*&',line):
            fields=line.split('&')
            rows.append([v.strip().removesuffix('\\\\').strip() for v in fields[2:]])
    return rows

datasets=['CS2','CX2','Oxford']
records={}
replacements={}
for f in files:
    text=before[f]
    old=parse_old(text)
    prefix=text[:text.index('\\begin{tabularx}')]
    rows=[]
    if f.endswith('table_4_9.tex'):
        assert len(old)==8 and all(len(r)==4 for r in old)
        spec=r'L{1.60}C{1.20}C{0.80}C{0.80}C{0.80}C{0.80}'
        head=r'Transfer & \makecell{Adaptation\\ratio (\%)} & $R^2$ & MAE & MAPE & RMSE \\'
        data=[]
        for s,source in enumerate(datasets[:2]):
            if s: rows.append(r'\TableGroupSpace')
            for j,ratio in enumerate([10,30,50,70]):
                values=[old[s*4+k][j] for k in range(4)]
                direction=source+r' $\to$ Oxford'
                rows.append(' & '.join([direction,str(ratio)]+['$'+v+'$' for v in values])+r' \\')
                data.append([source,'Oxford',ratio]+values)
    else:
        assert len(old)==12 and all(len(r)==3 for r in old)
        spec=r'L{0.90}L{0.90}C{1.20}C{1.00}C{1.00}C{1.00}'
        head=r'Source & Target & $R^2$ & MAE & MAPE & RMSE \\'
        data=[]
        for s,source in enumerate(datasets):
            for t,target in enumerate(datasets):
                values=[old[s*4+k][t] for k in range(4)]
                if s==t:
                    assert values==['---']*4
                    continue
                rows.append(' & '.join([source,target]+['$'+v+'$' for v in values])+r' \\')
                data.append([source,target]+values)
    assert all(re.fullmatch(r'-?\d+\.\d{4}',v) for row in data for v in row[-4:])
    replacements[f]=prefix+'\\begin{tabularx}{\\linewidth}{@{\\extracolsep{\\fill}}'+spec+'@{}}\n\\toprule\n'+head+'\n\\midrule\n'+'\n'.join(rows)+'\n\\bottomrule\n\\end{tabularx}\n\\end{table}\n'
    records[f]=data

for row in records[files[2]]:
    if row[2]==30:
        r=next(v for v in records[files[1]] if v[:2]==row[:2])
        assert row[-4:]==r[-4:]

protected=[p for d in ('chapters','tables','figures','algorithms','backmatter') for p in (root/d).glob('*.tex')]+[root/'preamble.tex',root/'main.tex',root/'table-style.tex']
hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
backup.mkdir(parents=True,exist_ok=False)
for rel in files+['chapters/chapter04.tex','tables/table_4_4.tex','table-style.tex','output/main.pdf','main.pdf','output/pdf/thesis_typeset.pdf']:
    p=root/rel
    if p.exists():
        dst=backup/'before'/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dst)
(backup/'before_hashes.json').write_text(json.dumps(hashes,indent=2,ensure_ascii=False),encoding='utf-8')
(backup/'transposed_records.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
for rel,content in replacements.items():
    (root/rel).write_text(content,encoding='utf-8',newline='\n')
chapfile.write_text(chapter.replace(anchor,anchor+sentence),encoding='utf-8',newline='\n')

changed=[rel for rel,h in hashes.items() if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=h]
assert sorted(changed)==sorted(files+['chapters/chapter04.tex']),changed
assert (root/'tables/table_4_4.tex').read_bytes()==(backup/'before/tables/table_4_4.tex').read_bytes()
assert chapfile.read_text(encoding='utf-8')==chapter.replace(anchor,anchor+sentence)
for rel in files:
    source_numbers=[n for row in parse_old(before[rel]) for n in row if n!='---']
    after_numbers=re.findall(r'\$(-?\d+\.\d{4})\$',(root/rel).read_text(encoding='utf-8'))
    assert sorted(source_numbers)==sorted(after_numbers)
report={'backup':str(backup),'changed':changed,'verified_values':80,'table11_unchanged':True,'thirty_percent_rows_match':True,'status':'awaiting compilation and visual inspection'}
(backup/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
(root/'tmp/table141516_backup_path.txt').write_text(str(backup),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
