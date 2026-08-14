#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「术后疼痛神经解码与客观疼痛指数（OPI）」研究技术路线图。

输出：
  figures/study-design.svg      独立矢量图（浅色/印刷用，内含 <style>）
  figures/study-design.body.svg 仅 SVG 片段（供 HTML 页面内联，不含 <style>）
  figures/figure.css            供页面复用的样式（内联版本使用同名 class 与 token）
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- 画布与栅格
W = 1240
M = 44                      # 页边距
BX0, BX1 = M, W - M         # 泳道左右边界
IX0, IX1 = BX0 + 28, BX1 - 28   # 泳道内容边界
CX = W / 2                  # 主流程中轴

INNER = IX1 - IX0           # 1096

# ---------------------------------------------------------------- 文本工具
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def tw(text, size):
    """粗略估算文本宽度：CJK 1.0em，拉丁 0.55em，空格 0.3em。"""
    w = 0.0
    for ch in text:
        o = ord(ch)
        if ch == " ":
            w += 0.30
        elif o > 0x2E80 or ch in "－—·｜　":
            w += 1.0
        else:
            w += 0.55
    return w * size

def T(x, y, text, cls, anchor="start", extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x:g}" y="{y:g}" class="{cls}"{a}{extra}>{esc(text)}</text>'

# ---------------------------------------------------------------- 折线（圆角）
def elbow(pts, r=10, cls="conn", marker="ah"):
    """由若干正交点生成圆角折线路径。"""
    pts = [(float(a), float(b)) for a, b in pts]
    d = [f"M{pts[0][0]:g},{pts[0][1]:g}"]
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        d1x, d1y = x1 - x0, y1 - y0
        d2x, d2y = x2 - x1, y2 - y1
        l1 = (d1x ** 2 + d1y ** 2) ** 0.5 or 1
        l2 = (d2x ** 2 + d2y ** 2) ** 0.5 or 1
        rr = min(r, l1 / 2, l2 / 2)
        ax, ay = x1 - d1x / l1 * rr, y1 - d1y / l1 * rr
        bx, by = x1 + d2x / l2 * rr, y1 + d2y / l2 * rr
        cross = d1x * d2y - d1y * d2x
        sweep = 1 if cross > 0 else 0
        d.append(f"L{ax:g},{ay:g}")
        d.append(f"A{rr:g},{rr:g} 0 0 {sweep} {bx:g},{by:g}")
    d.append(f"L{pts[-1][0]:g},{pts[-1][1]:g}")
    mk = f' marker-end="url(#{marker})"' if marker else ""
    return f'<path d="{" ".join(d)}" class="{cls}" fill="none"{mk}/>'

def vline(x, y0, y1, cls="conn", marker="ah"):
    return elbow([(x, y0), (x, y1)], cls=cls, marker=marker)

# ---------------------------------------------------------------- 卡片渲染
# 行进：title +24 / title(续) +24 / en +20 / rule +16 / sub +19
PAD_TOP, PAD_BOT = 26, 20

def measure(items):
    b = PAD_TOP
    last = b
    for kind, _ in items:
        if kind in ("title", "title2"):
            last = b; b += 24
        elif kind == "en":
            last = b; b += 20
        elif kind == "rule":
            b += 16
        elif kind == "sub":
            last = b; b += 19
    return last + PAD_BOT

