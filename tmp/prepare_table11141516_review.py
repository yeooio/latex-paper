from pathlib import Path
import re

root = Path('D:/初稿/latex-paper')
out = Path('D:/初稿/修改/Table11_14_15_16精简候选_20260908.md')
names = {11:'table_4_4.tex',14:'table_4_7.tex',15:'table_4_8.tex',16:'table_4_9.tex'}
sources = {n:(root/'tables'/name).read_text(encoding='utf-8') for n,name in names.items()}

def metric_rows(n):
    rows=[]
    for line in sources[n].splitlines():
        if re.search(r'&\s*(?:\$R\^2\$|MAE|MAPE|RMSE)\s*&',line):
            fields=line.split('&')
            rows.append([v.strip().removesuffix('\\\\').strip() for v in fields[2:]])
    return rows

datasets=['CS2','CX2','Oxford']
transfers={}
for n in (14,15):
    old=metric_rows(n)
    assert len(old)==12 and all(len(r)==3 for r in old)
    new=[]
    for s,source in enumerate(datasets):
        for t,target in enumerate(datasets):
            vals=[old[s*4+k][t] for k in range(4)]
            if s==t:
                assert vals==['---']*4
            else:
                assert all(re.fullmatch(r'-?\d+\.\d{4}',v) for v in vals)
                new.append([source,target]+vals)
    assert len(new)==6
    transfers[n]=new

old=metric_rows(16)
assert len(old)==8 and all(len(r)==4 for r in old)
new=[]
for s,source in enumerate(datasets[:2]):
    for r,ratio in enumerate((10,30,50,70)):
        vals=[old[s*4+k][r] for k in range(4)]
        assert all(re.fullmatch(r'-?\d+\.\d{4}',v) for v in vals)
        new.append([source+' → Oxford',str(ratio)]+vals)
        if ratio==30:
            reference=next(x for x in transfers[15] if x[:2]==[source,'Oxford'])
            assert vals==reference[2:]
transfers[16]=new

def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(row)+' |' for row in rows])

