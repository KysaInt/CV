#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历 PDF 生成脚本
风格：等线体 · 灰色系 · 单栏 · 一页
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 字体 ──────────────────────────────────────────────────────────────────
FL = "DengL"   # 等线细体  —— 次要信息（软件栈、日期等淡色小字）
FR = "DengR"   # 等线      —— 正文主字体（可读性更好）
FB = "DengB"   # 等线粗体  —— 标题
pdfmetrics.registerFont(TTFont(FL, r"C:\Windows\Fonts\Dengl.ttf"))
pdfmetrics.registerFont(TTFont(FR, r"C:\Windows\Fonts\Deng.ttf"))
pdfmetrics.registerFont(TTFont(FB, r"C:\Windows\Fonts\Dengb.ttf"))

# ── 颜色 ──────────────────────────────────────────────────────────────────
C_BGD  = colors.HexColor("#242424")   # 页眉底色
C_BGST = colors.HexColor("#f0f0f0")   # 奇数行浅底
C_BGW  = colors.white
C_INK1 = colors.HexColor("#000000")   # 最深：职位名
C_INK2 = colors.HexColor("#202020")   # 正文（加深）
C_INK3 = colors.HexColor("#555555")   # 次要：软件栈、日期（加深）
C_RULE = colors.HexColor("#cccccc")
C_SEC  = colors.HexColor("#444444")   # 节标题
C_HDRT = colors.HexColor("#e0e0e0")   # 页眉浅色文字
C_LINK = colors.HexColor("#4a6fa5")

# ── 页面 ──────────────────────────────────────────────────────────────────
PW, PH = A4
ML = MR = 14 * mm
MT = 8 * mm
MB = 9 * mm
TW = PW - ML - MR

# ── 样式（正文统一用 FR 等线，保证可读性）────────────────────────────────
def S(name, font=FR, size=8.5, lead=13, color=C_INK2, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=lead, textColor=color, **kw)

ST = {
    # 页眉
    "hdr_name": S("hn", FB, 20, 26, C_HDRT),
    "hdr_info": S("hi", FR, 8.5, 15, C_HDRT),   # 行间距宽松
    # 节标题
    "sec":      S("sc", FB, 9, 13, C_SEC, spaceBefore=3, spaceAfter=1),
    "sec_intro":S("sci", FB, 10.5, 14, C_INK1, spaceBefore=3, spaceAfter=1),
    # 简介正文
    "intro":    S("in", FR, 8.5, 11.5, C_INK2, spaceAfter=2, alignment=4, wordWrap="CJK"),
    # 经历
    "jt":       S("jt", FB, 9,  12, C_INK1),
    "date":     S("dt", FR, 8,  12, C_INK3, alignment=2),
    "co":       S("co", FR, 8,  12, C_INK3),
    "sw":       S("sw", FR, 7.5, 11, C_INK3),
    "bullet":   S("b",  FR, 8.5, 11.5, C_INK2, leftIndent=10),
    # 教育
    "edu_hdr":  S("eh", FB, 8.5, 13, C_HDRT),
    "edu_cell": S("ec", FR, 8.5, 11.5, C_INK2),
    # 作品集
    "port_desc":S("pd", FR, 8,  13, C_INK3, leftIndent=5),
    "port_url": S("pu", FR, 8.5, 13, C_LINK, leftIndent=5),
    "port_note":S("pn", FR, 8,  13, C_INK3),
}

# ── 内容区宽度（外层 row_tbl 左右各 8pt padding）────────────────────────
INNER_W = TW - 16   # 8*2 = 16pt

# ── 数据 ──────────────────────────────────────────────────────────────────────

# 个人简介（拆分为两段，避免单段内 br 导致的留白不均）
INTRO_P1 = (
    "从事三维可视化与视频制作约七年, 早期有插画实习经历 (熟悉 Photoshop 和手绘板操作, 具备基础绘画能力), "
    "随后在武汉东湖装饰 (2017-2019) 以 AutoCAD 施工图, 3ds Max 建模, V-Ray 渲染完成工装效果图制作. "
    "近几年工作重心转向产品与动态场景表达, 目前主要使用 <b>Rhino</b> 建模, <b>Cinema 4D</b> 进行批量出图与动画制作, "
    "并结合 <b>Grasshopper</b> 处理参数化需求. 渲染器长期以 <b>V-Ray</b> 为主, 对 <b>Enscape / Blender / OC / Redshift</b> 也有实践经验. "
    "在 <b>Unreal Engine 4/5</b> 实时场景和 <b>After Effects</b> 后期合成方面有实际项目落地经验. "
    "具备 <b>Python</b> 基础, 会在日常制作中编写脚本提升效率, 习惯用程序思维拆解问题, 也会通过与 AI 沟通持续补充方法库. "
    "长期建模与渲染实践让我在灯光控制, 模型细节, CMF 与色彩关系上形成稳定判断, 在电商项目中也会结合转化和盈利目标做视觉取舍."
)

