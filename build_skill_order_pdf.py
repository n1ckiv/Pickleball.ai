"""
Builds a PDF summarising the skill-order feature and its measurements.

One-off reporting script, kept alongside the app so the document can be
regenerated if the numbers change. It does not touch index.html.
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

OUTPUT_PATH = "Skill order - feature and measurements.pdf"

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#555555")
RULE = colors.HexColor("#BBBBBB")
BAND = colors.HexColor("#F2F2F2")
FLAG = colors.HexColor("#B00020")
GOOD = colors.HexColor("#1B5E20")

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


def data_table(rows, column_widths, highlight_row=None, highlight_colour=FLAG):
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
        style.append(("TEXTCOLOR", (0, highlight_row), (-1, highlight_row), highlight_colour))
        style.append(("FONTNAME", (0, highlight_row), (-1, highlight_row), "Helvetica-Bold"))

    table.setStyle(TableStyle(style))
    return table


story = []

# --- Title ---------------------------------------------------------------
story.append(Paragraph("Skill order within a section", title_style))
story.append(Paragraph(
    "Pickleball.ai scheduler &mdash; what was built, what it was measured to "
    "do, and why the scoring ended up switched off. Prepared 17 August 2026.",
    subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.1, color=INK, spaceAfter=4))

# --- What was built ------------------------------------------------------
story.append(Paragraph("What was built", heading_style))
story.append(Paragraph(
    "Players can now be ranked within each section they belong to. The order "
    "is a list of <b>tiers</b> rather than a strict one-per-player ranking, so "
    "players of the same standard can share a tier. Tier 1 is strongest.",
    body_style))
story.append(bullets([
    "<b>Data.</b> Each player gains <font face='Courier'>tiers: { \"int\": 2 }"
    "</font> &mdash; one number per section. A player&rsquo;s tier in one "
    "section is completely independent of their tier in another.",

    "<b>UI.</b> A Skill order panel on Manage players, with a section picker. "
    "Players are listed strongest first under numbered tier headings, moved "
    "with up and down buttons. <b>Not drag and drop</b>, which does not work "
    "on iPad Safari. &ldquo;Equal to above&rdquo; merges a player into the "
    "tier above; &ldquo;Split off&rdquo; breaks them out again.",

    "<b>Scoring.</b> A team-balance penalty on doubles courts, charged per "
    "point of difference between the two teams&rsquo; tier totals. Singles "
    "courts are skipped &mdash; a 1v1 has no teams to even up.",
]))
story.append(Paragraph(
    "Tier numbers are re-derived from list position on every write, so gaps "
    "cannot develop and the display and the scoring can never disagree.",
    body_style))

# --- Verification --------------------------------------------------------
story.append(Paragraph("Independent verification", heading_style))
story.append(Paragraph(
    "A separate agent, which had not seen the implementation, wrote tests "
    "against the specification and ran them at the production budget of "
    "10,000 attempts. Three of four criteria passed; one failed.",
    body_style))

story.append(KeepTogether([
    data_table(
        [
            ["Criterion", "Result", "Measured"],
            ["Strongest two rarely paired", "PASS", "7.3% vs 12.3% of rounds"],
            ["Untiered section unchanged", "PASS", "0 mismatches / 3,000"],
            ["Cross-section independence", "PASS", "0 of 8 tiers moved"],
            ["Partner variety not degraded", "FAIL", "repeats up 79%"],
        ],
        [190, 70, 170],
        highlight_row=4,
    ),
    Paragraph(
        "The failure was structural rather than a tuning mistake. The penalty "
        "was charged on every court in every round and then totalled, so it "
        "grew with the length of the evening &mdash; while a repeated "
        "partnership is charged once. The &ldquo;smallest weight in the "
        "file&rdquo; ended up contributing more to the score than the "
        "repeated-partner term it was meant to sit below.",
        caption_style),
]))

story.append(Paragraph(
    "Worth recording separately: the specific harm the feature targets "
    "&mdash; the top two partnered <i>against</i> the bottom two &mdash; was "
    "already occurring in <b>1 round out of 360</b> before the feature "
    "existed.", body_style))

# --- The three fixes -----------------------------------------------------
story.append(Paragraph("Three changes in response", heading_style))
story.append(bullets([
    "<b>Normalised.</b> The balance term is now the mean per doubles court, "
    "not the total, so its size no longer depends on how long the session is.",

    "<b>Retuned</b> from 2 to 0.5, and then to 0 &mdash; see below.",

    "<b>Untiered middle fixed.</b> The rounding was dropped. A player with no "
    "tier now lands on the exact midpoint of their section, the same neutral "
    "value a guest gets. Previously <font face='Courier'>Math.round(4.5)</font> "
    "made them a 5 &mdash; scored as slightly weak rather than unjudged.",
]))

story.append(KeepTogether([
    Paragraph("Normalisation holds", heading_style),
    data_table(
        [
            ["Rounds", "Courts scored", "Balance points in score"],
            ["3", "6", "2.01"],
            ["6", "12", "1.93"],
            ["12", "24", "1.91"],
        ],
        [90, 120, 180],
    ),
    Paragraph(
        "Flat across a fourfold change in session length. Before the fix this "
        "figure scaled roughly in line with the court count.", caption_style),
]))

# --- The measurement -----------------------------------------------------
story.append(Paragraph("Retuning to 0.5: variety restored", heading_style))
story.append(Paragraph(
    "100 schedules per condition, 10,000 attempts each, 8 players on 2 courts "
    "over 6 rounds.", body_style))

story.append(data_table(
    [
        ["", "Penalty on (0.5)", "Off (before)"],
        ["Zero-repeat schedules", "11 / 100", "9 / 100"],
        ["Repeated partners", "1.66", "1.68"],
        ["Distinct partnerships", "22.34", "22.32"],
        ["Balance points in score", "2.0", "0"],
        ["Partner points in score", "16.6", "16.8"],
        ["Top two paired per round", "0.148", "0.153"],
    ],
    [190, 120, 110],
))
story.append(Paragraph(
    "Zero-repeat schedules are back at 11 in 100, against the 12 benchmark. "
    "By the stated rule, that keeps the weight at 0.5.", caption_style))

# --- The catch -----------------------------------------------------------
story.append(Paragraph("Why that number is misleading", heading_style))
story.append(Paragraph(
    "Variety came back because the term stopped influencing the search. It "
    "now contributes <b>2.0 points against a mean score of 173</b>, about 1%. "
    "Top-two pairing moved from 0.153 to 0.148 per round, which is noise.",
    body_style))
story.append(Paragraph(
    "A weight sweep was run to find whether any setting buys the effect "
    "without the cost. It does not &mdash; the trade is clean and monotonic.",
    body_style))

story.append(KeepTogether([
    data_table(
        [
            ["Weight", "Zero-repeat /100", "Repeated partners", "Top two paired /round"],
            ["Off", "9", "1.68", "0.153"],
            ["0.5", "11", "1.66", "0.148"],
            ["2", "8.3", "1.77", "0.136"],
            ["10", "5.8", "2.04", "0.117"],
            ["25", "0", "3.10", "0.097"],
        ],
        [70, 120, 130, 130],
    ),
    Paragraph(
        "Every point of separation between the strong pair is paid for in "
        "partner variety. There is no setting that delivers one without "
        "spending the other.", caption_style),
]))

# --- Recommendation ------------------------------------------------------
story.append(Paragraph("The decision taken: weight 0", heading_style))
story.append(Paragraph(
    "The weight is set to <b>0</b>. A setting small enough not to cost "
    "variety is a setting small enough to do nothing &mdash; at 0.5 the term "
    "was worth 2 points against a typical score of 173 &mdash; and every "
    "setting large enough to matter costs partner variety. The problem it "
    "was built to solve was occurring in one round out of 360 anyway.",
    body_style))
story.append(Paragraph(
    "<b>The skill order itself is kept.</b> Tiers are still recorded, "
    "displayed and editable, and working out the ranking is the hard part if "
    "this is ever wanted again. Only the scoring is switched off. At 0 the "
    "term takes the same path as an unranked section, so it is genuinely "
    "skipped rather than computed and multiplied by nothing, and the tier "
    "line no longer appears in the stats.", body_style))
story.append(Paragraph(
    "Verified after the change: a fully ranked section scores identically to "
    "the pre-feature code across <b>3,000 schedules, 0 field mismatches</b>. "
    "Ranking, reordering and merging tiers all still work.", body_style))

story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=8))
story.append(Paragraph(
    "No schedule produced today differs from one produced before any of this "
    "was built. The tiers are recorded and waiting; nothing acts on them.",
    flag_style))

doc = SimpleDocTemplate(
    OUTPUT_PATH, pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm,
    topMargin=18 * mm, bottomMargin=18 * mm,
    title="Skill order - feature and measurements",
    author="Pickleball.ai scheduler",
)
doc.build(story)
print("Wrote " + OUTPUT_PATH)
