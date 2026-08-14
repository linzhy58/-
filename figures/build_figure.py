#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《基于EEG多模态融合的术后镇痛闭环管理系统研发与临床验证》研究技术路线图。

按 A4 版心排版：页宽 210 mm、左右页边距各 31.75 mm → 版心宽 146.5 mm。
坐标系 1 px = 0.1 mm，故画布宽固定 1465 px；字号 px ÷ 3.528 = pt。
图内最小字号 28 px ≈ 7.9 pt，插入 Word 按 100% 宽度放置即为该实际字号。

输出：
  study-design.svg        黑白版（默认，申请书用，独立矢量图）
  study-design-color.svg  彩色版（同一版式，用于汇报／投稿）
  study-design.body.svg   SVG 片段（供网页内联）
  figure.css              网页内联版样式
用法：python3 build_figure.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

# ============================================================ 画布与栅格（0.1 mm/px）
W = 1465                    # 设计栅格宽（无量纲）
PLACE_MM = 165.3            # 插入申请书时的排版宽度：正文单元格可用宽 9372 twips
M = 40
BX0, BX1 = M, W - M         # 泳道边界
IX0, IX1 = BX0 + 30, BX1 - 30   # 泳道内容边界
CX = W / 2
INNER = IX1 - IX0           # 1325

# 排印节奏
PAD_TOP, PAD_BOT = 44, 30
ADV_TITLE, ADV_SUB, ADV_RULE = 44, 38, 32
PAD_L, DOT_L, SUB_L, BADGE_L = 26, 26, 38, 70

WARN = []                   # 文本溢出告警

# ============================================================ 文本工具
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tw(text, size):
    """估算文本宽度：CJK 1.0 em，拉丁 0.55 em，空格 0.3 em。"""
    w = 0.0
    for ch in text:
        if ch == " ":
            w += 0.30
        elif ord(ch) > 0x2E80:
            w += 1.0
        else:
            w += 0.55
    return w * size

def fit(text, size, avail, where):
    """记录溢出，便于改文案时立即发现。"""
    got = tw(text, size)
    if got > avail:
        WARN.append(f"  溢出 {got - avail:5.0f}px  [{where}] {text}")
    return text

def T(x, y, text, cls, anchor="start"):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x:g}" y="{y:g}" class="{cls}"{a}>{esc(text)}</text>'

# ============================================================ 圆角折线
def elbow(pts, r=22, cls="conn", marker="ah"):
    pts = [(float(a), float(b)) for a, b in pts]
    d = [f"M{pts[0][0]:g},{pts[0][1]:g}"]
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        d1x, d1y, d2x, d2y = x1 - x0, y1 - y0, x2 - x1, y2 - y1
        l1 = (d1x ** 2 + d1y ** 2) ** 0.5 or 1
        l2 = (d2x ** 2 + d2y ** 2) ** 0.5 or 1
        rr = min(r, l1 / 2, l2 / 2)
        ax, ay = x1 - d1x / l1 * rr, y1 - d1y / l1 * rr
        bx, by = x1 + d2x / l2 * rr, y1 + d2y / l2 * rr
        sweep = 1 if d1x * d2y - d1y * d2x > 0 else 0
        d.append(f"L{ax:g},{ay:g}")
        d.append(f"A{rr:g},{rr:g} 0 0 {sweep} {bx:g},{by:g}")
    d.append(f"L{pts[-1][0]:g},{pts[-1][1]:g}")
    mk = f' marker-end="url(#{marker})"' if marker else ""
    return f'<path d="{" ".join(d)}" class="{cls}" fill="none"{mk}/>'

def vline(x, y0, y1, cls="conn", marker="ah"):
    return elbow([(x, y0), (x, y1)], cls=cls, marker=marker)

# ============================================================ 卡片
def measure(items):
    b, last = PAD_TOP, PAD_TOP
    for kind, _ in items:
        if kind == "title":
            last = b; b += ADV_TITLE
        elif kind == "sub":
            last = b; b += ADV_SUB
        elif kind == "rule":
            b += ADV_RULE
    return last + PAD_BOT

