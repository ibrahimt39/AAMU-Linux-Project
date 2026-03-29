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
import time
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


def load_dataset(filepath):
    """Load the IoT-23 dataset CSV (supports both raw and pre-processed formats)."""
    print(f"Loading dataset from: {filepath}")

    # Detect delimiter by reading first line
    with open(filepath, 'r') as f:
        header = f.readline()
    sep = '|' if '|' in header else ','

    df = pd.read_csv(filepath, sep=sep, low_memory=False)
    print(f"Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
    return df


def preprocess(df):
    """Clean and prepare the dataset for analysis."""
    print("\n--- Preprocessing ---")

    # Standardize column names
    df.columns = df.columns.str.strip().str.replace('-', '_')

    # Drop index column if present
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)

    # Detect format: pre-processed (has multi_label) vs raw (has detailed_label)
    is_preprocessed = 'multi_label' in df.columns

    if is_preprocessed:
        # Pre-processed format: label is already binary (0/1), multi_label has attack names
        print("Detected: pre-processed format (one-hot encoded)")

        # Drop columns with no predictive value
        drop_cols = ['local_orig', 'local_resp', 'tunnel_parents']
        df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

        # Replace '-' with 0 and ensure numeric
        df.replace('-', 0, inplace=True)
        for col in df.columns:
            if col not in ['label', 'multi_label']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df.fillna(0, inplace=True)

        # Rename for consistency
        df.rename(columns={'label': 'is_attack', 'multi_label': 'detailed_label'}, inplace=True)
    else:
        # Raw format: needs full preprocessing
        print("Detected: raw format")
        drop_cols = ['ts', 'uid', 'id.orig_h', 'id.resp_h', 'local_orig',
                     'local_resp', 'tunnel_parents']
        df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

        df.replace('-', np.nan, inplace=True)
        for col in df.select_dtypes(include=['object']).columns:
            if col not in ['proto', 'service', 'conn_state', 'history',
                           'label', 'detailed_label']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df.fillna(0, inplace=True)

        label_col = 'detailed_label' if 'detailed_label' in df.columns else 'label'
        df.rename(columns={label_col: 'detailed_label'}, inplace=True)

        # Create binary attack label
        df['is_attack'] = df['detailed_label'].apply(
            lambda x: 0 if str(x).lower() == 'benign' else 1
        )

    # Map detailed labels to broad categories
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

    df['attack_category'] = df['detailed_label'].apply(categorize)

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
    print("Saved: attack_distribution.png")
    plt.close(fig)

    # 2. Protocol distribution by attack type
    fig, ax = plt.subplots(figsize=(10, 6))
    proto_cols = [c for c in df.columns if c.startswith('proto_')]
    if proto_cols:
        proto_data = df[proto_cols].copy()
        proto_data.columns = [c.replace('proto_', '').upper() for c in proto_cols]
        proto_data['attack_category'] = df['attack_category']
        ct = proto_data.groupby('attack_category')[proto_data.columns[:-1]].sum()
        ct.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
    elif 'proto' in df.columns:
        ct = pd.crosstab(df['attack_category'], df['proto'])
        ct.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
    ax.set_title('Protocol Distribution by Attack Category', fontsize=14, fontweight='bold')
    ax.set_xlabel('Attack Category')
    ax.set_ylabel('Count')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(title='Protocol')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'protocol_by_attack.png'), dpi=150)
    print("Saved: protocol_by_attack.png")
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
    print("Saved: benign_vs_malicious.png")
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
        print("Saved: top_ports_attacked.png")
        plt.close(fig)


def train_model(df, output_dir):
    """Train and evaluate a Random Forest classifier."""
    print("\n--- Preparing Features ---")

    exclude = ['label', 'detailed_label', 'multi_label', 'attack_category', 'is_attack']
    feature_cols = [c for c in df.columns if c not in exclude]

    df_model = df.copy()

    # Encode categorical columns
    for col in feature_cols:
        if df_model[col].dtype == 'object':
            le = LabelEncoder()
            df_model[col] = le.fit_transform(df_model[col].astype(str))

    X = df_model[feature_cols]
    y = df_model['is_attack']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    print(f"Training: {X_train.shape[0]:,} samples")
    print(f"Testing:  {X_test.shape[0]:,} samples")
    print(f"Features: {len(feature_cols)}")

    # Train Random Forest
    print("\n--- Training Random Forest (100 trees) ---")
    start = time.time()
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    train_time = time.time() - start

    start = time.time()
    y_pred = clf.predict(X_test)
    predict_time = time.time() - start

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Benign', 'Malicious'])
    print(f"Accuracy:      {acc:.4f}")
    print(f"Training time: {train_time:.2f}s")
    print(f"Predict time:  {predict_time:.2f}s")
    print("\nClassification Report:")
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
        f.write(f"Accuracy: {acc:.4f}\n")
        f.write(f"Training time: {train_time:.2f}s\n")
        f.write(f"Prediction time: {predict_time:.2f}s\n\n")
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
    print("Saved: confusion_matrix.png")
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
    print("Saved: feature_importances.png")
    plt.close(fig)

    return clf, acc


def main():
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = 'iot23_combined.csv'

    if not os.path.isfile(dataset_path):
        print(f"ERROR: Dataset file not found: {dataset_path}")
        print("Usage: python3 iot_intrusion_detection.py [path/to/iot23_combined.csv]")
        print("\nDownload: kaggle datasets download -d srifqi/iot-23-cleaned-data")
        sys.exit(1)

    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)

    df = load_dataset(dataset_path)
    df = preprocess(df)
    exploratory_analysis(df, output_dir)
    model, accuracy = train_model(df, output_dir)

    print(f"\n{'=' * 55}")
    print(f"  Analysis complete. Results saved to '{output_dir}/'")
    print(f"  Model accuracy: {accuracy:.4f}")
    print(f"{'=' * 55}")


if __name__ == '__main__':
    main()