def card(x, y, w, items, tone="a1", align="left", badge=None, extra_cls=""):
    """tone: a1 / a2 / ctrl / gate ; align: left|center"""
    h = measure(items)
    tx = x + 22 if align == "left" else x + w / 2
    if badge:
        tx = x + 54 if align == "left" else tx
    anchor = "start" if align == "left" else "middle"
    out = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="8" '
           f'class="card card-{tone} {extra_cls}"/>']
    b = y + PAD_TOP
    for kind, text in items:
        if kind == "title":
            out.append(T(tx, b, text, f"t-title", anchor)); b += 24
        elif kind == "title2":
            out.append(T(tx, b, text, f"t-title", anchor)); b += 24
        elif kind == "en":
            out.append(T(tx, b, text, "t-en", anchor)); b += 20
        elif kind == "rule":
            out.append(f'<line x1="{x + 22:g}" y1="{b - 6:g}" x2="{x + w - 22:g}" '
                       f'y2="{b - 6:g}" class="hair"/>'); b += 16
        elif kind == "sub":
            if align == "left":
                out.append(f'<rect x="{x + 22:g}" y="{b - 8:g}" width="4" height="4" '
                           f'class="dot dot-{tone}"/>')
                out.append(T(x + 34, b, text, "t-sub", "start"))
            else:
                out.append(T(tx, b, text, "t-sub", anchor))
            b += 19
    if badge:
        cxb, cyb = x + 30, y + PAD_TOP - 5
        out.append(f'<circle cx="{cxb:g}" cy="{cyb:g}" r="13" class="badge badge-{tone}"/>')
        out.append(T(cxb, cyb + 5, badge, "t-badge", "middle"))
    return "\n".join(p for p in out if p), h

def band(y0, y1, tone):
    return (f'<rect x="{BX0:g}" y="{y0:g}" width="{BX1 - BX0:g}" '
            f'height="{y1 - y0:g}" rx="14" class="band band-{tone}"/>')

def tab(y_edge, tone, cn, en, right_note=""):
    h, pad = 36, 20
    w = tw(cn, 14.5) + pad * 2
    x = BX0 + 28
    y = y_edge - h / 2
    s = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{h/2:g}" '
         f'class="tab tab-{tone}"/>',
         T(x + pad, y + h / 2 + 5.2, cn, "t-tab", "start")]
    if en:
        s.append(T(x + w + 14, y + h / 2 + 4, en, f"t-tab-en tone-{tone}", "start"))
    if right_note:
        s.append(T(IX1, y + h / 2 + 4, right_note, "t-note", "end"))
    return "\n".join(s)

# ================================================================ 内容与布局
S = []          # svg 片段

# ---- 0. 入组 ---------------------------------------------------------------
ENTRY_W = 470
entry_y = 40
entry, entry_h = card(CX - ENTRY_W / 2, entry_y, ENTRY_W, [
    ("title", "术前筛选与知情同意"),
    ("en", "Preoperative screening & informed consent"),
    ("rule", ""),
    ("sub", "纳入／排除标准 · 基线与围术期资料采集 · 拟入组 n = ___"),
], tone="ink", align="center")
S.append(entry)
entry_b = entry_y + entry_h

# ---- 1. 阶段Ⅰ ---------------------------------------------------------------
B1_Y0 = entry_b + 30
box1_y = B1_Y0 + 66

P1 = [
    (["EEG 为核心的", "多模态神经生理感知"],
     "Multimodal neurophysiological sensing",
     ["围术期连续采集：EEG · HRV · EDA · 行为学",
      "同步记录 NRS／VAS 评分与镇痛用药"]),
    (["术后疼痛神经解码", "模型开发与验证"],
     "Decoding model development & validation",
     ["特征提取与降维 → 机器学习／深度学习建模",
      "内部交叉验证 + 时间／外部独立验证"]),
    (["客观疼痛指数（OPI）", "与风险阈值确定"],
     "Objective Pain Index & risk thresholds",
     ["连续量化输出（0–100）并与主观评分对齐",
      "确定预警截断值与疼痛风险分层"]),
]

BW = (INNER - 2 * 59) / 3      # 326
p1_boxes = []
for i, (titles, en, subs) in enumerate(P1):
    x = IX0 + i * (BW + 59)
    items = [("title", titles[0]), ("title2", titles[1]), ("en", en), ("rule", "")]
    items += [("sub", s) for s in subs]
    frag, h = card(x, box1_y, BW, items, tone="a1", badge=str(i + 1))
    p1_boxes.append((x, x + BW, h))
    S.append(frag)