def card(x, y, w, items, tone="a1", align="left", badge=None, name=""):
    h = measure(items)
    tx = x + (BADGE_L if badge else PAD_L) if align == "left" else x + w / 2
    anchor = "start" if align == "left" else "middle"
    t_avail = (w - (BADGE_L if badge else PAD_L) - PAD_L) if align == "left" else w - 2 * PAD_L
    s_avail = (w - SUB_L - PAD_L) if align == "left" else w - 2 * PAD_L
    out = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="16" '
           f'class="card card-{tone}"/>']
    b = y + PAD_TOP
    for kind, text in items:
        if kind == "title":
            fit(text, 33, t_avail, name)
            out.append(T(tx, b, text, "t-title", anchor)); b += ADV_TITLE
        elif kind == "rule":
            out.append(f'<line x1="{x + PAD_L:g}" y1="{b - 13:g}" x2="{x + w - PAD_L:g}" '
                       f'y2="{b - 13:g}" class="hair"/>'); b += ADV_RULE
        elif kind == "sub":
            fit(text, 28, s_avail, name)
            if align == "left":
                out.append(f'<rect x="{x + DOT_L:g}" y="{b - 18:g}" width="9" height="9" '
                           f'class="dot dot-{tone}"/>')
                out.append(T(x + SUB_L, b, text, "t-sub"))
            else:
                out.append(T(tx, b, text, "t-sub", anchor))
            b += ADV_SUB
    if badge:
        cxb, cyb = x + 34, y + PAD_TOP - 10
        out.append(f'<circle cx="{cxb:g}" cy="{cyb:g}" r="24" class="badge badge-{tone}"/>')
        out.append(T(cxb, cyb + 10, badge, "t-badge", "middle"))
    return "\n".join(out), h

def band(y0, y1, tone):
    return (f'<rect x="{BX0:g}" y="{y0:g}" width="{BX1 - BX0:g}" height="{y1 - y0:g}" '
            f'rx="26" class="band band-{tone}"/>')

def tab(y_edge, tone, cn, note=""):
    h, pad = 62, 34
    w = tw(cn, 32) + pad * 2
    x, y = BX0 + 30, y_edge - h / 2
    s = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{h / 2:g}" '
         f'class="tab tab-{tone}"/>',
         T(x + pad, y + h / 2 + 11, cn, "t-tab")]
    if note:
        s.append(T(IX1, y + h / 2 + 9, note, "t-note", "end"))
    return "\n".join(s)

# ============================================================ 内容（均取自申请书原文）
S = []

# ---- 入组 ---------------------------------------------------------------
entry_y, ENTRY_W = 28, 780
entry, entry_h = card(CX - ENTRY_W / 2, entry_y, ENTRY_W, [
    ("title", "术前筛选与知情同意"),
    ("rule", ""),
    ("sub", "择期腹腔镜结直肠手术、术后静脉PCA、ASA I–III级"),
], tone="ink", align="center", name="入组")
S.append(entry)
entry_b = entry_y + entry_h

# ---- 阶段Ⅰ ---------------------------------------------------------------
B1_Y0 = entry_b + 36
box1_y = B1_Y0 + 80

P1 = [(["EEG为核心的", "多模态神经生理感知"],
       ["EEG＋ECG/PPG＋呼吸信号", "PACU至病房连续监测24 h"]),
      (["术后疼痛神经解码", "模型开发与验证"],
       ["EEG特征＋HRV／呼吸指标", "患者级内部＋时间外验证"]),
      (["客观疼痛指数（OPI）", "与风险阈值确定"],
       ["连续输出0–100分指数", "中重度活动痛风险提示"])]

GAP1 = 36
BW = (INNER - 2 * GAP1) / 3
p1 = []
for i, (titles, subs) in enumerate(P1):
    x = IX0 + i * (BW + GAP1)
    items = [("title", titles[0]), ("title", titles[1]), ("rule", "")]
    items += [("sub", s) for s in subs]
    frag, h = card(x, box1_y, BW, items, tone="a1", badge=str(i + 1), name=f"阶段Ⅰ-{i+1}")
    p1.append((x, x + BW, h))
    S.append(frag)