architecture=[
    ['MS-AgentNet','Embedding (16); SLFA; DSConv-L; FFN'],
    ['CNN-Transformer','Embedding (16); positional encoding; Softmax attention; 2 × Conv1D + ReLU; MLP; Transformer decoder'],
    ['Transformer','Embedding (16); positional encoding; Softmax attention; MLP; Transformer decoder'],
    ['CNN-LSTM','Conv1D + ReLU; MaxPooling1D; 3 × Conv1D + ReLU; 3 × LSTM (16)'],
    ['LSTM','Linear (16); 5 × LSTM (16)'],
]
parts=['# Table 11、14、15、16：精简候选\n',
'状态：审阅与候选稿，尚未应用正式 LaTeX。依据当前表格源码及 output/main.pdf 第 19、24、25 页。原表已使用统一字号和三线表；本轮重点是信息组织，不能笼统判定其违反期刊规范。\n',
'## Table 11：将逐层清单压缩为主要结构概览\n',
'位置与作用：Oxford 性能比较之前，用于交代五类比较模型的主要结构差异。\n',
'问题：五个模型作为列，逐项堆叠 Input、Embedding、Add & Norm、Linear 等内容。各列长度不同，同一水平行也不表示同一处理阶段；当前表身较高且长模型名被拆行。\n',
'处理类型：表内结构备选。推荐每模型一行、两列；仅概括主要组件，不再称为完整层配置。章内顺序和模型均不变。若只做轻微排版，则保持原五列并改善换行，但压缩幅度有限。\n',
'建议表题：Main architectural components of the compared models.\n',
table(['Model','Main components'],architecture)+'\n',
'删冗边界：省略五个模型重复的 Input 和末端 Linear，不再逐项列残差与归一化连接。保留嵌入宽度、循环宽度、卷积及循环层数、池化位置与模型特有模块。LSTM 的输入 Linear (16) 保留；CNN-LSTM 保留首层卷积、池化和后三层卷积的次序。此表来自现有结构说明的压缩，不代表本轮已按代码重新核验模型实现。\n',
'正文必要联动（微调）：\n\n改前：五种模型的层配置如\\cref{tab:4-4}所示。\n\n改后：五种模型的主要结构组成如\\cref{tab:4-4}所示。\n',
'效果：读者先看见各模型的核心组件差异，具体的 MS-AgentNet 残差与归一化结构由第三章已存在的说明承担。\n',
'## Table 14、15：每行一个迁移方向\n',
'位置与作用：Table 14 报告直接迁移，Table 15 报告 30% 适应后的结果，两者用于比较相同六个方向在不同条件下的表现。\n',
'问题：原表每个源域重复四个指标名，三组各四行，共十二行；同域未评价的位置占十二个破折号单元格。表头也没有明确标示 CS2、CX2、Oxford 是目标域。训练电池编号已在迁移协议正文中交代。\n',
'处理类型：表内行列重排、删除重复标签；两表各改为六行，统一方向排序。题目沿用现有简短表题，保留全部实测数值。\n',
'Table 14 — Direct cross-dataset transfer results.\n',
table(['Source','Target','$R^2$','MAE','MAPE','RMSE'],transfers[14])+'\n',
'Table 15 — Transfer results after 30% target-domain adaptation.\n',
table(['Source','Target','$R^2$','MAE','MAPE','RMSE'],transfers[15])+'\n',
'效果：同一行完整呈现一个迁移任务；对应方向在两张表中位于同一行，便于核对适应前后变化。未评价的同域任务不再占格，不删任何实测结果。\n',
'## Table 16：明确目标域，统一条件与指标的组织方式\n',
'位置与作用：在 Oxford 目标域固定的前提下，比较四种适配比例。\n',
'问题：现有表题及表身只写源域和比例，单独阅读无法辨认目标域为 Oxford。它原本已是八行，重排不会自动减少数值量。\n',
'处理类型：表内行列重排。候选为每行一个方向与适配比例，指标作为列，与 Table 14、15 保持一致。\n',
'Table 16 — Transfer results under different adaptation ratios.\n',
table(['Transfer','Adaptation ratio (%)','$R^2$','MAE','MAPE','RMSE'],transfers[16])+'\n',
'效果：方向与适配条件明确，同一列可阅读某项指标随比例的变化。四个比例均有比较功能，不建议仅为了缩短表格删掉 10%、50% 或 70%；30% 与 Table 15 的重合提供比较基准，也保留。若优先横向观察比例趋势，原行列方向可以保留，只将首列换为明确的迁移方向。\n',
'## 三张迁移表的表注\n',
'当前三条完全相同：Note: Results are averaged over three independent runs.\n',
'候选：移除三条重复表注，在迁移实验共同设置中仅交代一次“迁移实验结果为三次独立运行的平均值。”\n',
'建议插入于两项输入健康指标说明之后、不同源域—目标域组合结果小节之前。重复次数仍为三次；目前不能因计划五次就改成五次。用户此前不喜欢表注细节，本候选不增加种子列表、训练流程或统计长解释。\n',
'## 数据与形式边界\n',
'四项指标在本轮均保留。负 R² 是跨域适用边界的证据，全部保留。MAPE 延用当前比例数值，表头不标 (%)；只在 Adaptation ratio 列标百分比。已逐条件从原表转换 24 + 24 + 32 个数值，并核对 Table 16 的两条 30% 记录与 Table 15 对应方向完全一致。这里只核对表格转换，未重算原始实验。\n',
'继续使用当前全文宽度、字号和三线表设置；不恢复已被用户撤销的 0.90 倍宽度和全列右对齐方案。本候选未渲染为论文页面，正式应用时需编译并检查最终换行、间距与跨页位置。\n',
'## 原表完整源码（改前）\n']
for n in names:
    parts += [f'### Table {n}\n\n来源：{root / "tables" / names[n]}\n', '```latex\n'+sources[n].rstrip()+'\n```\n']
out.write_text('\n'.join(parts),encoding='utf-8')
print(str(out))
print('Verified by source/target/ratio: 80 metric values; both 30% overlaps match. Formal files unchanged.')
