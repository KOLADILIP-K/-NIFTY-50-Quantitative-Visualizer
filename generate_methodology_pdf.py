"""
Generate NIFTY50_Visualizer_Methodology_and_Formulas.pdf
Rigorous mathematical, algorithmic, and quantitative specification document
containing exact formulas, conditions, thresholds, and logic for the NIFTY 50 Visualizer.
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "NIFTY50_Visualizer_Methodology_and_Formulas.pdf")

class MethodologyNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Header rule & text (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#0284c7"))
            self.drawString(14 * mm, A4[1] - 10 * mm, "NIFTY 50 QUANTITATIVE VISUALIZER  |  METHODOLOGY & FORMULAS")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(A4[0] - 14 * mm, A4[1] - 10 * mm, "MATHEMATICAL SPECIFICATION")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(14 * mm, A4[1] - 11.5 * mm, A4[0] - 14 * mm, A4[1] - 11.5 * mm)

        # Footer rule & page number
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(14 * mm, 12 * mm, A4[0] - 14 * mm, 12 * mm)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(14 * mm, 8.5 * mm, "Confidential — Quantitative Formula Specification: Dow Theory, Williams %R, BRC & Alerts")
        self.drawRightString(A4[0] - 14 * mm, 8.5 * mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_methodology_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=15 * mm,
        bottomMargin=16 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2
    )

    formula_box = ParagraphStyle(
        'FormulaBox',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )

    table_header = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#0f172a')
    )

    table_cell = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # ==================== COVER / HEADER ====================
    story.append(Paragraph("NIFTY 50 Quantitative Visualizer — Methodology & Formulas Specification", title_style))
    story.append(Paragraph("Formal Mathematical Definitions, Algorithmic Decision Trees, Threshold Equations, and Alert Logic for Multi-Timeframe Institutional Modeling", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=8))

    # ==================== SECTION 1 ====================
    story.append(Paragraph("1. Charles Dow Theory Market Structure Formalization", h1_style))
    story.append(Paragraph(
        "Market structure provides the primary deterministic backbone for institutional regime classification. "
        "A market is partitioned into fractal swings, structural breaks, and directional bias blocks:",
        body_style
    ))

    # Formula 1: Fractal Swings
    f1_content = [
        [Paragraph("<b>1.1 Bilateral Fractal Swing Extrema Equations:</b><br/>"
                   "Given a discrete bar sequence with High $H_t$ and Low $L_t$, a bar at index $i$ is a confirmed <b>Swing High (SH)</b> or <b>Swing Low (SL)</b> of order $n$ if and only if:<br/>"
                   "&nbsp;&nbsp;&bull; <b>Swing High:</b> <code>SH_i &hArr; (H_i &ge; H_{i-k}) &and; (H_i &ge; H_{i+k}), &forall; k &isin; {1, 2, ..., n}</code><br/>"
                   "&nbsp;&nbsp;&bull; <b>Swing Low:</b> &nbsp;<code>SL_i &hArr; (L_i &le; L_{i-k}) &and; (L_i &le; L_{i+k}), &forall; k &isin; {1, 2, ..., n}</code><br/>"
                   "<i>Adaptive Timeframe Order:</i> $n = 3$ for 1D & 4H; $n = 4$ for 1H; $n = 5$ for 30m & 15m; $n = 6$ for 5m.", formula_box)]
    ]
    t_f1 = Table(f1_content, colWidths=[182 * mm])
    t_f1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#0284c7')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f1)
    story.append(Spacer(1, 4))

    # Formula 2: Structural Tagging & BOS
    f2_content = [
        [Paragraph("<b>1.2 Sequential Structural Tagging & Break of Structure (BOS):</b><br/>"
                   "Let $SH_t$ and $SL_t$ be the current swing points, and $SH_{t-1}, SL_{t-1}$ the previous swing points:<br/>"
                   "&nbsp;&nbsp;&bull; <b>Higher High (HH):</b> <code>H(SH_t) &gt; H(SH_{t-1})</code> &nbsp;|&nbsp; <b>Lower High (LH):</b> <code>H(SH_t) &le; H(SH_{t-1})</code><br/>"
                   "&nbsp;&nbsp;&bull; <b>Higher Low (HL):</b> &nbsp;<code>L(SL_t) &gt; L(SL_{t-1})</code> &nbsp;|&nbsp; <b>Lower Low (LL):</b> &nbsp;<code>L(SL_t) &le; L(SL_{t-1})</code><br/>"
                   "&nbsp;&nbsp;&bull; <b>Bullish BOS Event:</b> <code>Close_t &gt; H(SH_{prev}) &and; Close_{t-1} &le; H(SH_{prev})</code><br/>"
                   "&nbsp;&nbsp;&bull; <b>Bearish BOS Event:</b> <code>Close_t &lt; L(SL_{prev}) &and; Close_{t-1} &ge; L(SL_{prev})</code>", formula_box)]
    ]
    t_f2 = Table(f2_content, colWidths=[182 * mm])
    t_f2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#10b981')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f2)
    story.append(Spacer(1, 4))

    # Formula 3: Pre/Post Breakout Metrics & Block Color
    f3_content = [
        [Paragraph(r"<b>1.3 Pre-Breakout Range, Post-Breakout Excursion & Block Color Rule:</b><br/>"
                   r"&nbsp;&nbsp;&bull; <b>Pre-Breakout Consolidation Range:</b> <code>R_{pre} = H(SH_{prev}) - L(SL_{prev})</code><br/>"
                   r"&nbsp;&nbsp;&bull; <b>Pre-Breakout Compression Bars:</b> <code>N_{bars} = Index(Breakout) - Index(Boundary_Anchor)</code><br/>"
                   r"&nbsp;&nbsp;&bull; <b>Post-Breakout Max Favorable Excursion (MFE):</b><br/>"
                   r"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Bullish: <code>MFE = max_{i &ge; t_{break}} (H_i) - Level_{BOS}</code> &nbsp;|&nbsp; Bearish: <code>MFE = Level_{BOS} - min_{i &ge; t_{break}} (L_i)</code><br/>"
                   r"&nbsp;&nbsp;&bull; <b>Retest Verification:</b> <code>|Price - Level_{BOS}| &le; 0.25 &times; ATR_{14}</code> (Confirmed if bounce occurs; Failed if close breaches inside).<br/>"
                   r"&nbsp;&nbsp;&bull; <b>Block Color Rule:</b><br/>"
                   r"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>Color = GREEN &hArr; (HH &and; HL confirmed) &or; (Bullish BOS Active &and; Retest Confirmed)</code><br/>"
                   r"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>Color = RED &nbsp;&nbsp;&hArr; (LH &and; LL confirmed) &or; (Bearish BOS Active &and; Retest Confirmed)</code><br/>"
                   r"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>Color = AMBER &hArr; Mixed Swings (Consolidation / Triangle Compression)</code>", formula_box)]
    ]
    t_f3 = Table(f3_content, colWidths=[182 * mm])
    t_f3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#f59e0b')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f3)
    story.append(Spacer(1, 6))

    # ==================== SECTION 2 ====================
    story.append(Paragraph(r"2. Williams %R ($W\%R_{14}$) & Swing Confluence Gap Metric", h1_style))
    story.append(Paragraph(
        "Larry Williams' %R oscillator measures relative close location against the 14-period extreme channel. "
        "The system evaluates whether price swing pivots coincide with %R exhaustion extremes, and computes the exact gap distance when they diverge:",
        body_style
    ))

    f4_content = [
        [Paragraph("<b>2.1 Williams %R Formulation:</b><br/>"
                   "$$W\\%R_{14, t} = \\frac{\\max_{i=0}^{13}(H_{t-i}) - Close_t}{\\max_{i=0}^{13}(H_{t-i}) - \\min_{i=0}^{13}(L_{t-i})} \\times (-100)$$<br/>"
                   "Bounded strictly in $[-100.0, 0.0]$. Institutional Regimes:<br/>"
                   "&nbsp;&nbsp;&bull; <b>Overbought Exhaustion Zone:</b> <code>W%R &ge; -20.0</code> (Extreme &ge; -10.0)<br/>"
                   "&nbsp;&nbsp;&bull; <b>Oversold Discount Zone:</b> &nbsp;&nbsp;<code>W%R &le; -80.0</code> (Extreme &le; -90.0)<br/>"
                   "&nbsp;&nbsp;&bull; <b>Neutral Momentum Channel:</b> <code>-80.0 &lt; W%R &lt; -20.0</code> (Centerline at -50.0)", formula_box)]
    ]
    t_f4 = Table(f4_content, colWidths=[182 * mm])
    t_f4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#38bdf8')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f4)
    story.append(Spacer(1, 4))

    f5_content = [
        [Paragraph("<b>2.2 Swing Confluence Matching & 'How Far It Is' Gap Distance Metric:</b><br/>"
                   "For every confirmed Swing High ($SH$) and Swing Low ($SL$):<br/>"
                   "&nbsp;&nbsp;&bull; <b>Swing High Confluence Match:</b> <code>W%R(SH) &ge; -20.0 &rArr; MATCH (Perfect Momentum Confirmation)</code><br/>"
                   "&nbsp;&nbsp;&bull; <b>Swing Low Confluence Match:</b> &nbsp;<code>W%R(SL) &le; -80.0 &rArr; MATCH (Perfect Momentum Confirmation)</code><br/>"
                   "&nbsp;&nbsp;&bull; <b>'How Far It Is' Gap Distance Formula (&Delta;%R pts):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>&Delta;%R(SH) = |-20.0 - W%R(SH)|</code>, if $W\\%R(SH) < -20.0$; else $0.0$<br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>&Delta;%R(SL) = |W%R(SL) - (-80.0)|</code>, if $W\\%R(SL) > -80.0$; else $0.0$<br/>"
                   "<i>Interpretation:</i> A non-zero gap distance directly quantifies the extent of <b>momentum divergence</b> at price inflection points.", formula_box)]
    ]
    t_f5 = Table(f5_content, colWidths=[182 * mm])
    t_f5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#a855f7')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f5)

    # ==================== PAGE BREAK ====================
    story.append(PageBreak())

    # ==================== SECTION 3 ====================
    story.append(Paragraph("3. Big Range Candle (BRC) Volatility Engine & Proximity Metric", h1_style))
    story.append(Paragraph(
        "The BRC engine identifies statistical volatility expansion where bar range dramatically exceeds prevailing baseline volatility. "
        "When a bar does not satisfy the BRC trigger, the system evaluates how far it is in points and percentage to the threshold:",
        body_style
    ))

    f6_content = [
        [Paragraph(r"<b>3.1 Wilder's Average True Range (ATR14) & Relative Range:</b><br/>"
                   r"$$TR_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$$<br/>"
                   r"$$ATR_{14, t} = \frac{13 \times ATR_{14, t-1} + TR_t}{14}$$<br/>"
                   r"$$Relative\_Range_t = \frac{Range_t}{ATR_{14, t}} = \frac{H_t - L_t}{ATR_{14, t}}$$<br/>"
                   r"&bull; <b>BRC Deterministic Trigger:</b> <code>Relative_Range_t &ge; 1.50</code> (Threshold $T_{BRC} = 1.50 \times ATR_{14}$)<br/>"
                   r"&bull; <b>Bullish BRC (Green):</b> <code>Relative_Range &ge; 1.5 &and; Close &gt; Open &and; (Body / Range) &ge; 0.10</code><br/>"
                   r"&bull; <b>Bearish BRC (Red):</b> &nbsp;<code>Relative_Range &ge; 1.5 &and; Close &lt; Open &and; (Body / Range) &ge; 0.10</code><br/>"
                   r"&bull; <b>Neutral / Doji BRC:</b> <code>Relative_Range &ge; 1.5 &and; (Body / Range) &lt; 0.10</code><br/>"
                   r"&bull; <b>Normal Candle:</b> &nbsp;&nbsp;&nbsp;&nbsp;<code>Relative_Range &lt; 1.50</code>", formula_box)]
    ]
    t_f6 = Table(f6_content, colWidths=[182 * mm])
    t_f6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#ef4444')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f6)
    story.append(Spacer(1, 4))

    f7_content = [
        [Paragraph(r"<b>3.2 'How Far It Is If Not Found' Proximity Equations:</b><br/>"
                   r"For any bar where $Relative\_Range < 1.50$ (Normal Candle / In-Progress Bar):<br/>"
                   r"&nbsp;&nbsp;&bull; <b>Points Needed to Reach BRC (&Delta;Pts):</b><br/>"
                   r"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$$\Delta Pts = \max(0.0, 1.50 \times ATR_{14, t} - Range_t)$$<br/>"
                   r"&nbsp;&nbsp;&bull; <b>Proximity Percentage Reached (Proximity %):</b><br/>"
                   r"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$$Proximity\% = \min\left(100.0, \frac{Range_t}{1.50 \times ATR_{14, t}} \times 100.0\right)$$<br/>"
                   r"&nbsp;&nbsp;&bull; <b>Compression Duration:</b> <code>Bars_Since_BRC = Index(Current) - Index(Last_Confirmed_BRC)</code><br/>"
                   r"<i>Squeeze Signal:</i> If $Bars\_Since\_BRC \ge 12$ bars, volatility compression reaches the 90th empirical percentile, signaling imminent directional expansion.", formula_box)]
    ]
    t_f7 = Table(f7_content, colWidths=[182 * mm])
    t_f7.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#10b981')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f7)
    story.append(Spacer(1, 6))

    # ==================== SECTION 4 ====================
    story.append(Paragraph("4. Dow Theory Three-Trend Hierarchy Mathematical Rules", h1_style))
    story.append(Paragraph(
        "Charles Dow categorized market movements into three synchronous tiers: Primary (The Tide), Secondary (The Waves), and Tertiary (The Ripples). "
        "The mathematical classification rules implemented in the terminal are:",
        body_style
    ))

    dow_rules_data = [
        [Paragraph("Dow Trend Tier", table_header), Paragraph("Target Timeframes", table_header), Paragraph("Deterministic Classification Condition", table_header), Paragraph("Mathematical Rule", table_header)],
        [Paragraph("<b>Primary Trend</b><br/>(The Tide)", table_cell), Paragraph("<b>1D & 4H</b>", table_cell), Paragraph("Evaluates multi-month macro structure. Bullish if 1D structure forms confirmed HH/HL and price holds above 21 EMA. Bearish if LH/LL.", table_cell), Paragraph("$$S_{pri} = 2 \\cdot Sign(Bias_{1D}) + Sign(Bias_{4H})$$<br/>Bullish if $S_{pri} \\ge 2$; Bearish if $S_{pri} \\le -2$.", table_cell)],
        [Paragraph("<b>Secondary Trend</b><br/>(The Waves)", table_cell), Paragraph("<b>4H & 1H</b>", table_cell), Paragraph("Evaluates counter-trend reactions or aligned impulses. Tracks percentage retracement of the primary swing.", table_cell), Paragraph("$$Retracement\\% = \\frac{|SH_{pri} - Close|}{|SH_{pri} - SL_{pri}|} \\times 100$$<br/><b>Dow Golden Zone:</b> $33.3\\%$ to $66.7\\%$.", table_cell)],
        [Paragraph("<b>Tertiary Trend</b><br/>(The Ripples)", table_cell), Paragraph("<b>30m, 15m, 5m</b>", table_cell), Paragraph("Evaluates minor intraday fluctuations and microstructure setups. Used strictly for high-precision entry timing.", table_cell), Paragraph("$$S_{ter} = \\sum_{tf \\in \\{30m, 15m, 5m\\}} Sign(Bias_{tf})$$<br/>Aligned Long if $S_{ter} \\ge 2$; Short if $S_{ter} \\le -2$.", table_cell)],
        [Paragraph("<b>Triple Confluence</b>", table_cell), Paragraph("<b>All 6 TFs</b>", table_cell), Paragraph("Highest-conviction regime where Primary, Secondary, and Tertiary all share identical directional bias.", table_cell), Paragraph("$$Confluence = (Bias_{pri} == Bias_{sec} == Bias_{ter})$$<br/>Trigger for institutional position sizing.", table_cell)],
    ]
    t_dow = Table(dow_rules_data, colWidths=[34 * mm, 24 * mm, 66 * mm, 58 * mm])
    t_dow.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_dow)
    story.append(Spacer(1, 6))

    # ==================== SECTION 5 ====================
    story.append(Paragraph("5. Relative Strength Index (RSI 14) & Divergence Equations", h1_style))
    story.append(Paragraph(
        "RSI is evaluated on Close prices across all timeframes using J. Welles Wilder's 14-period exponential smoothing:",
        body_style
    ))

    f8_content = [
        [Paragraph("<b>5.1 RSI Formulation & Divergence Conditions:</b><br/>"
                   "$$U_t = \\max(0, Close_t - Close_{t-1}), \\quad D_t = \\max(0, Close_{t-1} - Close_t)$$<br/>"
                   "$$RS_t = \\frac{Wilder(U, 14)_t}{Wilder(D, 14)_t}, \\quad RSI_{14, t} = 100 - \\frac{100}{1 + RS_t}$$<br/>"
                   "&bull; <b>Regular Bearish Divergence:</b> <code>High(SH_2) &gt; High(SH_1) &nbsp;&and;&nbsp; RSI(SH_2) &lt; RSI(SH_1)</code><br/>"
                   "&bull; <b>Regular Bullish Divergence:</b> <code>Low(SL_2) &lt; Low(SL_1) &nbsp;&and;&nbsp; RSI(SL_2) &gt; RSI(SL_1)</code><br/>"
                   "&bull; <b>Momentum Regime Barrier:</b> Bullish Control when $RSI > 50$ (support at 40-50); Bearish Control when $RSI < 50$ (resistance at 50-60).", formula_box)]
    ]
    t_f8 = Table(f8_content, colWidths=[182 * mm])
    t_f8.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#a855f7')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_f8)
    story.append(Spacer(1, 6))

    # ==================== SECTION 6 ====================
    story.append(Paragraph("6. User-Configurable Dynamic Alert Evaluation Logic", h1_style))
    story.append(Paragraph(
        "The alert dispatcher maps dynamic user threshold vectors $\\vec{\\theta} = \\{w_{ob}, w_{os}, \\Delta w_{gap}, m_{brc}, p_{brc}, r_{ob}, r_{os}\\}$ into discrete boolean trigger alerts:",
        body_style
    ))

    alert_matrix_data = [
        [Paragraph("Alert Category", table_header), Paragraph("User Input Variable", table_header), Paragraph("Default Value", table_header), Paragraph("Boolean Trigger Condition", table_header), Paragraph("Severity", table_header)],
        [Paragraph("<b>Market Structure BOS</b>", table_cell), Paragraph("Timeframe Selection", table_cell), Paragraph("All 6 TFs", table_cell), Paragraph("<code>(Close_t &gt; SH_{prev}) &or; (Close_t &lt; SL_{prev})</code>", table_cell), Paragraph("<font color='#991b1b'><b>CRITICAL</b></font>", table_cell)],
        [Paragraph("<b>Williams %R Overbought</b>", table_cell), Paragraph("<code>cfgWprOb</code> ($w_{ob}$)", table_cell), Paragraph("-20.0 pts", table_cell), Paragraph("<code>W%R_{14, t} &ge; w_{ob}</code>", table_cell), Paragraph("<font color='#d97706'><b>WARNING</b></font>", table_cell)],
        [Paragraph("<b>Williams %R Oversold</b>", table_cell), Paragraph("<code>cfgWprOs</code> ($w_{os}$)", table_cell), Paragraph("-80.0 pts", table_cell), Paragraph("<code>W%R_{14, t} &le; w_{os}</code>", table_cell), Paragraph("<font color='#d97706'><b>WARNING</b></font>", table_cell)],
        [Paragraph("<b>Swing %R Gap Divergence</b>", table_cell), Paragraph("<code>cfgWprGap</code> ($\\Delta w_{gap}$)", table_cell), Paragraph("15.0 pts", table_cell), Paragraph("<code>&not;Match(Swing) &and; &Delta;%R &ge; &Delta;w_{gap}</code>", table_cell), Paragraph("<font color='#0284c7'><b>INFO</b></font>", table_cell)],
        [Paragraph("<b>BRC Volatility Trigger</b>", table_cell), Paragraph("<code>cfgBrcMult</code> ($m_{brc}$)", table_cell), Paragraph("1.50x ATR", table_cell), Paragraph("<code>Range_t &ge; m_{brc} &times; ATR_{14, t}</code>", table_cell), Paragraph("<font color='#991b1b'><b>CRITICAL</b></font>", table_cell)],
        [Paragraph("<b>BRC Proximity Warning</b>", table_cell), Paragraph("<code>cfgBrcProx</code> ($p_{brc}$)", table_cell), Paragraph("75.0 %", table_cell), Paragraph("<code>Proximity\\% &ge; p_{brc} &and; Range_t &lt; Threshold_{BRC}</code>", table_cell), Paragraph("<font color='#d97706'><b>WARNING</b></font>", table_cell)],
        [Paragraph("<b>RSI Extreme Overbought</b>", table_cell), Paragraph("<code>cfgRsiOb</code> ($r_{ob}$)", table_cell), Paragraph("70.0 pts", table_cell), Paragraph("<code>RSI_{14, t} &ge; r_{ob}</code>", table_cell), Paragraph("<font color='#d97706'><b>WARNING</b></font>", table_cell)],
        [Paragraph("<b>RSI Extreme Oversold</b>", table_cell), Paragraph("<code>cfgRsiOs</code> ($r_{os}$)", table_cell), Paragraph("30.0 pts", table_cell), Paragraph("<code>RSI_{14, t} &le; r_{os}</code>", table_cell), Paragraph("<font color='#d97706'><b>WARNING</b></font>", table_cell)],
    ]
    t_alert = Table(alert_matrix_data, colWidths=[38 * mm, 34 * mm, 24 * mm, 66 * mm, 20 * mm])
    t_alert.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_alert)

    doc.build(story, canvasmaker=MethodologyNumberedCanvas)
    print(f"[SUCCESS] Methodology PDF generated: {PDF_PATH}")

if __name__ == "__main__":
    build_methodology_pdf()
