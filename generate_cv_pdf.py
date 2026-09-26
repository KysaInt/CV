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
    "sec":      S("sc", FB, 10.5, 14, C_SEC, spaceBefore=3, spaceAfter=1),
    "sec_intro":S("sci", FB, 10.5, 14, C_SEC, spaceBefore=3, spaceAfter=1),
    # 简介正文
    "intro":    S("in", FR, 9, 12.5, C_INK2, spaceAfter=2, alignment=4, wordWrap="CJK"),
    # 经历
    "jt":       S("jt", FB, 9,  12, C_INK1),
    "date":     S("dt", FR, 8,  12, C_INK3, alignment=2),
    "co":       S("co", FR, 8,  12, C_INK3),
    "sw":       S("sw", FR, 7.5, 11, C_INK3),
    "bullet":   S("b",  FR, 8.5, 11.5, C_INK2, leftIndent=10),
    "exp_title":S("et", FB, 7.7, 9.5, C_INK1),
    "exp_meta": S("em", FR, 7.0, 9.0, C_INK3),
    "exp_sum":  S("es", FR, 7.5, 10.0, C_INK2),
    "exp_hdr":  S("exh", FB, 8, 10.5, C_HDRT),
    "exp_cell": S("exc", FR, 8, 10.5, C_INK2),
    # 教育
    "edu_hdr":  S("eh", FB, 9, 13, C_HDRT),
    "edu_cell": S("ec", FR, 9, 12, C_INK2),
    # 作品集
    "port_desc":S("pd", FR, 9,  13, C_INK3, leftIndent=5),
    "port_url": S("pu", FR, 14, 18, C_LINK, leftIndent=5),
    "port_note":S("pn", FR, 8.5, 12, C_INK3),
}

# ── 内容区宽度（外层 row_tbl 左右各 8pt padding）────────────────────────
INNER_W = TW - 16   # 8*2 = 16pt

# ── 数据 ──────────────────────────────────────────────────────────────────────

# 个人简介
INTRO = (
    "从事三维可视化、产品表现与动画制作约七年. 熟悉 <b>Rhino</b> 建模、<b>Cinema 4D</b> 动画与批量出图、"
    "<b>V-Ray</b> 渲染及 <b>After Effects</b> 后期合成, 有 Unreal Engine 实时场景与电商产品视觉项目经验. "
    "能结合 Grasshopper 与 Python 处理参数化和制作效率需求, 注重灯光、材质、模型细节及信息表达节奏."
)

SKILLS = (
    "建模 / 参数化: Rhino, Grasshopper, 3ds Max, SketchUp, Blender | "
    "动画 / 实时: Cinema 4D, X-Particles, Unreal Engine 4/5, After Effects | "
    "渲染 / 后期: V-Ray, Enscape, Redshift, Octane, Photoshop | "
    "辅助工具: Python, ComfyUI, AutoCAD"
)

