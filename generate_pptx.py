#!/usr/bin/env python3
"""Generate Task2_Presentation.pptx for the IoT-23 cybersecurity team project."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

RESULTS = "results"
OUT = "Task2_Presentation.pptx"

NAVY = RGBColor(0x0B, 0x2A, 0x4A)
RED = RGBColor(0xC0, 0x39, 0x2B)
GRAY = RGBColor(0x55, 0x55, 0x55)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]


def add_title_bar(slide, title):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.8))
    tf = box.text_frame
    tf.text = title
    p = tf.paragraphs[0]
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = NAVY


def add_text(slide, left, top, width, height, text, size=18, bold=False, color=GRAY, align=None):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.text = text
    for p in tf.paragraphs:
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        if align:
            p.alignment = align


def add_bullets(slide, left, top, width, height, items, size=18):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "•  " + item
        p.font.size = Pt(size)
        p.font.color.rgb = GRAY
        p.space_after = Pt(8)


# ============================================================
# Slide 1 - Title
# ============================================================
s = prs.slides.add_slide(BLANK)
box = s.shapes.add_textbox(Inches(0.5), Inches(2.3), Inches(12.3), Inches(1.5))
tf = box.text_frame
tf.text = "Detecting IoT Botnet Attacks"
p = tf.paragraphs[0]
p.font.size = Pt(48)
p.font.bold = True
p.font.color.rgb = NAVY
p.alignment = PP_ALIGN.CENTER

add_text(s, 0.5, 3.6, 12.3, 0.6, "A Machine Learning Approach Using the IoT-23 Dataset",
         size=24, color=GRAY, align=PP_ALIGN.CENTER)
add_text(s, 0.5, 4.5, 12.3, 0.5,
         "Thabo Ibrahim Traore  •  Jordan Barnes  •  Zizwe Mtonga  •  Tapiwa Musinga",
         size=16, color=GRAY, align=PP_ALIGN.CENTER)
add_text(s, 0.5, 6.5, 12.3, 0.5, "CS Linux Team Project — Alabama A&M University",
         size=14, color=GRAY, align=PP_ALIGN.CENTER)


# ============================================================
# Slide 2 - Objective / Problem Statement
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Objective & Problem Statement")

add_text(s, 0.5, 1.4, 12.3, 0.5, "The Problem", size=22, bold=True, color=NAVY)
add_text(s, 0.5, 1.95, 12.3, 1.5,
         "IoT devices (cameras, routers, smart home gear) are easy targets for hackers. "
         "Once infected, they become part of botnets used to launch DDoS attacks, "
         "steal data, and spread further malware. Detecting these infections by hand is impossible "
         "at the scale of modern networks.",
         size=16)

add_text(s, 0.5, 3.5, 12.3, 0.5, "Our Goal", size=22, bold=True, color=NAVY)
add_bullets(s, 0.5, 4.0, 12.3, 3,
            ["Build an automated system that classifies IoT network connections "
             "as benign or malicious",
             "Identify which features (bytes, packets, ports, etc.) most strongly "
             "indicate an attack",
             "Run the entire pipeline on the ASAX supercomputer using a Linux shell script",
             "Achieve high accuracy on real-world malware traffic"],
            size=16)


# ============================================================
# Slide 3 - Dataset Overview
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Dataset: IoT-23")

add_text(s, 0.5, 1.4, 12.3, 0.5,
         "Real network traffic from 23 IoT device infection scenarios",
         size=18, bold=True, color=NAVY)

add_bullets(s, 0.5, 2.1, 12.3, 4,
            ["Source: Stratosphere Laboratory, Czech Technical University (CTU)",
             "1.88 million labeled network connections",
             "Captured from real malware infections — not simulated",
             "Includes Mirai, Torii, and Hajime botnet families",
             "23 capture scenarios + benign IoT device traffic",
             "Format: CSV files with 37 features per connection"],
            size=16)

add_text(s, 0.5, 6.4, 12.3, 0.5,
         "Link:  https://www.stratosphereips.org/datasets-iot23",
         size=14, color=GRAY)


# ============================================================
# Slide 4 - Attack Categories
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "What We're Detecting")

# Left side - text table
data = [
    ("Benign",  "120,499",  "Normal IoT device traffic"),
    ("DDoS",    "1,643,228","Distributed denial of service flood attacks"),
    ("PortScan","74,139",   "Scanning for open ports / vulnerable services"),
    ("C&C",     "22,502",   "Command & Control - infected device 'phones home'"),
    ("Botnet",  "15,252",   "Mirai/Okiru botnet propagation"),
    ("Attack",  "9,366",    "Other generic attacks"),
]
table_shape = s.shapes.add_table(len(data) + 1, 3, Inches(0.5), Inches(1.5),
                                  Inches(12.3), Inches(4.5)).table
headers = ["Category", "Connections", "Description"]
for i, h in enumerate(headers):
    cell = table_shape.cell(0, i)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = WHITE

for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        cell = table_shape.cell(r, c)
        cell.text = val
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(14)
        p.font.color.rgb = GRAY

add_text(s, 0.5, 6.4, 12.3, 0.5,
         "Heavily imbalanced — 93.6% of traffic is malicious (mostly DDoS)",
         size=14, color=RED, bold=True)


# ============================================================
# Slide 5 - Methodology
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Methodology — The Pipeline")

steps = [
    ("1.  Load",          "Read 23 CSV files, combine into 1.88M-row dataset"),
    ("2.  Preprocess",    "Drop dead columns, fill missing values, encode labels"),
    ("3.  Explore",       "Generate distribution charts and protocol breakdowns"),
    ("4.  Split",         "70% training (1.32M rows) / 30% testing (565K rows)"),
    ("5.  Train",         "Random Forest classifier — 100 decision trees"),
    ("6.  Evaluate",      "Accuracy, precision, recall, confusion matrix"),
    ("7.  Visualize",     "Save all results as PNGs in results/ folder"),
]

for i, (label, desc) in enumerate(steps):
    y = 1.5 + i * 0.7
    add_text(s, 0.8, y, 2.5, 0.5, label, size=18, bold=True, color=NAVY)
    add_text(s, 3.4, y, 9.5, 0.5, desc, size=16)

add_text(s, 0.5, 6.7, 12.3, 0.4,
         "Tools: Python 3 • pandas • scikit-learn • matplotlib • seaborn",
         size=13, color=GRAY, align=PP_ALIGN.CENTER)


# ============================================================
# Slide 6 - Data Distribution
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Exploratory Data Analysis")

if os.path.exists(f"{RESULTS}/attack_distribution.png"):
    s.shapes.add_picture(f"{RESULTS}/attack_distribution.png",
                         Inches(0.3), Inches(1.4), height=Inches(5.5))
if os.path.exists(f"{RESULTS}/benign_vs_malicious.png"):
    s.shapes.add_picture(f"{RESULTS}/benign_vs_malicious.png",
                         Inches(7.0), Inches(1.4), height=Inches(5.5))

add_text(s, 0.5, 6.9, 12.3, 0.4,
         "Massive class imbalance — model must work hard to recognize benign traffic",
         size=13, color=GRAY, align=PP_ALIGN.CENTER)


# ============================================================
# Slide 7 - Model Performance
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Results — Random Forest Performance")

if os.path.exists(f"{RESULTS}/confusion_matrix.png"):
    s.shapes.add_picture(f"{RESULTS}/confusion_matrix.png",
                         Inches(0.3), Inches(1.4), height=Inches(5.0))

# Metrics on the right
add_text(s, 7.0, 1.5, 6, 0.5, "Final Metrics", size=22, bold=True, color=NAVY)

metrics = [
    ("Accuracy",        "97.87%"),
    ("Benign F1",       "0.83"),
    ("Malicious F1",    "0.99"),
    ("Training Time",   "23.4s"),
    ("Prediction Time", "0.7s"),
    ("Test Samples",    "565,502"),
]
for i, (label, val) in enumerate(metrics):
    y = 2.3 + i * 0.55
    add_text(s, 7.0, y, 3.5, 0.4, label, size=16, color=GRAY)
    add_text(s, 10.5, y, 2.5, 0.4, val, size=16, bold=True, color=NAVY)

add_text(s, 0.3, 6.6, 12.7, 0.4,
         "97.87% of all 565,502 test connections classified correctly",
         size=14, color=RED, bold=True, align=PP_ALIGN.CENTER)


# ============================================================
# Slide 8 - Feature Importances
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Which Features Matter Most?")

if os.path.exists(f"{RESULTS}/feature_importances.png"):
    s.shapes.add_picture(f"{RESULTS}/feature_importances.png",
                         Inches(0.3), Inches(1.4), height=Inches(5.5))

add_text(s, 7.5, 1.6, 5.5, 0.5, "Key Insight", size=22, bold=True, color=NAVY)
add_text(s, 7.5, 2.3, 5.5, 4,
         "The model learned that traffic volume features "
         "(orig_pkts, orig_ip_bytes, resp_bytes) are the strongest "
         "indicators of an attack.\n\n"
         "This matches real-world intuition: DDoS and port-scan "
         "attacks send unusual volumes of small packets, while "
         "C&C traffic shows distinctive byte patterns.",
         size=15)


# ============================================================
# Slide 9 - Linux / ASAX Workflow
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Running on ASAX Supercomputer")

add_text(s, 0.5, 1.4, 12.3, 0.5,
         "One shell script handles everything", size=20, bold=True, color=NAVY)

add_bullets(s, 0.5, 2.0, 12.3, 4,
            ["Loads required Python modules via 'module load python3'",
             "Installs dependencies (pandas, scikit-learn, matplotlib, seaborn)",
             "Auto-downloads IoT-23 dataset from Kaggle",
             "Combines 23 CSV files into one dataset",
             "Runs the Python analysis pipeline",
             "Saves all charts and reports to results/ folder"],
            size=16)

add_text(s, 0.5, 5.2, 12.3, 0.4, "Submit to ASAX scheduler:",
         size=16, bold=True, color=NAVY)
add_text(s, 0.5, 5.7, 12.3, 0.4, "    sbatch run_analysis.sh",
         size=18, color=RED)

add_text(s, 0.5, 6.4, 12.3, 0.4, "Or run interactively:",
         size=16, bold=True, color=NAVY)
add_text(s, 0.5, 6.85, 12.3, 0.4, "    bash run_analysis.sh",
         size=18, color=RED)


# ============================================================
# Slide 10 - Conclusion / Demo
# ============================================================
s = prs.slides.add_slide(BLANK)
add_title_bar(s, "Conclusion & Demo")

add_text(s, 0.5, 1.4, 12.3, 0.5, "What We Built", size=22, bold=True, color=NAVY)
add_bullets(s, 0.5, 2.0, 12.3, 2,
            ["A complete ML pipeline that detects IoT botnet attacks at 97.87% accuracy",
             "An automated Linux shell script ready for ASAX deployment",
             "Visual analysis of 1.88M network connections from real malware infections"],
            size=16)

add_text(s, 0.5, 4.2, 12.3, 0.5, "Why It Matters", size=22, bold=True, color=NAVY)
add_text(s, 0.5, 4.8, 12.3, 1.5,
         "IoT security is one of the fastest growing threats in cybersecurity. "
         "The same techniques used here protect real networks from real attacks.",
         size=16)

add_text(s, 0.5, 6.6, 12.3, 0.5,
         "Live Demo  →  github.com/ibrahimt39/AAMU-Linux-Project",
         size=18, bold=True, color=RED, align=PP_ALIGN.CENTER)


prs.save(OUT)
print(f"Saved: {OUT}  ({len(prs.slides)} slides)")
