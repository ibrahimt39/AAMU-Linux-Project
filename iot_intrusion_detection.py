#!/usr/bin/env python3
"""
IoT-23 Botnet Traffic Detection
Dataset: IoT-23 (Stratosphere Laboratory, Czech Technical University)
Course: Linux Team Project - Alabama A&M University

Analyzes real IoT network traffic to detect and classify botnet attacks
(Mirai, Torii, Hajime) using Random Forest vs Neural Network comparison.
"""

import sys
import os
import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
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


def prepare_features(df):
    """Encode categorical columns and split into train/test sets."""
    exclude = ['label', 'detailed_label', 'attack_category', 'is_attack']
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

    return X_train, X_test, y_train, y_test, feature_cols


def train_random_forest(X_train, X_test, y_train, y_test, feature_cols, output_dir):
    """Train and evaluate a Random Forest classifier."""
    print("\n--- Random Forest (100 trees) ---")

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
    print(report)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt=',d', cmap='Blues',
                xticklabels=['Benign', 'Malicious'],
                yticklabels=['Benign', 'Malicious'], ax=ax)
    ax.set_title('Random Forest - Confusion Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'rf_confusion_matrix.png'), dpi=150)
    print(f"Saved: rf_confusion_matrix.png")
    plt.close(fig)

    # Feature importances (top 15)
    importances = clf.feature_importances_
    indices = np.argsort(importances)[-15:]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(range(len(indices)), importances[indices], color='#1abc9c')
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_cols[i] for i in indices])
    ax.set_title('Random Forest - Top 15 Feature Importances', fontsize=14, fontweight='bold')
    ax.set_xlabel('Importance')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'rf_feature_importances.png'), dpi=150)
    print("Saved: rf_feature_importances.png")
    plt.close(fig)

    return acc, train_time, predict_time, report, cm


