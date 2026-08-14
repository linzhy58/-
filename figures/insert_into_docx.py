#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把技术路线图插入申请书 Word 文件（原文件不改动，另存新文件）。

插入位置：三、思路方法 →（一）总体研究思路 正文段落之后。
图片按版心宽 100% 放置，随后自动追加一段图注。

用法：python3 insert_into_docx.py 原文件.docx 输出文件.docx [图片.png]
"""
import re
import shutil
import struct
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------ 版面参数
# 正文位于一个单列表格内：列宽 9588 twips，左右单元格边距各 108 twips
CELL_W, CELL_MAR = 9588, 108
EMU_PER_TWIP = 635
BODY_W_TWIP = CELL_W - 2 * CELL_MAR                 # 9372 twips = 165.3 mm

ANCHOR = "项目分两个阶段推进。"                        # 插入锚点段落的开头
FONT = ('<w:rFonts w:hint="eastAsia" w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
        'w:eastAsia="宋体" w:cs="Times New Roman"/>')

CAPTION = (
    "图1  研究技术路线。阶段Ⅰ开发、验证并锁定客观疼痛指数（OPI）模型与风险阈值，"
    "阶段Ⅱ以随机对照试验比较OPI辅助的人机协同闭环管理与常规管理，"
    "主要终点为术后0–24 h活动痛NRS时间加权平均值。"
)


def png_size(path):
    d = Path(path).read_bytes()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"不是 PNG 文件：{path}")
    return struct.unpack(">II", d[16:24])


def build_drawing(rid, cx, cy):
    return (
        '<w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="1001" name="图1 研究技术路线"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr><pic:cNvPr id="0" name="study-design.png"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
    )


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "src.docx")
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else HERE / "out.docx")
    img = Path(sys.argv[3] if len(sys.argv) > 3 else HERE / "study-design.png")

    px_w, px_h = png_size(img)
    cx = BODY_W_TWIP * EMU_PER_TWIP                 # 图宽 = 版心宽
    cy = round(cx * px_h / px_w)                    # 等比高度
    print(f"图片 {px_w}×{px_h} px → 排版 {cx / 360000:.1f} × {cy / 360000:.1f} cm")

    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    doc = zin.read("word/document.xml").decode("utf-8")
    rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
    ct = zin.read("[Content_Types].xml").decode("utf-8")

    # --- 关系与内容类型 ---
    used = {int(m) for m in re.findall(r'Id="rId(\d+)"', rels)}
    rid = f"rId{max(used) + 1}"
    rels = rels.replace(
        "</Relationships>",
        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/'
        f'2006/relationships/image" Target="media/study-design.png"/></Relationships>')
    if 'Extension="png"' not in ct:
        ct = ct.replace("<Types ", "<Types ", 1).replace(
            "</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')

    # --- 命名空间 ---
    root_end = doc.index(">", doc.index("<w:document"))
    root = doc[:root_end + 1]
    for prefix, uri in [
        ("wp", "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"),
        ("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships"),
        ("a", "http://schemas.openxmlformats.org/drawingml/2006/main"),
        ("pic", "http://schemas.openxmlformats.org/drawingml/2006/picture"),
    ]:
        if f"xmlns:{prefix}=" not in root:
            root = root[:-1] + f' xmlns:{prefix}="{uri}">'
            print(f"补充命名空间 xmlns:{prefix}")
    doc = root + doc[root_end + 1:]

    # --- 定位锚点段落 ---
    i = doc.find(ANCHOR)
    if i < 0:
        sys.exit(f"未找到锚点段落：{ANCHOR}")
    insert_at = doc.index("</w:p>", i) + len("</w:p>")

    fig_p = (
        '<w:p><w:pPr><w:spacing w:before="180" w:after="60" w:line="240" w:lineRule="auto"/>'
        '<w:ind w:firstLine="0"/><w:jc w:val="center"/><w:snapToGrid w:val="0"/></w:pPr>'
        + build_drawing(rid, cx, cy) + '</w:p>'
    )
    cap_p = (
        '<w:p><w:pPr><w:spacing w:before="0" w:after="180" w:line="260" w:lineRule="auto"/>'
        '<w:ind w:firstLine="0"/><w:jc w:val="both"/></w:pPr>'
        f'<w:r><w:rPr>{FONT}<w:b w:val="0"/><w:sz w:val="18"/></w:rPr>'
        f'<w:t xml:space="preserve">{CAPTION}</w:t></w:r></w:p>'
    )
    doc = doc[:insert_at] + fig_p + cap_p + doc[insert_at:]

    # --- 重新打包 ---
    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            if n == "word/document.xml":
                zout.writestr(n, doc)
            elif n == "word/_rels/document.xml.rels":
                zout.writestr(n, rels)
            elif n == "[Content_Types].xml":
                zout.writestr(n, ct)
            else:
                zout.writestr(n, zin.read(n))
        zout.writestr("word/media/study-design.png", img.read_bytes())
    print(f"已写出 {dst}")


if __name__ == "__main__":
    main()