INTRO_P2 = (
    "学习上保持长期迭代, 有需要时会通过代理工具到外网查文档和视频. 2022-2023 年集中研究 C4D 动画技法, "
    "并搭建本地 Stable Diffusion / ComfyUI 工作流; 2024-2025 年完成 UE5 蓝图项目与 Babylon.js Web3D 展示页面. "
    "对 UE 蓝图, Grasshopper, C4D Xpresso 等节点化程序设计有持续实践, 日常会结合 Copilot 辅助脚本开发和工具化整理. "
    "平时有稳定观影习惯, 会关注镜头语言, 音频音效与整体节奏的设计方式, 这些也会反哺到视觉与视频表达中. "
    "工作状态偏独立和专注, 沟通直接, 但配合意识稳定."
)

# 工作经历（儿童插画 & 东湖装饰已并入简介）
EXP = [
    {
        "title":   "展厅 / 家具产品建模渲染",
        "company": "上海木里木外实业有限公司",
        "date":    "2020.05 - 2021.04",
        "sw":      "SketchUp / 3ds Max / V-Ray / Rhino / Cinema 4D",
        "bullets": [
            "负责展厅空间搭建与家具模型制作, 以 3ds Max + V-Ray 完成产品表现图输出.",
            "阶段内开始自学 Rhino 与 C4D, 为后续曲面建模和动画表达打基础.",
        ],
    },
    {
        "title":   "艺术装置 / 参数化建模",
        "company": "上海伍鼎景观设计咨询有限公司",
        "date":    "2021.05 - 2022.04",
        "sw":      "Rhino / Grasshopper / Enscape / V-Ray / Cinema 4D",
        "bullets": [
            "负责曲面景观雕塑与 IP 形象建模, 配合 Enscape / V-Ray 完成方案可视化表达.",
            "将 Grasshopper 参数化逻辑逐步引入项目, 提升复杂形体的建模效率与可控性.",
        ],
    },
    {
        "title":   "动态虚拟直播场景设计",
        "company": "杭州青缇智能有限公司",
        "date":    "2023.05 - 2024.01",
        "sw":      "Rhino / Cinema 4D / X-Particles / Unreal Engine 4 / AE / PS",
        "bullets": [
            "参与 XR 虚拟直播项目, 负责从 Rhino 建模, C4D 动画到 UE4 实时播出的整段场景制作流程.",
            "与导播协作搭建可切换交互场景, 并用 AE / PS 完成直播贴片与包装素材.",
        ],
    },
    {
        "title":   "产品主图 / 动画设计制作",
        "company": "杭州顺颂商祺科技有限公司",
        "date":    "2024.03 - 2024.08",
        "sw":      "Cinema 4D / Rhino / V-Ray / After Effects",
        "bullets": [
            "整理电商产品图出图规范与场次模板, 在 C4D 中实现不同型号的批量高效输出.",
            "独立完成产品宣传动画, 覆盖建模, 灯光材质, 后期合成与音效处理全流程.",
            "制作安装说明视频, 重点保证步骤清晰度与信息传达效率.",
        ],
    },
    {
        "title":   "产品动画设计",
        "company": "武汉理理线科技有限公司",
        "date":    "2025.05 - 2026.02",
        "sw":      "Cinema 4D / Rhino / Grasshopper / After Effects / Python",
        "bullets": [
            "围绕产品卖点制作安装说明与功能介绍视频, 同步完成相关模型修改与优化.",
            "负责后期包装环节, 包含音乐音效匹配, 口播字幕整理和整体节奏统一.",
            "编写 Python 脚本辅助渲染流程, 并沉淀 Grasshopper 参数化复用组件用于重复场景.",
        ],
    },
]

EDU = [
    ("湖北生态工程学院", "室内设计施工与管理 (大专)",      "2013 - 2016"),
    ("武汉科技大学",     "视觉传达与设计 (本科, 非全日制)", "2017 - 2021"),
]

PORTFOLIO_URL  = "https://kysaint.github.io/CV/"
PORTFOLIO_DESC = "全时期作品归档: 三维 / 动画 / UE5 / Web3D / Python 音乐程序"
PORTFOLIO_NOTE = (
    "作品集托管于 GitHub Pages, 电脑端访问可能需要代理工具; "
    "如遇无法加载, 建议切换手机移动网络 (4G / 5G) 直接访问."
)


# ── 辅助函数 ──────────────────────────────────────────────────────────────
def sec_heading(text):
    return [
        Paragraph(text, ST["sec"]),
        HRFlowable(width="100%", thickness=0.4, color=C_RULE,
                   spaceBefore=1, spaceAfter=4),
    ]