box1_h = max(b[2] for b in p1_boxes)
box1_b = box1_y + box1_h
B1_Y1 = box1_b + 36
S.insert(1, band(B1_Y0, B1_Y1, "a1"))
S.insert(2, tab(B1_Y0, "a1", "阶段 Ⅰ · 前瞻性观察队列",
                "PHASE I · PROSPECTIVE OBSERVATIONAL COHORT", "研究周期：约 __ 个月"))

# 阶段Ⅰ内部横向箭头
for i in range(2):
    x0 = p1_boxes[i][1]
    x1 = p1_boxes[i + 1][0]
    ym = box1_y + box1_h / 2
    S.append(elbow([(x0 + 8, ym), (x1 - 4, ym)], cls="conn conn-a1"))

# ---- 2. 里程碑闸口 -----------------------------------------------------------
GATE_W = 620
gate_y = B1_Y1 + 44
gate, gate_h = card(CX - GATE_W / 2, gate_y, GATE_W, [
    ("title", "里程碑：模型锁定与 SOP 定稿"),
    ("en", "Milestone — model lock & standard operating procedure finalized"),
], tone="gate", align="center")
S.append(gate)
gate_b = gate_y + gate_h

# ③ → 闸口 的折线
c3 = (p1_boxes[2][0] + p1_boxes[2][1]) / 2
S.append(elbow([(c3, box1_b), (c3, B1_Y1 + 22), (CX, B1_Y1 + 22), (CX, gate_y - 4)],
               cls="conn conn-gate"))
# 入组 →（跨入阶段Ⅰ）→ 步骤①
c1 = (p1_boxes[0][0] + p1_boxes[0][1]) / 2
S.append(elbow([(CX, entry_b), (CX, B1_Y0 + 34), (c1, B1_Y0 + 34), (c1, box1_y - 4)],
               cls="conn"))

# ---- 3. 阶段Ⅱ ---------------------------------------------------------------
B2_Y0 = gate_b + 30
rand_w = 420
rand_y = B2_Y0 + 66
S.append(vline(CX, gate_b, rand_y - 4, cls="conn"))

rand, rand_h = card(CX - rand_w / 2, rand_y, rand_w, [
    ("title", "随机分组"),
    ("en", "Randomization  (1 : 1)"),
    ("rule", ""),
    ("sub", "分层区组随机 · 中央分配隐藏 · 结局评价者与统计师设盲"),
], tone="a2", align="center")
S.append(rand)
rand_b = rand_y + rand_h

# 两臂
AW = (INNER - 60) / 2          # 518
armL_x, armR_x = IX0, IX0 + AW + 60
armL_c, armR_c = armL_x + AW / 2, armR_x + AW / 2
arm_y = rand_b + 66

armL, hL = card(armL_x, arm_y, AW, [
    ("title", "客观疼痛指数（OPI）辅助组"),
    ("en", "OPI-assisted management  ·  intervention arm   n = ___"),
    ("rule", ""),
    ("sub", "常规镇痛管理 + OPI 连续监测与实时显示"),
    ("sub", "超阈值自动预警，触发人机协同决策"),
    ("sub", "按预设 SOP 调整镇痛方案并记录响应"),
], tone="a2")
armR, hR = card(armR_x, arm_y, AW, [
    ("title", "常规管理组"),
    ("en", "Standard care  ·  control arm   n = ___"),
    ("rule", ""),
    ("sub", "按现行镇痛常规进行管理"),
    ("sub", "定时 NRS／VAS 评估与经验性调整"),
    ("sub", "同步采集 OPI，但对医护与患者设盲"),
], tone="ctrl")
S.append(armL); S.append(armR)
arm_h = max(hL, hR)
arm_b = arm_y + arm_h

# 随机 → 两臂
split_y = rand_b + 34
S.append(elbow([(CX, rand_b), (CX, split_y), (armL_c, split_y), (armL_c, arm_y - 4)],
               cls="conn conn-a2"))
