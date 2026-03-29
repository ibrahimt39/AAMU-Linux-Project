#!/usr/bin/env python3
"""Generate Task1_Submission.pdf from scratch using fpdf2."""
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Title
pdf.set_font("Helvetica", "B", 18)
pdf.cell(0, 12, "Team Project Submission - Task #1", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# Divider
pdf.set_draw_color(60, 60, 60)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)

# --- Team Members ---
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "Team Members", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

pdf.set_font("Helvetica", "", 11)
members = [
    ("1", "Ibrahim Traore"),
    ("2", ""),
    ("3", ""),
    ("4", ""),
    ("5", "(optional)"),
]
pdf.set_fill_color(220, 220, 220)
pdf.set_font("Helvetica", "B", 11)
pdf.cell(15, 8, "#", border=1, fill=True, align="C")
pdf.cell(80, 8, "Name", border=1, fill=True, align="C")
pdf.ln()
pdf.set_font("Helvetica", "", 11)
for num, name in members:
    pdf.cell(15, 8, num, border=1, align="C")
    pdf.cell(80, 8, name, border=1)
    pdf.ln()
pdf.ln(6)

# --- Selected Topic Area ---
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "Selected Topic Area", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(0, 80, 160)
pdf.cell(0, 8, "Cybersecurity", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(6)

# --- Dataset Selected ---
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "Dataset Selected", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

info = [
    ("Dataset Name", "IoT-23: A Labeled Dataset of IoT Network Traffic"),
    ("Source", "Stratosphere Laboratory, Czech Technical University (CTU)"),
    ("Format", "CSV (Zeek/Bro connection logs), ~50-200 MB (preprocessed)"),
    ("Dataset Link", "https://www.stratosphereips.org/datasets-iot23"),
    ("Kaggle Mirror", "https://www.kaggle.com/datasets/arbazkhan971/iot23-dataset"),
]
pdf.set_font("Helvetica", "B", 11)
pdf.cell(40, 8, "Field", border=1, fill=True, align="C")
pdf.cell(145, 8, "Details", border=1, fill=True, align="C")
pdf.ln()
pdf.set_font("Helvetica", "", 10)
for field, detail in info:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 8, field, border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(145, 8, detail, border=1)
    pdf.ln()
pdf.ln(6)

# --- Description ---
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Description", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", "", 11)
desc = (
    "The IoT-23 dataset contains real network traffic captured from 23 IoT device "
    "infection scenarios involving active malware families such as Mirai, Torii, and "
    "Hajime botnets, alongside benign IoT device traffic. Each network connection is "
    "labeled with its traffic type (benign, malicious) and specific attack category "
    "(DDoS, C&C communication, port scan, etc.). It was produced by the Stratosphere "
    "Research Laboratory at Czech Technical University in Prague and is backed by "
    "published academic research."
)
pdf.multi_cell(0, 6, desc)
pdf.ln(4)

# --- Why This Dataset ---
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Why This Dataset", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", "", 11)
reasons = [
    "Real-world data - captured from actual malware infections on real IoT devices, not synthetic traffic.",
    "Modern and relevant - IoT security is one of the fastest-growing areas in cybersecurity.",
    "Multi-class labels - specific attack types (DDoS, C&C, port scan), not just binary classification.",
    "Well-documented - published by a respected research lab with accompanying papers.",
    "Manageable size - preprocessed CSV versions are 50-200 MB, suitable for supercomputer nodes.",
]
for r in reasons:
    pdf.cell(5, 6, "-")
    pdf.multi_cell(0, 6, " " + r)
    pdf.ln(1)
pdf.ln(4)

# --- Key Features ---
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Key Features", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

features = [
    ("duration", "Length of the connection"),
    ("proto", "Transport protocol (TCP, UDP, ICMP)"),
    ("service", "Application protocol (HTTP, DNS, SSH, etc.)"),
    ("src_bytes", "Bytes sent from source"),
    ("dst_bytes", "Bytes sent from destination"),
    ("conn_state", "Connection state (S0, SF, REJ, etc.)"),
    ("src_pkts", "Packets sent from source"),
    ("dst_pkts", "Packets sent from destination"),
    ("label", "Traffic classification (Benign / Malicious)"),
    ("detailed_label", "Specific attack type (DDoS, C&C, PortScan, etc.)"),
]
pdf.set_font("Helvetica", "B", 10)
pdf.set_fill_color(220, 220, 220)
pdf.cell(40, 8, "Feature", border=1, fill=True, align="C")
pdf.cell(130, 8, "Description", border=1, fill=True, align="C")
pdf.ln()
pdf.set_font("Helvetica", "", 10)
for feat, desc in features:
    pdf.set_font("Courier", "", 10)
    pdf.cell(40, 7, feat, border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(130, 7, desc, border=1)
    pdf.ln()
pdf.ln(6)

# --- Attack Scenarios ---
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Attack Scenarios", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

attacks = [
    ("Mirai", "DDoS, C&C, port scanning"),
    ("Torii", "C&C communication, data exfiltration"),
    ("Hajime", "P2P botnet propagation, scanning"),
    ("Benign", "Normal IoT device traffic"),
]
pdf.set_font("Helvetica", "B", 10)
pdf.set_fill_color(220, 220, 220)
pdf.cell(40, 8, "Malware Family", border=1, fill=True, align="C")
pdf.cell(120, 8, "Attack Types", border=1, fill=True, align="C")
pdf.ln()
pdf.set_font("Helvetica", "", 10)
for family, types in attacks:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 7, family, border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(120, 7, types, border=1)
    pdf.ln()
pdf.ln(6)

# --- Planned Approach ---
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "Planned Approach", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", "", 11)
steps = [
    "Load and clean the dataset with Python (pandas).",
    "Explore traffic patterns, protocol distributions, and attack breakdowns (matplotlib / seaborn).",
    "Train a Random Forest classifier to detect and categorize IoT botnet traffic.",
    "Evaluate with accuracy, precision, recall, F1-score, and a confusion matrix.",
    "Wrap the pipeline in a Linux shell script for the ASAX supercomputer.",
]
for i, step in enumerate(steps, 1):
    pdf.cell(0, 7, f"  {i}. {step}", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# --- Deliverables ---
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Deliverables", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

deliverables = [
    ("Python data processing program", "iot_intrusion_detection.py"),
    ("Linux shell script (ASAX launcher)", "run_analysis.sh"),
    ("Results / visualizations", "results/ directory (generated at runtime)"),
]
pdf.set_font("Helvetica", "B", 10)
pdf.set_fill_color(220, 220, 220)
pdf.cell(70, 8, "Deliverable", border=1, fill=True, align="C")
pdf.cell(90, 8, "File", border=1, fill=True, align="C")
pdf.ln()
pdf.set_font("Helvetica", "", 10)
for d, f in deliverables:
    pdf.cell(70, 7, d, border=1)
    pdf.set_font("Courier", "", 10)
    pdf.cell(90, 7, f, border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln()
pdf.ln(6)

# --- Programming Language ---
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "Programming Language", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, "Python 3 (with pandas, numpy, scikit-learn, matplotlib, seaborn)", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)

# Footer
pdf.set_font("Helvetica", "I", 9)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 6, "Prepared for CS Linux Course - Alabama A&M University", align="C")

pdf.output("Task1_Submission.pdf")
print("PDF generated: Task1_Submission.pdf")
