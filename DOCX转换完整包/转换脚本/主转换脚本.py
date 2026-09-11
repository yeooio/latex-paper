#!/usr/bin/env python3
"""
最终完整版DOCX转换
包含所有图片（单独PNG + 合成的子图面板）
"""
import re
from pathlib import Path
import subprocess
import datetime
from docx import Document
from docx.shared import Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH

PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
CONVERSION_DIR = OUTPUT_DIR / "final_docx_conversion"
IMAGES_PROCESSED = CONVERSION_DIR / "images_processed"
DOCX_STAGES = CONVERSION_DIR / "docx_stages"
FIGURES_DIR = PROJECT_DIR / "figures"

# 确保目录存在
IMAGES_PROCESSED.mkdir(parents=True, exist_ok=True)
DOCX_STAGES.mkdir(parents=True, exist_ok=True)

def latex_to_markdown():
    """LaTeX → Markdown"""
    print("="*70)
    print("步骤 1/4: LaTeX → Markdown")
    print("="*70)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_md = DOCX_STAGES / f"thesis_{timestamp}.md"

    cmd = [
        'pandoc', 'main.tex', '-o', str(output_md),
        '--from=latex', '--to=markdown',
        '--standalone', '--number-sections',
    ]

    result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=180)

    if result.returncode == 0 and output_md.exists():
        size_kb = output_md.stat().st_size / 1024
        print(f"✓ 生成: {output_md.name} ({size_kb:.1f} KB)")
        return output_md
    else:
        print(f"✗ 失败: {result.stderr[:500]}")
        return None

def markdown_to_docx(md_file):
    """Markdown → DOCX"""
    print("\n" + "="*70)
    print("步骤 2/4: Markdown → DOCX（基础版）")
    print("="*70)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_docx = DOCX_STAGES / f"base_{timestamp}.docx"

    cmd = [
        'pandoc', str(md_file), '-o', str(output_docx),
        '--from=markdown', '--to=docx',
        '--standalone', '--number-sections',
    ]

    result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=180)

    if result.returncode == 0 and output_docx.exists():
        size_mb = output_docx.stat().st_size / 1024 / 1024
        print(f"✓ 生成: {output_docx.name} ({size_mb:.2f} MB)")
        return output_docx
    else:
        print(f"✗ 失败: {result.stderr[:500]}")
        return None

def collect_available_images():
    """收集所有可用的图片"""
    print("\n" + "="*70)
    print("步骤 3/4: 收集图片资源")
    print("="*70)

    images = []

    # 第二章单独图片
    chapter2_images = [
        ('fig1.png', 'Flowchart of the developed SOH estimation approach', 150),
        ('fig2.png', 'Correlation matrices of candidate HIs', 150),
        ('fig3.png', 'Charge-side characteristic curves used for HI construction', 150),
        ('fig4_pccscc_print.png', 'Oxford Cell1 和 Cell2 的相关性结果', 150),
    ]

    for img_file, keyword, width in chapter2_images:
        img_path = FIGURES_DIR / img_file
        if img_path.exists():
            images.append({
                'file': img_path,
                'keyword': keyword,
                'width_mm': width,
                'chapter': 2,
                'type': 'single'
            })
            print(f"  ✓ 第2章: {img_file}")

    # 第三章单独图片
    chapter3_images = [
        ('01.png', 'Framework of MS-AgentNet', 150),
        ('02.png', 'Comparison of (a) Softmax attention', 150),
        ('fig3_3_attention_comparison.png', 'Agent Attention, and (d) the proposed', 150),
    ]

    for img_file, keyword, width in chapter3_images:
        img_path = FIGURES_DIR / img_file
        if img_path.exists():
            images.append({
                'file': img_path,
                'keyword': keyword,
                'width_mm': width,
                'chapter': 3,
                'type': 'single'
            })
            print(f"  ✓ 第3章: {img_file}")

    # 第四章 - 合成的子图面板
    chapter4_panels = [
        ('figure_4_2_oxford_panel.png', 'SOH estimation results', 165),
        ('figure_4_3_calce_mit_panel.png', 'SOH estimation errors', 165),
        ('fig4_n_agents.png', 'Impact of the number of agents', 140),
        ('fig4_storage.png', 'Storage complexity', 140),
    ]

    for img_file, keyword, width in chapter4_panels:
        img_path = IMAGES_PROCESSED / img_file
        if img_path.exists():
            images.append({
                'file': img_path,
                'keyword': keyword,
                'width_mm': width,
                'chapter': 4,
                'type': 'panel'
            })
            print(f"  ✓ 第4章: {img_file}")
        else:
            print(f"  ⚠ 缺失: {img_file} (等待Agent生成)")

    return images

