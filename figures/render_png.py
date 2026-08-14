#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 SVG 渲染为高分辨率 PNG，并校验没有被截断。

注意：chromium 的 --headless=new 会把浏览器界面高度算进 --window-size，
视口比窗口矮约 87 px，直接截图会丢掉图底部。这里用纯 headless_shell，
渲染后再用像素校验确认四边留白符合预期。

用法：python3 render_png.py study-design.svg study-design.png [缩放倍数]
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
HERE = Path(__file__).resolve().parent


def svg_size(path):
    s = Path(path).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s)
    return round(float(vb.group(1))), round(float(vb.group(2)))


def render(svg, png, scale=2.7):
    w, h = svg_size(svg)
    wrap = HERE / "_wrap.html"
    wrap.write_text(
        "<style>html,body{margin:0;padding:0;background:#fff}"
        f"img{{display:block;width:{w}px;height:{h}px}}</style>"
        f'<img src="file://{Path(svg).resolve()}">', encoding="utf-8")
    subprocess.run(
        [SHELL, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         f"--force-device-scale-factor={scale}", f"--window-size={w},{h}",
         f"--screenshot={Path(png).resolve()}", f"file://{wrap}"],
        check=True, capture_output=True)
    wrap.unlink(missing_ok=True)

    im = Image.open(png)
    if im.size != (round(w * scale), round(h * scale)):
        sys.exit(f"尺寸异常：{im.size}，应为 {(round(w * scale), round(h * scale))}")

    g = im.convert("L")
    iw, ih = g.size
    bbox = g.point(lambda v: 0 if v > 252 else 255).getbbox()   # 非白内容包围盒
    if not bbox:
        sys.exit("渲染结果全白")
    pad = (bbox[0], bbox[1], iw - bbox[2], ih - bbox[3])        # 左 上 右 下 留白
    exp = round(40 * scale)                                      # 设计稿页边距 M=40
    if pad[3] > exp + round(40 * scale) or pad[3] < round(10 * scale):
        sys.exit(f"底部留白 {pad[3]}px 异常，可能被截断（左上右下留白 {pad}）")
    print(f"{Path(png).name}  {iw}×{ih}px  留白(左上右下)={pad}  "
          f"≈{iw / (165.3 / 25.4):.0f} dpi @165.3mm")


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "study-design.svg",
           sys.argv[2] if len(sys.argv) > 2 else "study-design.png",
           float(sys.argv[3]) if len(sys.argv) > 3 else 2.7)