box1_h = max(b[2] for b in p1)
box1_b = box1_y + box1_h
B1_Y1 = box1_b + 40
S.insert(0, band(B1_Y0, B1_Y1, "a1"))
S.insert(1, tab(B1_Y0, "a1", "阶段Ⅰ · 前瞻性观察队列", "第4–12个月 · 最多约120例"))

for i in range(2):                       # ①→②→③
    ym = box1_y + box1_h / 2
    S.append(elbow([(p1[i][1] + 6, ym), (p1[i + 1][0] - 8, ym)], cls="conn conn-a1"))

c1 = (p1[0][0] + p1[0][1]) / 2
S.append(elbow([(CX, entry_b), (CX, B1_Y0 + 56), (c1, B1_Y0 + 56), (c1, box1_y - 8)],
               cls="conn"))

# ---- 里程碑 ---------------------------------------------------------------
GATE_W = 900
gate_y = B1_Y1 + 44
gate, gate_h = card(CX - GATE_W / 2, gate_y, GATE_W, [
    ("title", "里程碑：模型、风险阈值与SOP锁定"),
    ("sub", "阶段Ⅰ模型不参与临床决策；锁定参数、阈值、提示规则与软件版本"),
], tone="gate", align="center", name="里程碑")
S.append(gate)
gate_b = gate_y + gate_h

c3 = (p1[2][0] + p1[2][1]) / 2
S.append(elbow([(c3, box1_b), (c3, B1_Y1 + 26), (CX, B1_Y1 + 26), (CX, gate_y - 8)],
               cls="conn conn-gate"))

# ---- 阶段Ⅱ ---------------------------------------------------------------
B2_Y0 = gate_b + 36
RAND_W = 820
rand_y = B2_Y0 + 80
S.append(vline(CX, gate_b, rand_y - 8, cls="conn"))
rand, rand_h = card(CX - RAND_W / 2, rand_y, RAND_W, [
    ("title", "随机分组（1:1）"),
    ("rule", ""),
    ("sub", "变动区组随机、分配隐藏；结局评估与统计分析盲态"),
    ("sub", "两组均接受标准多模式镇痛、静脉PCA与相同监测"),
], tone="a2", align="center", name="随机分组")
S.append(rand)
rand_b = rand_y + rand_h

GAP2 = 60
AW = (INNER - GAP2) / 2
armL_x, armR_x = IX0, IX0 + AW + GAP2
armL_c, armR_c = armL_x + AW / 2, armR_x + AW / 2
arm_y = rand_b + 78

armL, hL = card(armL_x, arm_y, AW, [
    ("title", "客观疼痛指数（OPI）辅助组"),
    ("rule", ""),
    ("sub", "约60例；开放锁定模型的指数与提示"),
    ("sub", "达阈值触发人机协同闭环（见下）"),
], tone="a2", name="试验组")
armR, hR = card(armR_x, arm_y, AW, [
    ("title", "常规管理组"),
    ("rule", ""),
    ("sub", "约60例；间断NRS评估与APS管理"),
    ("sub", "不开放客观疼痛指数结果"),
], tone="ctrl", name="对照组")
S += [armL, armR]
arm_b = arm_y + max(hL, hR)

split_y = rand_b + 44
S.append(elbow([(CX, rand_b), (CX, split_y), (armL_c, split_y), (armL_c, arm_y - 8)],
               cls="conn conn-a2"))
S.append(elbow([(CX, rand_b), (CX, split_y), (armR_c, split_y), (armR_c, arm_y - 8)],
               cls="conn conn-ctrl"))

# ---- 人机协同闭环 ---------------------------------------------------------
loop_y = arm_b + 42
LOOP_H = 240
S.append(f'<rect x="{armL_x:g}" y="{loop_y:g}" width="{AW:g}" height="{LOOP_H:g}" '
         f'rx="16" class="loop"/>')
S.append(T(armL_x + PAD_L, loop_y + 52, "神经解码驱动的人机协同闭环", "t-loop"))
S.append(elbow([(armL_c, arm_b), (armL_c, loop_y - 8)], cls="conn conn-a1"))