def exp_block(e):
    title_row = Table(
        [[Paragraph(e["title"], ST["jt"]),
          Paragraph(e["date"],  ST["date"])]],
        colWidths=[INNER_W * 0.60, INNER_W * 0.40],
    )
    title_row.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "BOTTOM"),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))

    items = [title_row,
             Paragraph(e["company"], ST["co"]),
             Paragraph(e["sw"],      ST["sw"]),
             Spacer(1, 2)]
    for b in e["bullets"]:
        items.append(Paragraph(f"- {b}", ST["bullet"]))
    return items


# ── 主构建 ────────────────────────────────────────────────────────────────
def build_pdf(output_path: str):
    story = []

    # ── 页眉（宽松间距，不紧凑）─────────────────────────────────────────
    name_para = Paragraph(
        f'<font name="{FB}" size="19" color="#e0e0e0">祝志野</font>'
        f'<font name="{FR}" size="8.5" color="#909090"> 三维动画 / 产品视觉设计</font>',
        ST["hdr_info"]
    )
    info_para = Paragraph(
        "电话: 15900765489 | 生日: 1995/05/05 | 籍贯: 湖北武汉",
        ST["hdr_info"]
    )

    hdr_inner = [
        Spacer(1, 3),
        name_para,
        Spacer(1, 6),    # 姓名与信息行之间留有呼吸
        info_para,
        Spacer(1, 3),
    ]
    hdr = Table([[hdr_inner]], colWidths=[TW])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_BGD),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 5))

    # ── 个人简介 ─────────────────────────────────────────────────────────
    story.append(Paragraph("个人简介", ST["sec_intro"]))
    story.append(HRFlowable(width="100%", thickness=0.4, color=C_RULE,
                            spaceBefore=1, spaceAfter=4))
    story.append(Paragraph(INTRO_P1, ST["intro"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(INTRO_P2, ST["intro"]))
    story.append(Spacer(1, 2))

    # ── 工作经历 ─────────────────────────────────────────────────────────
    story += sec_heading("工作经历")
    for idx, e in enumerate(EXP):
        bg = C_BGST if idx % 2 == 0 else C_BGW
        row_tbl = Table([[exp_block(e)]], colWidths=[TW])
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("LINEBELOW",     (0,0),(-1,-1), 0.3, C_RULE),
        ]))
        story.append(row_tbl)

    story.append(Spacer(1, 4))

    # ── 教育经历 ─────────────────────────────────────────────────────────
    story += sec_heading("教育经历")
    edu_data = [
        [Paragraph(h, ST["edu_hdr"]) for h in ["学校", "专业", "时间"]],
    ] + [
        [Paragraph(s, ST["edu_cell"]),
         Paragraph(m, ST["edu_cell"]),
         Paragraph(p, ST["edu_cell"])]
        for s, m, p in EDU
    ]
    edu_tbl = Table(edu_data, colWidths=[TW*0.28, TW*0.52, TW*0.20])
    edu_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  C_BGD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_BGST, C_BGW]),
        ("FONTNAME",      (0,0),(-1,-1), FR),
        ("FONTSIZE",      (0,0),(-1,-1), 8.5),
        ("LEADING",       (0,0),(-1,-1), 13),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("GRID",          (0,0),(-1,-1), 0.3, C_RULE),
    ]))
    story.append(edu_tbl)
    story.append(Spacer(1, 4))

    # ── 作品集（仅 GitHub Pages）─────────────────────────────────────────
    story += sec_heading("作品集")
    story.append(Paragraph(
        f'作品集主页 (GitHub Pages) - <b>全时期作品</b> <font color="#555555">{PORTFOLIO_DESC}</font>',
        ST["port_desc"]
    ))
    story.append(Paragraph(
        f'<a href="{PORTFOLIO_URL}" color="#4a6fa5">{PORTFOLIO_URL}</a>',
        ST["port_url"]
    ))
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width="100%", thickness=0.3, color=C_RULE,
                            spaceBefore=1, spaceAfter=4))
    story.append(Paragraph(PORTFOLIO_NOTE, ST["port_note"]))

    # ── 输出 ─────────────────────────────────────────────────────────────
    doc = BaseDocTemplate(
        output_path, pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT,  bottomMargin=MB,
        title="祝志野_简历_2026", author="祝志野",
    )
    frame = Frame(ML, MB, TW, PH - MT - MB, id="body",
                  leftPadding=0, rightPadding=0,
                  topPadding=0,  bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    doc.build(story)
    size_kb = os.path.getsize(output_path) // 1024
    print(f"[OK] {output_path}  ({size_kb} KB)")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PDF", "CV_2026.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build_pdf(out)
