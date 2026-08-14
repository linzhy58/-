# 研究技术路线图 · 术后疼痛神经解码与客观疼痛指数（OPI）

两阶段研究设计图版，按 SCI 期刊插图与基金申请书技术路线图规范排版。

## 文件

| 文件 | 用途 |
| --- | --- |
| `study-design.svg` | **矢量原图**（浅色，印刷用，含图注）。可用 Illustrator / Inkscape / PowerPoint 打开逐字修改，投稿首选 |
| `study-design@3x.png` | 3720 × 4581 位图，插入 Word 申请书约合 300 dpi |
| `study-design.html` | 网页预览版（含设计说明、占位符清单，自适应浅色/深色） |
| `build_figure.py` | 图版生成脚本：文案、配色、间距集中在顶部常量与内容列表中 |
| `build_page.py` | 将 SVG 片段与样式注入 `page.template.html`，输出预览页 |

## 重新生成

```bash
cd figures
python3 build_figure.py   # → study-design.svg / study-design.body.svg / figure.css
python3 build_page.py     # → study-design.html
```

导出高分辨率 PNG（需 Chromium）：

```bash
chrome --headless=new --hide-scrollbars \
  --force-device-scale-factor=3 --window-size=1240,1527 \
  --screenshot=study-design@3x.png file://$PWD/study-design.svg
```

## 修改要点

- **改文字**：编辑 `build_figure.py` 中的 `P1`（阶段Ⅰ三步骤）、各 `card(...)` 调用的 items 列表、`NODES`（闭环四节点）、`CAP1..CAP3`（图注）。连线与框高会自动重排。
- **改配色**：`TOKENS_LIGHT` / `TOKENS_DARK` 两组 CSS 变量。`--f-a1` 青色为神经解码链路，`--f-a2` 靛蓝为试验主流程，`--f-ctrl` 灰色为对照组，`--f-gate` 琥珀为里程碑。
- **待填占位**：图中 `n = ___` 与`约 __ 个月`为样本量与研究周期占位；主要结局、统计方法等为草稿文案，需按实际方案替换。

## 字体

图版使用系统中文字体栈（思源黑体 / Noto Sans SC / 苹方 / 微软雅黑）。若在无中文字体的环境渲染 PNG，会回退到 WenQuanYi 正黑，字形略粗；投稿时建议在本地环境重新导出。