NODES = ["风险提示", "限时复评", "镇痛处置", "效果评价"]
NGAP, n_pad = 20, 16
NW = (AW - 2 * n_pad - 3 * NGAP) / 4
node_y, node_h = loop_y + 84, 78
ctr = []
for i, cn in enumerate(NODES):
    nx = armL_x + n_pad + i * (NW + NGAP)
    nc = nx + NW / 2
    ctr.append(nc)
    fit(cn, 28, NW - 14, "闭环节点")
    S.append(f'<rect x="{nx:g}" y="{node_y:g}" width="{NW:g}" height="{node_h:g}" '
             f'rx="12" class="node"/>')
    S.append(T(nc, node_y + node_h / 2 + 10, cn, "t-node", "middle"))
    if i:
        S.append(elbow([(ctr[i - 1] + NW / 2 + 5, node_y + node_h / 2),
                        (nx - 7, node_y + node_h / 2)], cls="conn conn-a1", r=8))

fb_y = node_y + node_h + 44
S.append(elbow([(ctr[-1], node_y + node_h), (ctr[-1], fb_y), (ctr[0], fb_y),
                (ctr[0], node_y + node_h + 8)], cls="conn conn-fb", marker="ah-fb", r=16))
FB = "记录与再评估"
fw = tw(FB, 25) + 26
S.append(f'<rect x="{armL_c - fw / 2:g}" y="{fb_y - 20:g}" width="{fw:g}" height="36" '
         f'class="lbl-bg"/>')
S.append(T(armL_c, fb_y + 9, FB, "t-fb", "middle"))
loop_b = loop_y + LOOP_H

# ---- 随访与统计 -----------------------------------------------------------
bus_y = loop_b + 42
tail_y = bus_y + 40
out_c, hO = card(armL_x, tail_y, AW, [
    ("title", "随访与结局评价（术后48 h）"),
    ("rule", ""),
    ("sub", "主要终点：0–24 h活动痛NRS时间加权均值"),
    ("sub", "次要：阿片用量、处置时效、不良事件"),
], tone="a2", name="随访")
stat_c, hS = card(armR_x, tail_y, AW, [
    ("title", "统计分析"),
    ("rule", ""),
    ("sub", "意向性分析为主，辅以符合方案集"),
    ("sub", "ANCOVA／线性混合效应模型"),
], tone="a2", name="统计")
S += [out_c, stat_c]
tail_b = tail_y + max(hO, hS)

S.append(elbow([(armL_c, loop_b), (armL_c, tail_y - 8)], cls="conn conn-a2"))
S.append(elbow([(armR_c, arm_b), (armR_c, bus_y), (armL_c, bus_y)],
               cls="conn conn-ctrl", marker=None))
S.append(f'<circle cx="{armL_c:g}" cy="{bus_y:g}" r="8" class="junction"/>')
S.append(elbow([(armL_x + AW + 6, tail_y + max(hO, hS) / 2),
                (armR_x - 8, tail_y + max(hO, hS) / 2)], cls="conn conn-a2"))

B2_Y1 = tail_b + 40
S.insert(0, band(B2_Y0, B2_Y1, "a2"))
S.append(tab(B2_Y0, "a2", "阶段Ⅱ · 随机对照试验", "第13–21个月 · 120例，1:1"))

H = B2_Y1 + 30

# ============================================================ 样式
FONT = ('"Source Han Sans SC","Noto Sans SC","PingFang SC","Hiragino Sans GB",'
        '"Microsoft YaHei","WenQuanYi Zen Hei",-apple-system,"Segoe UI",Arial,sans-serif')

