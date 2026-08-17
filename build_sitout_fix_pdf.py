"""
Builds a PDF reporting the Option A fix to the sit-out penalty, with the
measured before/after numbers for both findings in the original analysis.

Companion to build_sitout_analysis_pdf.py, which documented the problem.
Neither script touches index.html.
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

OUTPUT_PATH = "Sit-out fairness fix.pdf"

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#BBBBBB")
BAND = colors.HexColor("#F2F2F2")
FLAG = colors.HexColor("#B00020")
GOOD = colors.HexColor("#0A6B2D")

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
good_style = ParagraphStyle(
    "Good", parent=styles["Normal"],
    fontSize=10.5, leading=15.5, textColor=GOOD,
    fontName="Helvetica-Bold", spaceAfter=9,
)


def bullets(items):
    """A bulleted list with consistent spacing."""
    return ListFlowable(
        [ListItem(Paragraph(text, body_style), leftIndent=12) for text in items],
        bulletType="bullet", bulletFontSize=8, leftIndent=14, spaceAfter=6,
    )


def data_table(rows, column_widths, good_rows=(), flag_rows=()):
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
    for row in good_rows:
        style.append(("TEXTCOLOR", (0, row), (-1, row), GOOD))
        style.append(("FONTNAME", (0, row), (-1, row), "Helvetica-Bold"))
    for row in flag_rows:
        style.append(("TEXTCOLOR", (0, row), (-1, row), FLAG))

    table.setStyle(TableStyle(style))
    return table


story = []

# --- Title ---------------------------------------------------------------
story.append(Paragraph("Sit-out fairness: Option A implemented", title_style))
story.append(Paragraph(
    "Pickleball.ai scheduler &mdash; sit-outs are now compared as rates, not "
    "totals. Both findings re-measured. 15 August 2026.", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.1, color=INK, spaceAfter=4))

# --- What changed --------------------------------------------------------
story.append(Paragraph("What changed", heading_style))
story.append(Paragraph(
    "The penalty used to level <b>lifetime sit-out totals</b>, with a newcomer "
    "starting at zero. It now levels <b>sit-outs per session attended</b>.",
    body_style))
story.append(bullets([
    "<b>A player's own rate</b> is used once they have three or more recorded "
    "sessions.",
    "<b>Below three sessions &mdash; including none at all &mdash;</b> the "
    "section average is used instead. One or two nights is noise, and it would "
    "otherwise dominate the scoring.",
    "<b>No history for the section</b> leaves the penalty skipped entirely, "
    "exactly as before.",
]))
story.append(Paragraph(
    "One design correction was needed along the way. Dividing each player by "
    "their <i>own</i> attendance still penalised the newcomer, because a short "
    "record is dragged further by a single night than a long one. Every player "
    "is now projected over the same horizon, so only the rates are compared:",
    body_style))
story.append(Paragraph(
    "function rateIncludingTonight(baseline, sitOutsTonight) {<br/>"
    "&nbsp;&nbsp;const sitOutsOverHorizon =<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;baseline.rate * HISTORY_RATE_HORIZON_NIGHTS<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;+ sitOutsTonight;<br/>"
    "&nbsp;&nbsp;return sitOutsOverHorizon / (HISTORY_RATE_HORIZON_NIGHTS + 1);<br/>"
    "}",
    code_style))

# --- Method --------------------------------------------------------------
story.append(Paragraph("How the numbers were measured", heading_style))
story.append(Paragraph(
    "Five players, one court, four rounds &mdash; four bench places to share "
    "among five people, so exactly one player escapes the bench each night and "
    "history decides who. The old raw-count scoring was replayed through the "
    "same harness for a like-for-like comparison. Finding 1 was run 300 times "
    "(1,200 bench places, an even share being 240 each); Finding 2 twenty "
    "times.", body_style))

# --- Finding 1 -----------------------------------------------------------
story.append(KeepTogether([
    Paragraph("Finding 1 &mdash; the newcomer", heading_style),
    data_table(
        [
            ["", "Before (totals)", "After (rates)", "Fair share"],
            ["Newcomer, first night", "300  (25.0%)", "238  (19.8%)", "240  (20%)"],
            ["Four regulars combined", "900  (75.0%)", "962  (80.2%)", "960  (80%)"],
        ],
        [150, 105, 105, 80],
        good_rows=(1,),
    ),
    Paragraph(
        "The newcomer lands on her fair share. Her starting rate is the section "
        "average of 6.0 per night rather than zero, so she arrives owing nothing "
        "and owed nothing. Before, she was benched in every single one of the "
        "300 runs; now she is indistinguishable from the regulars, the remaining "
        "spread being ordinary chance (one standard deviation is about 7).",
        caption_style),
]))

# --- Finding 2 -----------------------------------------------------------
story.append(KeepTogether([
    Paragraph("Finding 2 &mdash; Faithful against Occasional", heading_style),
    data_table(
        [
            ["", "Rate used", "Benched before", "Benched after"],
            ["Faithful (8 nights, 8 sit-outs)", "1.00", "17", "20"],
            ["Occasional (6 sit-outs)", "1.12", "20", "0"],
        ],
        [180, 70, 95, 95],
        good_rows=(2,),
    ),
    Paragraph(
        "The inversion is gone: Occasional is now benched <i>less</i> than "
        "Faithful, where before she was benched more despite having the worse "
        "deal every night she came.", caption_style),
]))
story.append(Paragraph(
    "Note the rate she is judged on. With only two recorded sessions she falls "
    "under the three-session guard, so the scheduler uses the section average "
    "of 1.12 rather than her own 3.0. That is the guard doing its job &mdash; "
    "and 1.12 is still above Faithful's 1.00, so she is favoured anyway. Given "
    "a third session, her own rate of 3.0 is used and the result is the same.",
    body_style))

# --- Self-correction -----------------------------------------------------
story.append(KeepTogether([
    Paragraph("The correction stops when the debt is paid", heading_style),
    Paragraph(
        "A fair scheduler should repay Occasional and then stop, not favour her "
        "forever. Letting her attend every week from then on:", body_style),
    data_table(
        [
            ["Week", "1", "2", "3", "4", "5", "6"],
            ["Her rate", "1.12", "2.00", "1.50", "1.20", "1.00", "1.00"],
            ["Sat out", "0", "0", "0", "0", "1", "1"],
        ],
        [80, 60, 60, 60, 60, 60, 60],
        good_rows=(2,),
    ),
    Paragraph(
        "Four weeks of protected play, then her rate meets the group's 1.00 and "
        "she rejoins the ordinary rotation. Week 2 rises to 2.00 because her "
        "third session unlocks her own rate; it then falls as she plays.",
        caption_style),
]))

# --- Review catch --------------------------------------------------------
story.append(Paragraph("A bug the review caught", heading_style))
story.append(Paragraph(
    "A sub-agent reviewing the change found that the switch turning this "
    "penalty off was testing the wrong thing. It asked &ldquo;is there any "
    "saved history?&rdquo; when what matters is &ldquo;do the players&rsquo; "
    "rates actually differ?&rdquo;. Where every rate is the same, the penalty "
    "measures nothing but tonight&rsquo;s imbalance, which is already charged "
    "for elsewhere &mdash; so it was billed twice.", body_style))
story.append(Paragraph(
    "This was not a rare edge case. With the three-session guard, nobody can "
    "be judged on their own rate until a section has three saved nights, so "
    "<b>every section&rsquo;s first two nights hit it, guaranteed</b>, as did "
    "any night where none of the players present appear in the record. The "
    "effect was to inflate the ordinary sit-out penalty from 8 to 14 per unit "
    "&mdash; a 75% distortion against every other consideration in the score, "
    "carrying no information at all.", body_style))
story.append(data_table(
    [
        ["Case", "History term before fix", "After fix"],
        ["Section with 2 saved nights", "6.0 points of noise", "0"],
        ["None of tonight's players in the record", "6.0 points of noise", "0"],
        ["Group who genuinely all share a rate", "6.0 points of noise", "0"],
        ["Rates that genuinely differ", "138 points", "138 points"],
    ],
    [230, 145, 90],
    good_rows=(1, 2, 3),
))
story.append(Paragraph(
    "The last row is the check that matters in the other direction: the fix "
    "silences the penalty only where it was saying nothing, and leaves it at "
    "full strength where it has something to say.", caption_style))

# --- Unchanged -----------------------------------------------------------
story.append(Paragraph("What deliberately did not change", heading_style))
story.append(bullets([
    "A section with no saved history scores exactly as before &mdash; the "
    "history sit-out term stays at zero, so tonight's imbalance is not counted "
    "twice.",
    "History saved against a different section is ignored, as before.",
    "Saving a session is still a deliberate click. Nothing auto-saves.",
    "Repeated partners and opponents from past sessions are untouched.",
    "Backup files need no migration: rates are worked out at generate time "
    "from what is already saved, so nothing new is written to disk.",
]))

story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=8))
story.append(Paragraph(
    "Both findings from the original analysis are resolved. The change is in "
    "index.html and running.", good_style))

doc = SimpleDocTemplate(
    OUTPUT_PATH, pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm,
    topMargin=18 * mm, bottomMargin=18 * mm,
    title="Sit-out fairness: Option A implemented",
    author="Pickleball.ai scheduler",
)
doc.build(story)
print("Wrote " + OUTPUT_PATH)
