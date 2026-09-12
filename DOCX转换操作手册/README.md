# LaTeX 论文转换为可编辑 DOCX 操作手册

> **最常见场景：只修改正文文字**
>
> 只改 `chapters/`、`abstract.tex`、`chapter05.tex` 或参考文献文字时，也必须重新生成 DOCX：
>
> ```powershell
> # 修改 LaTeX 文字后，先重新编译 main.pdf
> $py = 'C:\Users\c1342\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
> & $py tools\build_docx_verified.py
> Copy-Item 'output\docx_verified\MS-AgentNet_可编辑论文.docx' `
>   'output\docx_verified\MS-AgentNet_editable_final.docx' -Force
> ```
>
> 只编译 `main.pdf` 不会更新 DOCX；必须再运行 `tools\build_docx_verified.py`。不需要手动重新截图表格或重新插入图片，脚本会自动处理。
本手册对应当前仓库中的最终转换脚本和输出文件。目标是把最新 LaTeX 论文转换成 Word 文档：正文和公式可编辑，普通图片正常插入，表格使用最新 PDF 的截图，正文引用和参考文献支持跳转。

最终文件：

`output/docx_verified/MS-AgentNet_editable_final.docx`

转换主脚本：

`tools/build_docx_verified.py`

---

## 一、当前流程是怎样工作的

转换不是把 PDF 直接转成 Word，而是分成四部分：

1. 读取 `main.tex`、`chapters/`、`tables/`、`figures/` 和 `backmatter/references.tex`；
2. 展开 LaTeX 输入文件，将正文、公式、标题、引用和参考文献转换为 Markdown；
3. 使用 Pandoc 将 Markdown 转换为 DOCX，使正文和公式尽量保持可编辑；
4. 从最新 `main.pdf` 中裁剪表格图片，从 `figures/` 中读取普通图片，再写回 DOCX，并用 Word 渲染检查分页和比例。

表格采用图片是有意设计：LaTeX 表格中存在复杂列宽、数学符号和跨页布局，直接转换容易乱码或错列。表格图片来自当前 PDF，因此视觉上与 PDF 一致，但表格单元格本身不能编辑。

---

## 二、重要文件和目录

| 路径 | 用途 | 是否直接修改 |
|---|---|---|
| `main.tex` | 论文入口文件 | 按论文写作流程修改 |
| `chapters/` | 正文章节 | 按论文写作流程修改 |
| `tables/` | LaTeX 表格源文件 | 按论文写作流程修改 |
| `figures/` | 普通图片和图源 | 按论文写作流程修改 |
| `backmatter/references.tex` | 参考文献 | 按论文写作流程修改 |
| `main.pdf` | 最新视觉基准 | 由 LaTeX 编译生成 |
| `tools/build_docx_verified.py` | 自动转换脚本 | 一般不要修改 |
| `output/docx_verified/` | DOCX、表格截图和验证文件 | 自动生成 |
| `DOCX转换操作手册/` | 本说明文档 | 可补充维护 |

`output/docx_verified/assets/` 中的 `table_*.png` 是从当前 `main.pdf` 裁剪出的表格，不能脱离对应 PDF 版本单独复用。

---

## 三、首次生成 DOCX

### 1. 准备环境

当前流程使用：

- Python：Codex 工作区运行时中的 Python；
- Pandoc：安装在 `tmp/docx-deps/pypandoc/files/pandoc.exe`；
- `python-docx`、`pdfplumber`、Pillow；
- Microsoft Word：用于最终 PDF 渲染检查；
- Poppler：用于 PDF 页面和表格裁剪。

如果 `tmp/docx-deps/pypandoc/files/pandoc.exe` 不存在，可以用工作区 Python 安装：

```powershell
$py = 'C:\Users\c1342\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m pip install --target 'tmp\docx-deps' pypandoc_binary
```

### 2. 先编译最新论文 PDF

修改论文源文件后，先用仓库已有的 LaTeX 编译方式更新 `main.pdf`。编译成功的判断是：

- `main.pdf` 时间戳已更新；
- PDF 可以打开；
- 页数和图表编号正常；
- `main.log` 没有未处理的致命错误。

### 3. 运行转换脚本

在仓库根目录运行：

```powershell
$py = 'C:\Users\c1342\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py tools\build_docx_verified.py
```

脚本会重新生成：

- `output/docx_verified/MS-AgentNet_可编辑论文.docx`；
- `output/docx_verified/assets/table_01.png` 等表格截图；
- `output/docx_verified/manifest.json`；
- 中间的 `conversion.tex`、`paper.md` 和 `base.docx`。

生成完成后，将中文文件复制为稳定的英文文件名：

```powershell
Copy-Item 'output\docx_verified\MS-AgentNet_可编辑论文.docx' `
  'output\docx_verified\MS-AgentNet_editable_final.docx' -Force
```

---

## 四、只修改正文文字时怎么做

这是最常见的情况。只要修改的是 `chapters/`、摘要或结论中的文字，通常不需要手动改 DOCX。

按以下顺序操作：

1. 修改 LaTeX 正文；
2. 重新编译 `main.pdf`；
3. 重新运行 `tools/build_docx_verified.py`；
4. 重新生成 `MS-AgentNet_editable_final.docx`；
5. 检查新增或删除文字是否造成分页变化；
6. 检查公式编号、图表编号和正文引用是否仍连续。

也就是说，**不是只编译 LaTeX 就能自动更新 DOCX**。LaTeX 编译只更新 PDF；DOCX 必须重新运行转换脚本。

如果只是改了一个普通句子，也建议完整重跑脚本，因为表格截图页码、图表位置和引用跳转可能随正文长度变化。

---

## 五、修改公式时怎么做

