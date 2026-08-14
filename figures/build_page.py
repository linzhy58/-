#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把生成的 SVG 片段与图版样式注入网页模板，输出 figures/study-design.html。"""
from pathlib import Path

D = Path(__file__).resolve().parent
html = (D / "page.template.html").read_text(encoding="utf-8")
svg = (D / "study-design.body.svg").read_text(encoding="utf-8")
css = (D / "figure.css").read_text(encoding="utf-8")

# figure.css 顶部的 :root token 块已在模板中另行定义主题，此处整体注入即可
html = html.replace("/*FIGURE_CSS*/", css.strip())
html = html.replace("<!--FIGURE_SVG-->", svg.strip())

out = D / "study-design.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out.name}  ({len(html)/1024:.1f} KB)")