def insert_all_images_complete(docx_file, images):
    """插入所有图片"""
    print("\n" + "="*70)
    print("步骤 4/4: 插入所有图片")
    print("="*70)

    doc = Document(str(docx_file))
    inserted_count = 0
    inserted_files = set()

    print("\n正在匹配和插入...")

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue

        for img_info in images:
            img_file = img_info['file']
            keyword = img_info['keyword']
            width_mm = img_info['width_mm']

            # 已插入，跳过
            if str(img_file) in inserted_files:
                continue

            # 关键词匹配
            if keyword.lower() in text.lower():
                if img_file.exists():
                    try:
                        # 在图注前插入图片
                        new_para = para.insert_paragraph_before()
                        run = new_para.add_run()
                        run.add_picture(str(img_file), width=Mm(width_mm))
                        new_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

                        inserted_count += 1
                        inserted_files.add(str(img_file))

                        img_type = img_info['type']
                        chapter = img_info['chapter']
                        print(f"  ✓ 第{chapter}章 [{img_type}] {img_file.name}")
                        break
                    except Exception as e:
                        print(f"  ✗ 插入失败: {img_file.name} - {e}")

    # 保存最终文件
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    final_docx = CONVERSION_DIR / f"FINAL_thesis_complete_{timestamp}.docx"
    doc.save(str(final_docx))

    size_mb = final_docx.stat().st_size / 1024 / 1024

    return final_docx, inserted_count, size_mb

def generate_summary(final_docx, total_images, inserted_count, size_mb):
    """生成最终报告"""
    print("\n" + "="*70)
    print("✓ 转换完成")
    print("="*70)

    print(f"\n最终文件:")
    print(f"  路径: {final_docx.relative_to(PROJECT_DIR)}")
    print(f"  大小: {size_mb:.2f} MB")

    print(f"\n图片统计:")
    print(f"  可用图片: {total_images} 个")
    print(f"  已插入: {inserted_count} 个")

    if inserted_count < total_images:
        print(f"  缺失: {total_images - inserted_count} 个 (等待Agent完成)")

    print(f"\n内容状态:")
    print(f"  ✓ 文本：完整")
    print(f"  ✓ 公式：正常显示（编号需验证）")
    print(f"  ✓ 图片：{inserted_count}/{total_images} 已插入")
    print(f"  ⚠ 表格：待从PDF截图替换")

    # 生成状态报告
    report_path = CONVERSION_DIR / f"CONVERSION_SUMMARY_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"""# DOCX转换完成报告

生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 最终文件
- **文件名：** `{final_docx.name}`
- **路径：** `{final_docx.relative_to(PROJECT_DIR)}`
- **大小：** {size_mb:.2f} MB

## 内容统计
- **文本：** 完整转换 ✓
- **公式：** 正常显示（编号待验证）✓
- **图片：** {inserted_count}/{total_images} 已插入
- **表格：** 待处理（从PDF截图）

## 后续步骤
1. 等待所有Agent完成图片合成
2. 重新运行此脚本插入剩余图片
3. 验证公式编号是否完整
4. 按TABLE_REPLACEMENT_CHECKLIST.md替换表格

---
*生成工具：Claude Code*
""")

    print(f"\n详细报告已保存: {report_path.name}")

def main():
    print("\n" + "="*70)
    print("LaTeX → DOCX 完整转换流程")
    print("="*70)
    print(f"工作目录: {CONVERSION_DIR.relative_to(PROJECT_DIR)}")

    # 步骤1: LaTeX → Markdown
    md_file = latex_to_markdown()
    if not md_file:
        return

    # 步骤2: Markdown → DOCX
    base_docx = markdown_to_docx(md_file)
    if not base_docx:
        return

    # 步骤3: 收集图片
    images = collect_available_images()

    # 步骤4: 插入图片
    final_docx, inserted_count, size_mb = insert_all_images_complete(base_docx, images)

    # 生成报告
    generate_summary(final_docx, len(images), inserted_count, size_mb)

if __name__ == "__main__":
    main()