# 工作经历（按网页简历完整收录，并压缩为每段一条代表性职责）
EXP = [
    {
        "title": "儿童插画设计",
        "company": "武汉品胜文化传媒有限公司",
        "date": "2016 - 2016",
        "sw": "Photoshop",
        "summary": "使用数位板配合 Photoshop 完成儿童插画线稿上色，并整理画面色彩与细节。",
    },
    {
        "title": "公装施工图 / 效果图制图",
        "company": "武汉东湖装饰工程有限公司",
        "date": "2017 - 2019",
        "sw": "Photoshop / AutoCAD / 3ds Max / V-Ray",
        "summary": "负责工装项目施工图规范绘制；从零掌握 3ds Max + V-Ray，承担餐饮、办公空间效果图建模与渲染输出。",
    },
    {
        "title": "展厅 / 家具产品建模渲染",
        "company": "上海木里木外实业有限公司",
        "date": "2020 - 2021",
        "sw": "SketchUp / 3ds Max / V-Ray / Rhino / Cinema 4D",
        "summary": "使用 SketchUp 完成展厅空间布局，以 3ds Max + V-Ray 制作家具产品精细建模与渲染；同步学习 Rhino 和 C4D。",
    },
    {
        "title": "艺术装置 / 参数化建模设计",
        "company": "上海伍鼎景观设计咨询有限公司",
        "date": "2021 - 2022",
        "sw": "Rhino / Grasshopper / Enscape / V-Ray / Cinema 4D",
        "summary": "主导曲面景观雕塑及卡通 IP 形象建模，以 Enscape 完成方案可视化；引入 Grasshopper 参数化逻辑提升批量建模效率。",
    },
    {
        "title": "离职期间 / 技术进修",
        "company": "个人项目",
        "date": "2022 - 2023",
        "sw": "Cinema 4D / Octane（了解）/ Redshift（了解）/ Stable Diffusion",
        "summary": "学习 C4D 动画制作，并了解 Octane / Redshift 的基础渲染流程；完成具完整叙事的个人动画作品，搭建 Stable Diffusion 本地工作流。",
    },
    {
        "title": "动态虚拟直播场景设计",
        "company": "杭州青缇智能有限公司",
        "date": "2023 - 2024",
        "sw": "Rhino / Cinema 4D / X-Particles / Unreal Engine 4 / AE / PS",
        "summary": "主导 XR 直播场景从 Rhino 精模、C4D 动画到 UE4 实时播出的全流程；搭建互动场景分支并制作 UI 贴片与动态图层。",
    },
    {
        "title": "产品主图 / 动画设计制作",
        "company": "杭州顺颂商祺科技有限公司",
        "date": "2024 - 2024",
        "sw": "Cinema 4D / Rhino / V-Ray / After Effects",
        "summary": "制定产品图出图规范和 C4D 批量渲染场次，缩短多型号切换时间；独立完成产品宣传及安装说明动画的全流程制作。",
    },
    {
        "title": "离职期间 / 交互开发进修",
        "company": "个人项目",
        "date": "2024 - 2025",
        "sw": "Unreal Engine 5 / Babylon.js / Blender / Figma / Git",
        "summary": "完成 UE5 蓝图驱动的音乐可视化和休闲游戏原型；结合 Babylon.js 部署 Web3D 交互展示，并探索 Figma UI / UX 设计流程。",
    },
    {
        "title": "产品动画设计",
        "company": "武汉理理线科技有限公司",
        "date": "2025 - 2026",
        "sw": "Cinema 4D / Rhino / Grasshopper / After Effects / Python",
        "summary": "根据产品卖点完成安装说明、功能介绍视频及模型优化；负责音乐音效、口播字幕和包装，并开发 Python / Grasshopper 效率工具。",
    },
    {
        "title": "Unity 音频可视化原型开发（短期项目）",
        "company": "武汉声音进化有限公司",
        "date": "2026 - 2026",
        "sw": "Unity / Visual Scripting / Python / 音频分析",
        "summary": "搭建 Unity 音频分析面板及实时数据驱动接口，为 Shader 和后处理提供控制；完成基于节拍、频谱和能量的视觉反馈原型。",
    },
    {
        "title": "三维模型重建 / 自动化工具开发（远程）",
        "company": "Palatial（美国公司）",
        "date": "2026 - 2026",
        "sw": "Rhino / Grasshopper / Blender / Python / Qt / GLB / USDZ",
        "summary": "完成公寓柜体及内部抽屉结构的尺寸化重建，并用 Grasshopper 批量生成资产；开发 Qt 工具处理 GLB 转 USDZ 和贴图参数。",
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


def exp_table():
    data = [[Paragraph(label, ST["exp_hdr"]) for label in [
        "时间", "职位 / 公司", "软件工具", "核心职责"
    ]]]
    for e in EXP:
        data.append([
            Paragraph(e["date"], ST["exp_cell"]),
            Paragraph(f'<b>{e["title"]}</b><br/><font color="#555555">{e["company"]}</font>', ST["exp_cell"]),
            Paragraph(e["sw"], ST["exp_cell"]),
            Paragraph(e["summary"], ST["exp_cell"]),
        ])
    table = Table(data, colWidths=[TW * 0.10, TW * 0.25, TW * 0.31, TW * 0.34], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), C_BGD),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [C_BGST, C_BGW]),
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("TOPPADDING", (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0),(-1,-1), 4),
        ("RIGHTPADDING", (0,0),(-1,-1), 4),
        ("GRID", (0,0),(-1,-1), 0.25, C_RULE),
    ]))
    return table


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

    # ── 详细经历与作品集 ─────────────────────────────────────────────────
    story += sec_heading("详细经历&作品集")
    story.append(Paragraph(
        f'作品集主页 (GitHub Pages) - <b>全时期作品</b> <font color="#555555">{PORTFOLIO_DESC}</font>',
        ST["port_desc"]
    ))
    story.append(Paragraph(
        f'<a href="{PORTFOLIO_URL}" color="#4a6fa5">{PORTFOLIO_URL}</a>',
        ST["port_url"]
    ))
    story.append(Spacer(1, 4))

    # ── 工作经历 ─────────────────────────────────────────────────────────
    story += sec_heading("工作经历")
    story.append(exp_table())

    story.append(Spacer(1, 4))

    # ── 个人简介 ─────────────────────────────────────────────────────────
    story += sec_heading("个人简介")
    story.append(Paragraph(INTRO, ST["intro"]))
    story.append(Spacer(1, 3))

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
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("LEADING",       (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(-1,-1), 4.5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4.5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("GRID",          (0,0),(-1,-1), 0.3, C_RULE),
    ]))
    story.append(edu_tbl)

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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PDF", "CV_2026_0926.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build_pdf(out)