S.append(elbow([(CX, rand_b), (CX, split_y), (armR_c, split_y), (armR_c, arm_y - 4)],
               cls="conn conn-ctrl"))

# ---- 4. 人机协同闭环 ---------------------------------------------------------
loop_y = arm_b + 32
LOOP_H = 152
S.append(f'<rect x="{armL_x:g}" y="{loop_y:g}" width="{AW:g}" height="{LOOP_H:g}" '
         f'rx="8" class="loop"/>')
S.append(T(armL_x + 20, loop_y + 26, "神经解码驱动的人机协同闭环", "t-loop"))
S.append(T(armL_x + 20, loop_y + 45, "Neural-decoding-driven human–AI closed loop", "t-en"))

NODES = [("连续感知", "EEG · HRV · EDA"),
         ("实时 OPI", "0–100 连续输出"),
         ("阈值预警", "风险分层提示"),
         ("镇痛调整", "医护决策 + SOP")]
NW, NGAP = 105, 22
n_x0 = armL_x + 16
node_y = loop_y + 60
node_h = 46
centers = []
for i, (cn, en) in enumerate(NODES):
    nx = n_x0 + i * (NW + NGAP)
    nc = nx + NW / 2
    centers.append(nc)
    S.append(f'<rect x="{nx:g}" y="{node_y:g}" width="{NW:g}" height="{node_h:g}" '
             f'rx="6" class="node"/>')
    S.append(T(nc, node_y + 20, cn, "t-node", "middle"))
    S.append(T(nc, node_y + 35, en, "t-node-en", "middle"))
    if i:
        S.append(elbow([(centers[i - 1] + NW / 2 + 4, node_y + node_h / 2),
                        (nx - 3, node_y + node_h / 2)], cls="conn conn-a1"))

fb_y = node_y + node_h + 22
S.append(elbow([(centers[-1], node_y + node_h), (centers[-1], fb_y),
                (centers[0], fb_y), (centers[0], node_y + node_h + 4)],
               cls="conn conn-fb", marker="ah-fb", r=8))
fb_label = "疗效再评估 · 反馈"
fw = tw(fb_label, 11) + 12
S.append(f'<rect x="{(armL_x + AW / 2 - fw / 2):g}" y="{fb_y - 9:g}" width="{fw:g}" '
         f'height="16" class="lbl-bg"/>')
S.append(T(armL_x + AW / 2, fb_y + 4, fb_label, "t-fb", "middle"))
loop_b = loop_y + LOOP_H

S.append(elbow([(armL_c, arm_b), (armL_c, loop_y - 4)], cls="conn conn-a1"))

# ---- 5. 随访 / 统计 ---------------------------------------------------------
bus_y = loop_b + 36
tail_y = bus_y + 32

out_box, hO = card(armL_x, tail_y, AW, [
    ("title", "随访与结局评价"),
    ("en", "Follow-up & outcome assessment"),
    ("rule", ""),
    ("sub", "主要结局：术后 48 h 疼痛强度曲线下面积（AUC）"),
    ("sub", "次要结局：阿片累积用量 · 补救镇痛率 · 恢复质量"),
    ("sub", "安全性与远期：不良事件 · 慢性术后疼痛（3／6 个月）"),
], tone="a2")
stat_box, hS = card(armR_x, tail_y, AW, [
    ("title", "统计分析"),
    ("en", "Statistical analysis"),
    ("rule", ""),
    ("sub", "意向性治疗（ITT）为主，符合方案集（PP）为辅"),
    ("sub", "混合效应模型 · 协变量校正 · 多重比较控制"),
    ("sub", "预设亚组分析 · 缺失数据多重插补 · 敏感性分析"),
], tone="a2")
S.append(out_box); S.append(stat_box)
tail_h = max(hO, hS)
tail_b = tail_y + tail_h