BW_LIGHT = """
  --f-paper:#FFFFFF; --f-ink:#000000; --f-muted:#333333; --f-note:#555555;
  --f-hair:#C4C4C4; --f-band1:#EFEFEF; --f-band1-line:#CFCFCF;
  --f-band2:#F7F7F7; --f-band2-line:#D7D7D7;
  --f-a1:#111111; --f-a2:#4A4A4A; --f-ctrl:#8A8A8A; --f-gate:#000000;
  --f-gate-fill:#E3E3E3; --f-gate-line:#5A5A5A;
  --f-card-line:#8C8C8C; --f-card-line2:#3C3C3C; --f-card-line3:#A8A8A8;
  --f-node:#F2F2F2; --f-node-line:#9A9A9A; --f-loop-line:#5A5A5A;
  --f-conn:#333333; --f-on-accent:#FFFFFF;
"""
BW_DARK = """
  --f-paper:#14181B; --f-ink:#F2F4F5; --f-muted:#C4CACD; --f-note:#A6ADB1;
  --f-hair:#3A4145; --f-band1:#1E2427; --f-band1-line:#333A3E;
  --f-band2:#181D20; --f-band2-line:#2C3336;
  --f-a1:#E8ECEE; --f-a2:#B9C0C4; --f-ctrl:#7E878C; --f-gate:#F2F4F5;
  --f-gate-fill:#2A3033; --f-gate-line:#6B7479;
  --f-card-line:#4A5256; --f-card-line2:#8B9498; --f-card-line3:#3E4549;
  --f-node:#1E2427; --f-node-line:#4A5256; --f-loop-line:#798388;
  --f-conn:#C4CACD; --f-on-accent:#14181B;
"""
COLOR_LIGHT = """
  --f-paper:#FFFFFF; --f-ink:#12212B; --f-muted:#48606D; --f-note:#5D707C;
  --f-hair:#DAE3E8; --f-band1:#F2F7F9; --f-band1-line:#DCE9EE;
  --f-band2:#F5F6FA; --f-band2-line:#E0E4EE;
  --f-a1:#1C6C86; --f-a2:#2C4C7C; --f-ctrl:#68747F; --f-gate:#9A6B1E;
  --f-gate-fill:#FCF6EA; --f-gate-line:#E3CB9C;
  --f-card-line:#D5DFE5; --f-card-line2:#B9C4DA; --f-card-line3:#DEE2E6;
  --f-node:#F4F9FB; --f-node-line:#CBDFE7; --f-loop-line:#8FBFCF;
  --f-conn:#48606D; --f-on-accent:#FFFFFF;
"""
COLOR_DARK = """
  --f-paper:#141E26; --f-ink:#E8EFF3; --f-muted:#B4C4CE; --f-note:#9DAEB9;
  --f-hair:#2C3A45; --f-band1:#101A21; --f-band1-line:#22343E;
  --f-band2:#121821; --f-band2-line:#25303F;
  --f-a1:#63B6CD; --f-a2:#8FA9DC; --f-ctrl:#9AA7B3; --f-gate:#D6AC63;
  --f-gate-fill:#231C10; --f-gate-line:#4A3B22;
  --f-card-line:#2B3B45; --f-card-line2:#3B4A63; --f-card-line3:#303A42;
  --f-node:#16242C; --f-node-line:#2B4450; --f-loop-line:#3C6A7B;
  --f-conn:#B4C4CE; --f-on-accent:#0E1A20;
"""

