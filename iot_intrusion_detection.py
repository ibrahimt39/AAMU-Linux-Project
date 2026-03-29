#!/usr/bin/env python3
"""
IoT-23 Botnet Traffic Detection
Dataset: IoT-23 (Stratosphere Laboratory, Czech Technical University)
Course: Linux Team Project - Alabama A&M University

Analyzes real IoT network traffic to detect and classify botnet attacks
(Mirai, Torii, Hajime) using a Random Forest classifier.
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


# Columns to drop (no predictive value or entirely null)
DROP_COLS = ['ts', 'uid', 'id.orig_h', 'id.resp_h', 'local_orig',
             'local_resp', 'tunnel_parents']

# Categorical columns that need encoding
CAT_COLS = ['proto', 'service', 'conn_state', 'history']


def load_dataset(filepath):
    """Load the IoT-23 dataset CSV."""
    print(f"Loading dataset from: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    return df


def preprocess(df):
    """Clean and prepare the dataset for analysis."""
    print("\n--- Preprocessing ---")

    # Standardize column names (handle both hyphen and underscore variants)
    df.columns = df.columns.str.strip().str.replace('-', '_')

    # Drop columns with no predictive value
    cols_to_drop = [c for c in DROP_COLS if c.replace('-', '_') in df.columns]
    cols_to_drop = [c.replace('-', '_') for c in cols_to_drop]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    print(f"Dropped columns: {cols_to_drop}")

    # Replace Zeek's '-' placeholder with NaN
    df.replace('-', np.nan, inplace=True)

    # Convert numeric columns
    numeric_cols = ['duration', 'orig_bytes', 'resp_bytes', 'missed_bytes',
                    'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes',
                    'id.orig_p', 'id.resp_p']
    for col in numeric_cols:
        col_clean = col.replace('-', '_').replace('.', '_')
        # Try both naming conventions
        for c in [col, col.replace('-', '_'), col.replace('.', '_')]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
                break

    # Fill missing numeric values with 0
    df.fillna(0, inplace=True)

    # Create simplified attack category from the label column
    if 'label' in df.columns:
        label_col = 'label'
    elif 'detailed_label' in df.columns:
        label_col = 'detailed_label'
    else:
        print("ERROR: No label column found.")
        sys.exit(1)

    # Map to broad categories
    def categorize(label):
        label = str(label).lower()
        if 'benign' in label:
            return 'Benign'
        elif 'ddos' in label:
            return 'DDoS'
        elif 'c&c' in label or 'c_c' in label:
            return 'C&C'
        elif 'scan' in label or 'portscan' in label:
            return 'PortScan'
        elif 'okiru' in label or 'mirai' in label:
            return 'Botnet'
        elif 'filedownload' in label:
            return 'FileDownload'
        elif 'attack' in label:
            return 'Attack'
        else:
            return 'Other'

    df['attack_category'] = df[label_col].apply(categorize)
    df['is_attack'] = (df['attack_category'] != 'Benign').astype(int)

    print(f"\nLabel distribution:")
    print(df['attack_category'].value_counts())
    print(f"\nBenign: {(df['is_attack'] == 0).sum():,}  |  Malicious: {(df['is_attack'] == 1).sum():,}")

    return df


def exploratory_analysis(df, output_dir):
    """Generate EDA visualizations."""
    print("\n--- Exploratory Data Analysis ---")

    # 1. Attack category distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    counts = df['attack_category'].value_counts()
    colors = ['#2ecc71' if cat == 'Benign' else '#e74c3c' for cat in counts.index]
    counts.plot(kind='bar', ax=ax, color=colors)
    ax.set_title('Distribution of Traffic Categories', fontsize=14, fontweight='bold')
    ax.set_xlabel('Category')
    ax.set_ylabel('Number of Connections')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'attack_distribution.png'), dpi=150)
    print(f"Saved: attack_distribution.png")
    plt.close(fig)

    # 2. Protocol distribution by attack type
    fig, ax = plt.subplots(figsize=(10, 6))
    if 'proto' in df.columns:
        ct = pd.crosstab(df['attack_category'], df['proto'])
        ct.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
        ax.set_title('Protocol Distribution by Attack Category', fontsize=14, fontweight='bold')
        ax.set_xlabel('Attack Category')
        ax.set_ylabel('Count')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.legend(title='Protocol')
        plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'protocol_by_attack.png'), dpi=150)
    print(f"Saved: protocol_by_attack.png")
    plt.close(fig)

    # 3. Benign vs Malicious pie chart
    fig, ax = plt.subplots(figsize=(7, 7))
    benign_count = (df['is_attack'] == 0).sum()
    attack_count = (df['is_attack'] == 1).sum()
    ax.pie([benign_count, attack_count],
           labels=['Benign', 'Malicious'],
           autopct='%1.1f%%',
           colors=['#2ecc71', '#e74c3c'],
           startangle=90,
           textprops={'fontsize': 13})
    ax.set_title('Benign vs Malicious Traffic', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'benign_vs_malicious.png'), dpi=150)
    print(f"Saved: benign_vs_malicious.png")
    plt.close(fig)

    # 4. Top destination ports targeted
    port_col = None
    for c in ['id.resp_p', 'id_resp_p', 'resp_p']:
        if c in df.columns:
            port_col = c
            break
    if port_col:
        fig, ax = plt.subplots(figsize=(10, 6))
        top_ports = df[df['is_attack'] == 1][port_col].value_counts().head(15)
        top_ports.plot(kind='barh', ax=ax, color='#3498db')
        ax.set_title('Top 15 Destination Ports Targeted by Attacks', fontsize=14, fontweight='bold')
        ax.set_xlabel('Number of Attacks')
        ax.set_ylabel('Port')
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, 'top_ports_attacked.png'), dpi=150)
        print(f"Saved: top_ports_attacked.png")
        plt.close(fig)


def train_model(df, output_dir):
    """Train a Random Forest classifier for binary intrusion detection."""
    print("\n--- Training Random Forest Model ---")

    # Prepare features: drop label columns and non-numeric identifiers
    exclude = ['label', 'detailed_label', 'attack_category', 'is_attack']
    feature_cols = [c for c in df.columns if c not in exclude]

    df_model = df.copy()

    # Encode categorical columns
    encoders = {}
    for col in feature_cols:
        if df_model[col].dtype == 'object':
            le = LabelEncoder()
            df_model[col] = le.fit_transform(df_model[col].astype(str))
            encoders[col] = le

    X = df_model[feature_cols]
    y = df_model['is_attack']

    # Split 70/30
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    print(f"Training: {X_train.shape[0]:,} samples")
    print(f"Testing:  {X_test.shape[0]:,} samples")

    # Train
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}")
    print("\nClassification Report:")
    report = classification_report(y_test, y_pred, target_names=['Benign', 'Malicious'])
    print(report)

    # Save report
    report_path = os.path.join(output_dir, 'classification_report.txt')
    with open(report_path, 'w') as f:
        f.write("IoT-23 Intrusion Detection - Classification Report\n")
        f.write("=" * 55 + "\n")
        f.write(f"Model: Random Forest (100 trees)\n")
        f.write(f"Features: {len(feature_cols)}\n")
        f.write(f"Training samples: {X_train.shape[0]:,}\n")
        f.write(f"Testing samples: {X_test.shape[0]:,}\n")
        f.write(f"Accuracy: {acc:.4f}\n\n")
        f.write(report)
    print(f"Saved: {report_path}")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt=',d', cmap='Blues',
                xticklabels=['Benign', 'Malicious'],
                yticklabels=['Benign', 'Malicious'], ax=ax)
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=150)
    print(f"Saved: confusion_matrix.png")
    plt.close(fig)

    # Feature importances (top 15)
    importances = clf.feature_importances_
    indices = np.argsort(importances)[-15:]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(range(len(indices)), importances[indices], color='#1abc9c')
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_cols[i] for i in indices])
    ax.set_title('Top 15 Feature Importances', fontsize=14, fontweight='bold')
    ax.set_xlabel('Importance')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'feature_importances.png'), dpi=150)
    print(f"Saved: feature_importances.png")
    plt.close(fig)

    return clf, acc


def main():
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = 'iot23_dataset.csv'

    if not os.path.isfile(dataset_path):
        print(f"ERROR: Dataset file not found: {dataset_path}")
        print("Usage: python3 iot_intrusion_detection.py [path/to/iot23_dataset.csv]")
        print("\nDownload from: https://www.kaggle.com/datasets/arbazkhan971/iot23-dataset")
        sys.exit(1)

    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)

    df = load_dataset(dataset_path)
    df = preprocess(df)
    exploratory_analysis(df, output_dir)
    model, accuracy = train_model(df, output_dir)

    print(f"\n{'=' * 55}")
    print(f"  Analysis complete. Results saved to '{output_dir}/'")
    print(f"  Final model accuracy: {accuracy:.4f}")
    print(f"{'=' * 55}")


if __name__ == '__main__':
    main()