# 两臂汇合 → 随访
S.append(elbow([(armL_c, loop_b), (armL_c, bus_y), (armL_c, tail_y - 4)], cls="conn conn-a2"))
S.append(elbow([(armR_c, arm_b), (armR_c, bus_y), (armL_c, bus_y)], cls="conn conn-ctrl", marker=None))
S.append(f'<circle cx="{armL_c:g}" cy="{bus_y:g}" r="3.6" class="junction"/>')
S.append(elbow([(armL_x + AW + 8, tail_y + tail_h / 2), (armR_x - 4, tail_y + tail_h / 2)],
               cls="conn conn-a2"))

B2_Y1 = tail_b + 36
S.insert(0, band(B2_Y0, B2_Y1, "a2"))
S.append(tab(B2_Y0, "a2", "阶段 Ⅱ · 随机对照试验",
             "PHASE II · RANDOMISED CONTROLLED TRIAL", "研究周期：约 __ 个月"))

# ---- 6. 图例与图注 -----------------------------------------------------------
leg_y = B2_Y1 + 34
lx = IX0
S.append(f'<line x1="{lx:g}" y1="{leg_y:g}" x2="{lx + 26:g}" y2="{leg_y:g}" class="conn conn-a1" marker-end="url(#ah)"/>')
S.append(T(lx + 40, leg_y + 4, "主流程", "t-leg"))
lx2 = lx + 40 + tw("主流程", 11.5) + 26
S.append(f'<line x1="{lx2:g}" y1="{leg_y:g}" x2="{lx2 + 26:g}" y2="{leg_y:g}" class="conn conn-fb" marker-end="url(#ah-fb)"/>')
S.append(T(lx2 + 40, leg_y + 4, "反馈闭环", "t-leg"))
lx3 = lx2 + 40 + tw("反馈闭环", 11.5) + 26
S.append(f'<rect x="{lx3:g}" y="{leg_y - 7:g}" width="14" height="14" rx="3" class="card card-gate"/>')
S.append(T(lx3 + 24, leg_y + 4, "阶段里程碑（Go／No-Go）", "t-leg"))
S.append(T(IX1, leg_y + 4, "下划线处 ___ 为待填写的样本量与时间参数", "t-note", "end"))

# 图注仅随独立 SVG 输出；内联到网页时由 <figcaption> 承担，避免重复
CAPTION = []
cap_y = leg_y + 34
CAPTION.append(f'<line x1="{BX0:g}" y1="{cap_y - 16:g}" x2="{BX1:g}" y2="{cap_y - 16:g}" class="hair"/>')
CAP1 = "研究总体技术路线。阶段Ⅰ（前瞻性观察队列）以 EEG 为核心的多模态神经生理信号为输入，开发并验证术后疼痛神经解码模型，"
CAP2 = "输出客观疼痛指数（OPI）并确定风险阈值；经模型锁定与 SOP 定稿后进入阶段Ⅱ（随机对照试验），比较 OPI 辅助的人机协同闭环镇痛管理"
CAP3 = "与常规管理在主要／次要结局上的差异。"
CAPTION.append(f'<text x="{BX0:g}" y="{cap_y + 6:g}" class="t-cap">'
               f'<tspan class="t-cap-b">图 1 |</tspan> {esc(CAP1)}</text>')
CAPTION.append(T(BX0, cap_y + 25, CAP2, "t-cap"))
CAPTION.append(T(BX0, cap_y + 44, CAP3, "t-cap"))

H = cap_y + 44 + 30          # 含图注（独立 SVG）
H_BODY = leg_y + 26          # 不含图注（内联网页）

# ================================================================ 样式
FONT = ('"Source Han Sans SC","Noto Sans SC","PingFang SC","Hiragino Sans GB",'
        '"Microsoft YaHei","WenQuanYi Zen Hei",-apple-system,"Segoe UI",Roboto,'
        'Helvetica,Arial,sans-serif')