def train_neural_network(X_train, X_test, y_train, y_test, output_dir):
    """Train and evaluate a Neural Network (MLP) classifier."""
    print("\n--- Neural Network (3-layer MLP) ---")

    # Neural networks need scaled features (all values in similar range)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Architecture: 128 -> 64 -> 32 neurons, ReLU activation
    start = time.time()
    nn = MLPClassifier(
        hidden_layer_sizes=(128, 64, 32),
        activation='relu',
        max_iter=200,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )
    nn.fit(X_train_scaled, y_train)
    train_time = time.time() - start

    start = time.time()
    y_pred = nn.predict(X_test_scaled)
    predict_time = time.time() - start

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Benign', 'Malicious'])
    print(f"Accuracy:      {acc:.4f}")
    print(f"Training time: {train_time:.2f}s")
    print(f"Predict time:  {predict_time:.2f}s")
    print(report)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt=',d', cmap='Oranges',
                xticklabels=['Benign', 'Malicious'],
                yticklabels=['Benign', 'Malicious'], ax=ax)
    ax.set_title('Neural Network - Confusion Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'nn_confusion_matrix.png'), dpi=150)
    print(f"Saved: nn_confusion_matrix.png")
    plt.close(fig)

    # Training loss curve
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(nn.loss_curve_, color='#e74c3c', linewidth=2)
    ax.set_title('Neural Network - Training Loss Curve', fontsize=14, fontweight='bold')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Loss')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'nn_loss_curve.png'), dpi=150)
    print("Saved: nn_loss_curve.png")
    plt.close(fig)

    return acc, train_time, predict_time, report, cm


def compare_models(rf_results, nn_results, output_dir):
    """Generate side-by-side comparison chart and report."""
    rf_acc, rf_train, rf_pred, rf_report, rf_cm = rf_results
    nn_acc, nn_train, nn_pred, nn_report, nn_cm = nn_results

    print("\n" + "=" * 60)
    print("  MODEL COMPARISON: Random Forest vs Neural Network")
    print("=" * 60)
    print(f"{'Metric':<25} {'Random Forest':>15} {'Neural Network':>15}")
    print("-" * 60)
    print(f"{'Accuracy':<25} {rf_acc:>14.4f} {nn_acc:>14.4f}")
    print(f"{'Training Time':<25} {rf_train:>13.2f}s {nn_train:>13.2f}s")
    print(f"{'Prediction Time':<25} {rf_pred:>13.2f}s {nn_pred:>13.2f}s")
    print(f"{'Explainable?':<25} {'Yes':>15} {'No (black box)':>15}")
    print("-" * 60)

    winner = "Random Forest" if rf_acc >= nn_acc else "Neural Network"
    faster = "Random Forest" if rf_train <= nn_train else "Neural Network"
    print(f"  Higher accuracy: {winner}")
    print(f"  Faster training: {faster}")
    print("=" * 60)

    # Save comparison report
    report_path = os.path.join(output_dir, 'model_comparison.txt')
    with open(report_path, 'w') as f:
        f.write("IoT-23 Intrusion Detection - Model Comparison\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Metric':<25} {'Random Forest':>15} {'Neural Network':>15}\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Accuracy':<25} {rf_acc:>14.4f} {nn_acc:>14.4f}\n")
        f.write(f"{'Training Time':<25} {rf_train:>13.2f}s {nn_train:>13.2f}s\n")
        f.write(f"{'Prediction Time':<25} {rf_pred:>13.2f}s {nn_pred:>13.2f}s\n")
        f.write(f"{'Explainable?':<25} {'Yes':>15} {'No (black box)':>15}\n\n")
        f.write(f"Winner (accuracy): {winner}\n")
        f.write(f"Winner (speed):    {faster}\n\n")
        f.write("--- Random Forest Report ---\n" + rf_report + "\n")
        f.write("--- Neural Network Report ---\n" + nn_report + "\n")
    print(f"Saved: {report_path}")

    # Side-by-side bar chart
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Accuracy
    axes[0].bar(['Random\nForest', 'Neural\nNetwork'], [rf_acc, nn_acc],
                color=['#1abc9c', '#e67e22'], width=0.5)
    axes[0].set_title('Accuracy', fontsize=13, fontweight='bold')
    axes[0].set_ylim(0, 1.05)
    for i, v in enumerate([rf_acc, nn_acc]):
        axes[0].text(i, v + 0.02, f"{v:.4f}", ha='center', fontweight='bold')

    # Training time
    axes[1].bar(['Random\nForest', 'Neural\nNetwork'], [rf_train, nn_train],
                color=['#1abc9c', '#e67e22'], width=0.5)
    axes[1].set_title('Training Time (seconds)', fontsize=13, fontweight='bold')
    for i, v in enumerate([rf_train, nn_train]):
        axes[1].text(i, v + max(rf_train, nn_train) * 0.03,
                     f"{v:.1f}s", ha='center', fontweight='bold')

    # Prediction time
    axes[2].bar(['Random\nForest', 'Neural\nNetwork'], [rf_pred, nn_pred],
                color=['#1abc9c', '#e67e22'], width=0.5)
    axes[2].set_title('Prediction Time (seconds)', fontsize=13, fontweight='bold')
    for i, v in enumerate([rf_pred, nn_pred]):
        axes[2].text(i, v + max(rf_pred, nn_pred) * 0.03,
                     f"{v:.2f}s", ha='center', fontweight='bold')

    plt.suptitle('Random Forest vs Neural Network', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'model_comparison.png'), dpi=150, bbox_inches='tight')
    print("Saved: model_comparison.png")
    plt.close(fig)


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

    X_train, X_test, y_train, y_test, feature_cols = prepare_features(df)

    rf_results = train_random_forest(X_train, X_test, y_train, y_test, feature_cols, output_dir)
    nn_results = train_neural_network(X_train, X_test, y_train, y_test, output_dir)
    compare_models(rf_results, nn_results, output_dir)

    print("\n" + "=" * 55)
    print("  Analysis complete. Results saved to '{}/'".format(output_dir))
    print("=" * 55)


if __name__ == '__main__':
    main()