修改公式时必须重新编译 PDF，再重新运行 DOCX 脚本。

脚本会：

- 从 LaTeX 公式生成 Word 公式对象；
- 根据 LaTeX 的编号重新写入右侧公式编号；
- 根据 `\label{eq:...}` 建立公式跳转目标；
- 根据 `\eqref{...}` 或 `\cref{...}` 生成内部链接。

不要直接在最终 DOCX 中手动改公式后再继续自动转换，因为下一次转换会覆盖手工修改。

---

## 六、修改普通图片时怎么做

如果替换 `figures/` 中的普通图片：

1. 保持图片文件名不变，或同步修改对应的 `figure_*.tex`；
2. 重新编译 `main.pdf`；
3. 重新运行转换脚本；
4. 检查图片清晰度、比例和图题是否在同一页。

如果新增图片，必须在 `main.tex` 或相应章节中通过 `figure_*.tex` 引入，并写好 `\caption` 和 `\label`。脚本会根据图标签插入图片。

Figure 4.2 和 Figure 4.3 这类复杂对比图，当前采用最新 PDF 页面中的完整图区域截图，以确保 Word 中的图与 PDF 视觉一致。更新这类图后，必须以最新 `main.pdf` 为准重新裁剪，不能继续使用旧的合成面板。

---

## 七、修改表格时怎么做

表格的正确流程是：

1. 修改 `tables/` 中的 LaTeX 表格源文件；
2. 重新编译 `main.pdf`；
3. 确认 PDF 中表格内容、标题和分页正确；
4. 重新运行转换脚本；
5. 脚本从新的 `main.pdf` 自动裁剪表格截图；
6. 检查 `output/docx_verified/assets/table_*.png`。

不要直接编辑 `output/docx_verified/assets/table_*.png`，因为下一次运行会覆盖它们。

如果新增或删除表格，必须同时更新：

- LaTeX 表格文件中的 `\caption` 和 `\label`；
- `main.aux` 中的表格编号；
- `tools/build_docx_verified.py` 中的表格识别规则（只有脚本无法自动识别时才需要修改）。

---

## 八、修改参考文献时怎么做

修改 `backmatter/references.tex` 后：

1. 重新编译 `main.pdf`，确保引用编号和参考文献列表正确；
2. 重新运行 DOCX 脚本；
3. 在 Word 中点击正文引用，确认能跳转到对应参考文献；
4. 检查新增文献是否出现重复编号或断号。

不要在 DOCX 中手动给参考文献重新编号。编号应由 LaTeX 源文件和转换脚本共同生成。

---

## 九、最终检查命令

### DOCX 结构检查

```powershell
$py = 'C:\Users\c1342\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import zipfile; p='output/docx_verified/MS-AgentNet_editable_final.docx'; z=zipfile.ZipFile(p); print(z.testzip())"
```

输出 `None` 表示 DOCX 压缩包没有损坏。

### Word 渲染检查

用 Microsoft Word 将 DOCX 导出为 PDF，然后使用 Poppler 转 PNG。重点检查：

- Figure 4.2 和 Figure 4.3 是否使用最新 PDF 中的图；
- 图题是否与图在同一页；
- 表格截图是否清晰；
- 公式编号是否连续；
- 正文引用和参考文献是否能跳转；
- 是否出现空白页、图片拉伸、文字溢出或页码错误。

### 结果状态

`output/docx_verified/manifest.json` 中的 `status` 用于记录转换状态。只有在 DOCX 成功打开并完成渲染检查后，才应标记为 `verified_with_word_render` 或更具体的已修复状态。

---

## 十、常见问题

### 修改文字后 DOCX 没有变化

原因通常是只重新编译了 LaTeX，没有重新运行 DOCX 脚本。重新执行：

```powershell
& $py tools\build_docx_verified.py
```

### 图表编号错了

先检查 LaTeX 源文件中的 `\caption`、`\label` 和编译生成的 `main.aux`。确认 PDF 编号正常后，再重跑 DOCX。

### 表格出现乱码

不要把表格当 Markdown 表格转换。确认表格截图来自最新 `main.pdf`，并检查 `assets/table_*.png` 是否为最新时间戳。

### 图片被拉伸

检查图片源文件的宽高比，以及脚本写入的 Word 图片尺寸。不能只替换 DOCX 压缩包里的图片文件而不更新 Word 的尺寸参数。

### Word 提示文档损坏

优先检查：

- 是否有 Word 进程锁定文件；
- 是否在 DOCX 写入过程中中断；
- `zipfile.testzip()` 是否返回 `None`；
- 是否误将 PNG 或 PDF 覆盖成 DOCX 文件。

### 需要恢复上一版

当前转换脚本不会删除 LaTeX 源文件。旧版 DOCX 若需要保留，应在重新生成前复制到备份目录，并记录对应的 `main.pdf` SHA-256 或提交号。

---

## 十一、推荐的日常操作简表

### 只改文字

```text
改 chapters/ 或参考文献
→ 编译 main.pdf
→ 运行 build_docx_verified.py
→ 检查 DOCX
```

### 改公式

```text
改 LaTeX 公式和 label
→ 编译 main.pdf
→ 运行 build_docx_verified.py
→ 检查公式编号和跳转
```

### 改图

```text
替换 figures/ 图片或 figure_*.tex
→ 编译 main.pdf
→ 运行 build_docx_verified.py
→ 检查图比例和图题
```

### 改表

```text
改 tables/ 表格源文件
→ 编译 main.pdf
→ 运行 build_docx_verified.py
→ 检查 assets/table_*.png
→ 检查 DOCX 中对应位置
```

最终原则：**PDF 是视觉基准，LaTeX 是内容基准，DOCX 是重新生成的交付物。**
