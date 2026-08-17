"""
Builds a PDF summarising the cumulative sit-out penalty analysis.

One-off reporting script, kept alongside the app so the document can be
regenerated if the findings change. It does not touch index.html.
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_PATH = "Sit-out penalty analysis.pdf"

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#BBBBBB")
BAND = colors.HexColor("#F2F2F2")
FLAG = colors.HexColor("#B00020")

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleTight", parent=styles["Title"],
    fontName="Helvetica-Bold", fontSize=20, leading=24,
    textColor=INK, alignment=TA_LEFT, spaceAfter=2,
)
subtitle_style = ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontSize=10.5, leading=15, textColor=MUTED, spaceAfter=14,
)
heading_style = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=13, leading=17,
    textColor=INK, spaceBefore=16, spaceAfter=7,
    # Never let a heading sit alone at the foot of a page.
    keepWithNext=1,
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10.5, leading=15.5, textColor=INK, spaceAfter=9,
)
code_style = ParagraphStyle(
    "Code", parent=styles["Normal"],
    fontName="Courier", fontSize=9.5, leading=13,
    textColor=INK, backColor=BAND,
    borderPadding=(7, 7, 7, 7), spaceAfter=10,
)
caption_style = ParagraphStyle(
    "Caption", parent=styles["Normal"],
    fontSize=9, leading=13, textColor=MUTED, spaceAfter=12,
)
flag_style = ParagraphStyle(
    "Flag", parent=styles["Normal"],
    fontSize=10.5, leading=15.5, textColor=FLAG,
    fontName="Helvetica-Bold", spaceAfter=9,
)


def bullets(items):
    """A bulleted list with consistent spacing."""
    return ListFlowable(
        [ListItem(Paragraph(text, body_style), leftIndent=12) for text in items],
        bulletType="bullet", bulletFontSize=8, leftIndent=14, spaceAfter=6,
    )


def data_table(rows, column_widths, highlight_row=None):
    """A plain, high-contrast table. Row 0 is the header."""
    table = Table(rows, colWidths=column_widths, hAlign="LEFT")

    style = [
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",   (0, 0), (-1, -1), INK),
        ("BACKGROUND",  (0, 0), (-1, 0), BAND),
        ("LINEBELOW",   (0, 0), (-1, 0), 0.9, INK),
        ("GRID",        (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (1, 1), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]
    if highlight_row is not None:
        style.append(("TEXTCOLOR", (0, highlight_row), (-1, highlight_row), FLAG))
        style.append(("FONTNAME", (0, highlight_row), (-1, highlight_row), "Helvetica-Bold"))

    table.setStyle(TableStyle(style))
    return table


story = []

# --- Title ---------------------------------------------------------------
story.append(Paragraph("Cumulative sit-out penalty", title_style))
story.append(Paragraph(
    "Pickleball.ai scheduler &mdash; analysis of how session history affects "
    "who gets benched. Prepared 15 August 2026.", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.1, color=INK, spaceAfter=4))

# --- The answer ----------------------------------------------------------
story.append(Paragraph("The question, answered", heading_style))
story.append(Paragraph(
    "The penalty compares <b>raw counts</b>, not rates. A player with no "
    "history defaults to <b>zero</b>.", body_style))
story.append(Paragraph(
    "This is the whole calculation, from the scoring function:", body_style))
story.append(Paragraph(
    "const lifetimeSitOuts =<br/>"
    "&nbsp;&nbsp;historyContext.pastSitOuts[index]<br/>"
    "&nbsp;&nbsp;+ schedule.sitOutTally[index];",
    code_style))
story.append(Paragraph(
    "A lifetime tally added to tonight&rsquo;s tally. Nothing is divided by "
    "sessions attended. The penalty is then the spread &mdash; highest total "
    "minus lowest &mdash; multiplied by 6.", body_style))
story.append(Paragraph(
    "The zero default comes from how the tally is created: an array of one "
    "slot per player, filled with 0. Anyone absent from the record is simply "
    "never incremented.", body_style))

# --- Why it matters ------------------------------------------------------
story.append(Paragraph("Why the combination is wrong", heading_style))
story.append(Paragraph(
    "Raw counts reward attendance rather than measuring fairness, because "
    "somebody who comes rarely cannot accumulate sit-outs. Two findings, both "
    "measured over 20 generated schedules with one bench place per round.",
    body_style))

story.append(KeepTogether([
    Paragraph("Finding 1 &mdash; newcomers are penalised", heading_style),
    data_table(
        [
            ["", "Past sit-outs", "Share of bench time", "Fair share"],
            ["Four regulars", "48 each", "75% combined", "80%"],
            ["Newcomer (first night)", "0", "25%", "20%"],
        ],
        [150, 90, 120, 70],
        highlight_row=2,
    ),
    Paragraph(
        "A zero record reads as &ldquo;maximally owed bench time&rdquo;, so the "
        "newcomer is benched more than her fair share &mdash; penalised precisely "
        "for having never played.", caption_style),
]))

story.append(KeepTogether([
    Paragraph("Finding 2 &mdash; fairness is inverted", heading_style),
    data_table(
        [
            ["", "Sessions", "Raw sit-outs", "Per session", "Benched (20 runs)"],
            ["Faithful", "8", "8", "1.0", "17"],
            ["Occasional", "2", "6", "3.0", "20"],
        ],
        [110, 65, 85, 75, 105],
        highlight_row=2,
    ),
    Paragraph(
        "Occasional is treated three times worse every night she attends, yet has "
        "<i>fewer</i> raw sit-outs than Faithful &mdash; so the scheduler benches "
        "her even more. This is the more serious of the two problems.",
        caption_style),
]))
story.append(Paragraph(
    "The flaw only bites with irregular attendance. In a stable group where "
    "everyone turns up most weeks, raw counts and rates agree closely.",
    body_style))

# --- Options -------------------------------------------------------------
story.append(Paragraph("Three ways forward", heading_style))
story.append(Paragraph(
    "&ldquo;Fair&rdquo; here is a judgment about how the club runs, not a "
    "technical detail &mdash; hence a decision rather than a silent fix.",
    body_style))
story.append(bullets([
    "<b>Option A &mdash; compare rates.</b> Use sit-outs divided by sessions "
    "attended, so Occasional&rsquo;s 3.0 correctly outranks Faithful&rsquo;s "
    "1.0. Newcomers need a starting value; the section average is the neutral "
    "choice, meaning &ldquo;no claim either way&rdquo; rather than "
    "&ldquo;maximally owed&rdquo;. Fixes both findings.",

    "<b>Option B &mdash; keep raw counts, seed newcomers at the average.</b> "
    "A smaller change that fixes Finding 1, but leaves the Faithful/Occasional "
    "inversion in Finding 2 intact.",

    "<b>Option C &mdash; leave it.</b> Defensible if attendance is stable. "
    "No complexity added for a case that does not arise in practice.",
]))

story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=8))
story.append(Paragraph(
    "Nothing has been changed in the scheduler. The behaviour described here "
    "is what is currently committed and running.", flag_style))

doc = SimpleDocTemplate(
    OUTPUT_PATH, pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm,
    topMargin=18 * mm, bottomMargin=18 * mm,
    title="Cumulative sit-out penalty analysis",
    author="Pickleball.ai scheduler",
)
doc.build(story)
print("Wrote " + OUTPUT_PATH)
