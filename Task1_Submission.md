# Team Project Submission -- Task #1

---

## Team Members

| #   | Name       |
|-----|------------|
| 1   | Ibrahim Traore |
| 2   |            |
| 3   |            |
| 4   |            |
| 5   | *(optional)* |

---

## Selected Topic Area

> **Cybersecurity**

---

## Dataset Selected

| Field            | Details |
|------------------|---------|
| **Dataset Name** | IoT-23: A Labeled Dataset of IoT Network Traffic |
| **Source**        | Stratosphere Laboratory, Czech Technical University (CTU) |
| **Format**       | CSV (Zeek/Bro connection logs), ~50-200 MB (preprocessed) |
| **Dataset Link** | https://www.stratosphereips.org/datasets-iot23 |
| **Kaggle Mirror** | https://www.kaggle.com/datasets/arbazkhan971/iot23-dataset |

### Description

The IoT-23 dataset contains real network traffic captured from 23 IoT device infection scenarios involving active malware families such as **Mirai**, **Torii**, and **Hajime** botnets, alongside benign IoT device traffic. Each network connection is labeled with its traffic type (benign, malicious) and specific attack category (DDoS, C&C communication, port scan, etc.). It was produced by the Stratosphere Research Laboratory at Czech Technical University in Prague and is backed by published academic research.

### Why This Dataset

- **Real-world data** -- captured from actual malware infections running on real IoT devices, not synthetic or simulated traffic.
- **Modern and relevant** -- IoT security is one of the fastest-growing areas in cybersecurity; Mirai-style botnets remain a top threat.
- **Multi-class labels** -- goes beyond simple normal/attack binary classification with specific attack types (DDoS, C&C, port scan, etc.).
- **Well-documented** -- published by a respected research lab with accompanying papers and documentation.
- **Manageable size** -- preprocessed CSV versions are 50-200 MB, suitable for processing on supercomputer nodes.

### Key Features

| Feature          | Description |
|------------------|-------------|
| `duration`       | Length of the connection |
| `proto`          | Transport protocol (TCP, UDP, ICMP) |
| `service`        | Application protocol (HTTP, DNS, SSH, etc.) |
| `src_bytes`      | Bytes sent from source |
| `dst_bytes`      | Bytes sent from destination |
| `conn_state`     | Connection state (S0, SF, REJ, etc.) |
| `missed_bytes`   | Bytes missed in content gaps |
| `src_pkts`       | Packets sent from source |
| `dst_pkts`       | Packets sent from destination |
| `label`          | Traffic classification (Benign / Malicious) |
| `detailed_label` | Specific attack type (DDoS, C&C, PortScan, etc.) |

### Attack Scenarios

| Malware Family | Attack Types                        |
|----------------|-------------------------------------|
| **Mirai**      | DDoS, C&C, port scanning            |
| **Torii**      | C&C communication, data exfiltration |
| **Hajime**     | P2P botnet propagation, scanning    |
| **Benign**     | Normal IoT device traffic           |

---

## Planned Approach

1. **Load and clean** the dataset with Python (pandas).
2. **Explore** traffic patterns, protocol distributions, and attack breakdowns (matplotlib / seaborn).
3. **Train** a Random Forest classifier to detect and categorize IoT botnet traffic.
4. **Evaluate** with accuracy, precision, recall, F1-score, and a confusion matrix.
5. **Wrap** the pipeline in a Linux shell script that loads the required modules on the ASAX supercomputer and launches the Python program.

### Deliverables

| Deliverable | File |
|-------------|------|
| Python data processing program | `iot_intrusion_detection.py` |
| Linux shell script (ASAX launcher) | `run_analysis.sh` |
| Results / visualizations | `results/` directory (generated at runtime) |

---

## Programming Language

> **Python 3** (with pandas, numpy, scikit-learn, matplotlib, seaborn)

---

*Prepared for CS Linux Course -- Alabama A&M University*
