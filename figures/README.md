# 研究技术路线图 · 基于EEG多模态融合的术后镇痛闭环管理系统

课题申请书用的技术路线图：黑白、无英文，按申请书正文的实际版面尺寸排版，可直接插入 Word。

## 版面核算

| 项目 | 数值 |
| --- | --- |
| 排版宽度 | **165.3 mm**（正文单元格可用宽 9372 twips，非页面版心 146.5 mm） |
| 图片高度 | **216.6 mm**；加图注约 9 mm、段前段后约 7.5 mm ＝ 233 mm ≤ 版心高 246.2 mm |
| 图内字号 | 说明 **9.0 pt**（小五）· 节点标题 10.6 pt · 泳道标签 10.2 pt（正文为 10.5 pt 五号） |
| 位图精度 | 3956 × 5184 px，在 165.3 mm 宽下约 **608 dpi** |
| 插入位置 | 三、思路方法 →（一）总体研究思路，“项目分两个阶段推进……”一段之后 |

> 申请书正文排在一个单列表格里（列宽 9588 twips，左右单元格边距各 108 twips），
> 可用宽度比页面版心还宽 19 mm。按单元格宽度排版比按版心排版多出 13% 的字号。

## 文件

| 文件 | 用途 |
| --- | --- |
| `study-design.svg` | **黑白矢量原图**（申请书用）。可用 Illustrator / Inkscape / PowerPoint 打开逐字修改 |
| `study-design.png` | 608 dpi 位图，自行插图时用这个 |
| `study-design-color.svg` / `.png` | 同一版式的彩色版，留给答辩 PPT 或英文投稿 |
| `study-design.html` | 网页预览版（含版面核算与内容来源对照，自适应浅色/深色） |
| `build_figure.py` | 图版生成脚本 |
| `render_png.py` | SVG → 高分辨率 PNG，附截断校验 |
| `insert_into_docx.py` | 把图与图注插入申请书 Word（原文件不改动，另存新文件） |
| `build_page.py` | 生成网页预览版 |

## 使用

```bash
cd figures
python3 build_figure.py                       # → study-design.svg / -color.svg / body.svg / figure.css
python3 render_png.py study-design.svg study-design.png 2.7
python3 build_page.py                         # → study-design.html
python3 insert_into_docx.py 申请书.docx 申请书_含技术路线图.docx study-design.png
```

## 修改要点

- **改文字**：编辑 `build_figure.py` 里的 `P1`（阶段Ⅰ三步骤）、各 `card(...)` 的 items 列表、`NODES`（闭环四节点）。
  框高与连线自动重排；文案超出框宽时脚本会在末尾打印“溢出”告警。
- **改配色**：`BW_LIGHT`／`COLOR_LIGHT` 两组 CSS 变量；`BW_DARK`／`COLOR_DARK` 供网页深色模式使用。
- **改尺寸**：`PLACE_MM` 是插入 Word 时的排版宽度，脚本据此换算并打印图内文字的实际磅值。
  画布 `W` 只是设计栅格，改 `PLACE_MM` 即可整体缩放而不影响版式比例。
- **改图注**：`insert_into_docx.py` 顶部的 `CAPTION`；插入锚点为 `ANCHOR`。

## 已知环境问题（本仓库脚本已规避）

- `chromium --headless=new` 的 `--window-size` 把浏览器界面高度算进去，视口比窗口矮约 87 px，
  直接截图会丢掉图的底部。`render_png.py` 改用 `headless_shell` 并在渲染后做像素级留白校验。
- 图内使用系统中文字体栈（思源黑体 / Noto Sans SC / 苹方 / 微软雅黑）。若在无上述字体的环境导出 PNG，
  会回退到文泉驿正黑，字形略粗；定稿前建议在本地环境用 SVG 重新导出。