TOKENS_LIGHT = """
  --f-paper:#FFFFFF; --f-ink:#12212B; --f-muted:#5D707C; --f-hair:#DAE3E8;
  --f-band1:#F2F7F9; --f-band1-line:#DCE9EE;
  --f-band2:#F5F6FA; --f-band2-line:#E0E4EE;
  --f-a1:#1C6C86; --f-a2:#2C4C7C; --f-ctrl:#68747F; --f-gate:#9A6B1E;
  --f-gate-fill:#FCF6EA; --f-gate-line:#E3CB9C;
  --f-card-line:#D5DFE5; --f-card-line2:#DCE1EC; --f-card-line3:#DEE2E6;
  --f-node:#F4F9FB; --f-node-line:#CBDFE7; --f-loop-line:#8FBFCF;
  --f-on-accent:#FFFFFF;
"""
TOKENS_DARK = """
  --f-paper:#141E26; --f-ink:#E8EFF3; --f-muted:#9DAEB9; --f-hair:#2C3A45;
  --f-band1:#101A21; --f-band1-line:#22343E;
  --f-band2:#121821; --f-band2-line:#25303F;
  --f-a1:#63B6CD; --f-a2:#8FA9DC; --f-ctrl:#9AA7B3; --f-gate:#D6AC63;
  --f-gate-fill:#231C10; --f-gate-line:#4A3B22;
  --f-card-line:#2B3B45; --f-card-line2:#2C3648; --f-card-line3:#303A42;
  --f-node:#16242C; --f-node-line:#2B4450; --f-loop-line:#3C6A7B;
  --f-on-accent:#0E1A20;
"""

RULES = f"""
.fig-root {{ font-family: {FONT}; }}
.band {{ stroke-width:1; }}
.band-a1 {{ fill:var(--f-band1); stroke:var(--f-band1-line); }}
.band-a2 {{ fill:var(--f-band2); stroke:var(--f-band2-line); }}
.card {{ fill:var(--f-paper); stroke-width:1.1; }}
.card-a1 {{ stroke:var(--f-card-line); }}
.card-a2 {{ stroke:var(--f-card-line2); }}
.card-ctrl {{ stroke:var(--f-card-line3); }}
.card-ink {{ stroke:var(--f-card-line3); }}
.card-gate {{ fill:var(--f-gate-fill); stroke:var(--f-gate-line); }}
.badge-a1 {{ fill:var(--f-a1); }}
.badge-a2 {{ fill:var(--f-a2); }}
.dot {{ }}
.dot-a1 {{ fill:var(--f-a1); }}
.dot-a2 {{ fill:var(--f-a2); }}
.dot-ctrl {{ fill:var(--f-ctrl); }}
.dot-ink {{ fill:var(--f-muted); }}
.dot-gate {{ fill:var(--f-gate); }}
.hair {{ stroke:var(--f-hair); stroke-width:1; }}
.tab {{ stroke:none; }}
.tab-a1 {{ fill:var(--f-a1); }}
.tab-a2 {{ fill:var(--f-a2); }}
.loop {{ fill:none; stroke:var(--f-loop-line); stroke-width:1.2; stroke-dasharray:5 4; }}
.node {{ fill:var(--f-node); stroke:var(--f-node-line); stroke-width:1; }}
.lbl-bg {{ fill:var(--f-band2); }}
.conn {{ stroke:var(--f-muted); stroke-width:1.6; stroke-linecap:round; }}
.conn-a1 {{ stroke:var(--f-a1); }}
.conn-a2 {{ stroke:var(--f-a2); }}
.conn-ctrl {{ stroke:var(--f-ctrl); }}
.conn-gate {{ stroke:var(--f-gate); }}
.conn-fb {{ stroke:var(--f-a1); stroke-dasharray:5 4; stroke-width:1.4; }}
.junction {{ fill:var(--f-a2); }}
.ah {{ fill:var(--f-muted); }}
.ah-fb {{ fill:var(--f-a1); }}

.t-title {{ font-size:16px; font-weight:600; fill:var(--f-ink); letter-spacing:.2px; }}
.t-en {{ font-size:11px; fill:var(--f-muted); letter-spacing:.25px; }}
.t-sub {{ font-size:12.2px; fill:var(--f-muted); }}
.t-badge {{ font-size:12.5px; font-weight:700; fill:var(--f-on-accent); letter-spacing:0; }}
.t-tab {{ font-size:14.5px; font-weight:600; fill:var(--f-on-accent); letter-spacing:.4px; }}
.t-tab-en {{ font-size:10.5px; font-weight:600; letter-spacing:.9px; }}
.tone-a1 {{ fill:var(--f-a1); }}
.tone-a2 {{ fill:var(--f-a2); }}
.t-note {{ font-size:11px; fill:var(--f-muted); }}
.t-loop {{ font-size:14px; font-weight:600; fill:var(--f-a1); letter-spacing:.2px; }}
.t-node {{ font-size:13px; font-weight:600; fill:var(--f-ink); }}
.t-node-en {{ font-size:10px; fill:var(--f-muted); }}
.t-fb {{ font-size:11px; fill:var(--f-a1); }}
.t-leg {{ font-size:11.5px; fill:var(--f-muted); }}
.t-cap {{ font-size:12.5px; fill:var(--f-muted); }}
.t-cap-b {{ font-weight:700; fill:var(--f-ink); }}
"""