RULES = f"""
.fig-root {{ font-family: {FONT}; }}
.band {{ stroke-width:2.2; }}
.band-a1 {{ fill:var(--f-band1); stroke:var(--f-band1-line); }}
.band-a2 {{ fill:var(--f-band2); stroke:var(--f-band2-line); }}
.card {{ fill:var(--f-paper); stroke-width:2.4; }}
.card-a1 {{ stroke:var(--f-card-line); }}
.card-a2 {{ stroke:var(--f-card-line2); stroke-width:3; }}
.card-ctrl {{ stroke:var(--f-card-line3); }}
.card-ink {{ stroke:var(--f-card-line); }}
.card-gate {{ fill:var(--f-gate-fill); stroke:var(--f-gate-line); stroke-width:3; }}
.badge-a1 {{ fill:var(--f-a1); }}
.badge-a2 {{ fill:var(--f-a2); }}
.dot-a1 {{ fill:var(--f-a1); }}
.dot-a2 {{ fill:var(--f-a2); }}
.dot-ctrl {{ fill:var(--f-ctrl); }}
.dot-ink {{ fill:var(--f-muted); }}
.dot-gate {{ fill:var(--f-gate); }}
.hair {{ stroke:var(--f-hair); stroke-width:2; }}
.tab {{ stroke:none; }}
.tab-a1 {{ fill:var(--f-a1); }}
.tab-a2 {{ fill:var(--f-a2); }}
.loop {{ fill:none; stroke:var(--f-loop-line); stroke-width:2.6; stroke-dasharray:11 9; }}
.node {{ fill:var(--f-node); stroke:var(--f-node-line); stroke-width:2; }}
.lbl-bg {{ fill:var(--f-band2); }}
.junction {{ fill:var(--f-conn); }}
.conn {{ stroke:var(--f-conn); stroke-width:3.4; stroke-linecap:round; }}
.conn-a1, .conn-a2, .conn-gate {{ stroke:var(--f-conn); }}
.conn-ctrl {{ stroke:var(--f-ctrl); }}
.conn-fb {{ stroke:var(--f-loop-line); stroke-width:2.8; stroke-dasharray:11 9; }}
.ah {{ fill:var(--f-conn); }}
.ah-fb {{ fill:var(--f-loop-line); }}

.t-title {{ font-size:33px; font-weight:700; fill:var(--f-ink); }}
.t-sub {{ font-size:28px; fill:var(--f-muted); }}
.t-badge {{ font-size:28px; font-weight:700; fill:var(--f-on-accent); }}
.t-tab {{ font-size:32px; font-weight:700; fill:var(--f-on-accent); letter-spacing:.6px; }}
.t-note {{ font-size:26px; fill:var(--f-note); }}
.t-loop {{ font-size:30px; font-weight:700; fill:var(--f-ink); }}
.t-node {{ font-size:28px; font-weight:700; fill:var(--f-ink); }}
.t-fb {{ font-size:25px; fill:var(--f-note); }}
"""

DEFS = """<defs>
  <marker id="ah" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="22" markerHeight="22"
          markerUnits="userSpaceOnUse" orient="auto">
    <path d="M0.5,1 L11,6 L0.5,11 L3.2,6 Z" class="ah"/>
  </marker>
  <marker id="ah-fb" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="20" markerHeight="20"
          markerUnits="userSpaceOnUse" orient="auto">
    <path d="M0.5,1 L11,6 L0.5,11 L3.2,6 Z" class="ah-fb"/>
  </marker>
</defs>"""

BODY = "\n".join(x for x in S if x)
ARIA = ("研究技术路线：阶段Ⅰ前瞻性观察队列完成多模态神经生理感知、疼痛神经解码模型开发验证与"
        "客观疼痛指数风险阈值确定，经模型锁定与SOP定稿后进入阶段Ⅱ随机对照试验，"
        "比较客观疼痛指数辅助的人机协同闭环管理与常规管理。")

def write_svg(path, tokens):
    (OUT / path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:g}" '
        f'width="{W}" height="{H:g}" class="fig-root" role="img" aria-label="{esc(ARIA)}">\n'
        f'<style>\nsvg.fig-root {{{tokens}}}\n{RULES}\n</style>\n{DEFS}\n'
        f'<rect x="0" y="0" width="{W}" height="{H:g}" fill="var(--f-paper)"/>\n{BODY}\n</svg>\n',
        encoding="utf-8")

write_svg("study-design.svg", BW_LIGHT)          # 申请书用（黑白）
write_svg("study-design-color.svg", COLOR_LIGHT)  # 汇报／投稿用（彩色）

(OUT / "study-design.body.svg").write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:g}" '
    f'class="fig-root" role="img" aria-label="{esc(ARIA)}">\n{DEFS}\n{BODY}\n</svg>\n',
    encoding="utf-8")

(OUT / "figure.css").write_text(
    f":root{{{BW_LIGHT}}}\n"
    f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{BW_DARK}}}}}\n'
    f':root[data-theme="dark"]{{{BW_DARK}}}\n{RULES}\n', encoding="utf-8")

k = PLACE_MM / W
print(f"画布 {W} x {H:g}  →  排版 {W * k:.1f} x {H * k:.1f} mm"
      f"（正文可用宽 {PLACE_MM} mm，版心高 246.2 mm）")
print(f"印刷字号：正文 {28 * k / 0.3528:.1f} pt，标题 {33 * k / 0.3528:.1f} pt，泳道标签 {32 * k / 0.3528:.1f} pt")
print("\n".join(WARN) if WARN else "文本宽度检查：全部通过")