DEFS = """<defs>
  <marker id="ah" viewBox="0 0 11 11" refX="10" refY="5.5" markerWidth="10"
          markerHeight="10" markerUnits="userSpaceOnUse" orient="auto">
    <path d="M0.5,1 L10,5.5 L0.5,10 L3,5.5 Z" class="ah"/>
  </marker>
  <marker id="ah-fb" viewBox="0 0 11 11" refX="10" refY="5.5" markerWidth="9"
          markerHeight="9" markerUnits="userSpaceOnUse" orient="auto">
    <path d="M0.5,1 L10,5.5 L0.5,10 L3,5.5 Z" class="ah-fb"/>
  </marker>
</defs>"""

BODY = "\n".join(x for x in S if x)
CAP = "\n".join(CAPTION)
ARIA = ("两阶段研究技术路线：阶段Ⅰ前瞻性观察队列完成多模态神经生理感知、"
        "疼痛神经解码模型开发验证与客观疼痛指数（OPI）阈值确定，"
        "经模型锁定后进入阶段Ⅱ随机对照试验，比较 OPI 辅助闭环管理与常规管理。")

# ---- 独立 SVG（浅色/印刷） ---------------------------------------------------
standalone = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:g}"
     width="{W}" height="{H:g}" class="fig-root" role="img" aria-label="{esc(ARIA)}">
<style>
svg.fig-root {{{TOKENS_LIGHT}}}
{RULES}
</style>
{DEFS}
<rect x="0" y="0" width="{W}" height="{H:g}" fill="var(--f-paper)"/>
{BODY}
{CAP}
</svg>
'''
(OUT / "study-design.svg").write_text(standalone, encoding="utf-8")

# ---- 内联片段 + 样式（供 HTML 页面使用） --------------------------------------
(OUT / "study-design.body.svg").write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H_BODY:g}" '
    f'class="fig-root" role="img" aria-label="{esc(ARIA)}">\n{DEFS}\n{BODY}\n</svg>\n',
    encoding="utf-8")

(OUT / "figure.css").write_text(
    f":root{{{TOKENS_LIGHT}}}\n"
    f"@media (prefers-color-scheme: dark){{:root:not([data-theme=\"light\"]){{{TOKENS_DARK}}}}}\n"
    f":root[data-theme=\"dark\"]{{{TOKENS_DARK}}}\n{RULES}\n",
    encoding="utf-8")

print(f"canvas {W} x {H:g}  (inline body {W} x {H_BODY:g})")
print("wrote study-design.svg / study-design.body.svg / figure.css")
