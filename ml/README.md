# ML Analysis and Comparative Evaluation

This document summarizes the machine-learning work in `/ml`, including exploratory data analysis, baseline model training, and comparative evaluation across classical and deep-learning approaches for influenza sequence classification.

## Scope

- **Data analysis notebook:** `/ml/notebooks/01_data_analysis.ipynb`
- **Baseline models notebook:** `/ml/notebooks/02a_baseline_models.ipynb`
- **HyenaDNA notebook:** `/ml/notebooks/02b_HyenaDNA_model.ipynb`
- **Comparative analysis notebook:** `/ml/notebooks/03_comparative_analysis.ipynb`

## Dataset Summary

Source file: `/ml/data/cleaned_data.csv`

- **Total samples:** 10,467
- **Target classes:** 17 influenza labels
- **Train/test split:** stratified 80/20 (`random_state=42`)
- **Classical-model features:** character **3-mer** frequencies (`CountVectorizer(analyzer="char", ngram_range=(3,3))`)

### Sequence-level descriptive statistics

- **Length (nt):** min 246, Q1 1,398, median 1,683, mean 1,651.37, Q3 2,208, max 2,867
- **GC content (%):** min 34.63, Q1 42.13, median 43.56, mean 43.79, Q3 44.97, max 50.59

### Class distribution (samples)

| Label | Count |
|---|---:|
| H1N1 | 2,470 |
| H3N2 | 1,971 |
| H5N1 | 1,135 |
| H9N2 | 1,101 |
| H5N2 | 779 |
| H7N3 | 602 |
| H7N9 | 421 |
| H1N2 | 398 |
| influenza B | 280 |
| H3N8 | 280 |
| H5N8 | 200 |
| H5N6 | 180 |
| H7N7 | 162 |
| influenza D | 149 |
| H4N6 | 128 |
| H7N2 | 111 |
| H6N2 | 100 |

## Data Analysis Findings

The exploratory stage focuses on sequence composition and class separability in reduced feature space.

### PCA projection (3-mer frequencies)

![PCA of 3-mer frequencies](./ml/figures/pca_results_3mer_freq.jpg)

### t-SNE projection (3-mer frequencies)

![t-SNE of 3-mer frequencies](./ml/figures/tsne_results_3mer_freq.jpg)

### UMAP projection (3-mer frequencies)

![UMAP of 3-mer frequencies](./ml/figures/umap_results_3mer_freq.jpg)

**Interpretation:** the projections indicate partial clustering by subtype, with meaningful overlap among related influenza classes, motivating robust multiclass modeling and per-class evaluation.

## Comparative Analysis

Models compared in `/ml/notebooks/03_comparative_analysis.ipynb`:

- Logistic Regression
- Random Forest
- XGBoost
- HyenaDNA (fine-tuned sequence model)

### Overall performance and efficiency

| Model | Accuracy | Macro F1 | Weighted F1 | Macro AUC | Pred Time (ms/sample) | Model Size (MB) |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.2359 | 0.0225 | 0.0901 | 0.7015 | 0.0054 | 0.0802 |
| Random Forest | 0.8801 | 0.8056 | 0.8740 | 0.9778 | 0.0319 | 56.6545 |
| XGBoost | 0.8749 | 0.8072 | 0.8705 | 0.9868 | 0.0384 | 2.9057 |
| HDNA | 0.8548 | 0.7634 | 0.8529 | 0.9806 | 11.5954 | 15.5724 |

### ROC curves by class and model

![ROC curves](./ml/figures/results_roc_curves.png)

### Precision–Recall curves by class and model

![PR curves](./ml/figures/results_pr_curves.png)

### Per-class F1 heatmap

![Per-class F1 heatmap](./ml/figures/per_class_f1_heatmap.png)

### Efficiency vs performance trade-off

![Efficiency vs performance](./ml/figures/efficiency_vs_performance.png)

## Key Conclusions

1. **Random Forest and XGBoost** provide the strongest aggregate performance among tested models, with high macro/weighted F1 and high macro AUC.
2. **XGBoost** achieves near-top predictive quality with a much smaller footprint than Random Forest, making it a practical deployment candidate.
3. **HyenaDNA** remains competitive in discrimination (macro AUC), but has materially higher per-sample inference cost in this setup.
4. **Logistic Regression** serves as a lightweight baseline but underperforms significantly on multiclass discrimination.

## Reproducibility Notes

- Re-run notebooks in this order:
  1. `01_data_analysis.ipynb`
  2. `02a_baseline_models.ipynb`
  3. `02b_HyenaDNA_model.ipynb`
  4. `03_comparative_analysis.ipynb`
- Figures in `/ml/figures` are consumed directly in this README.
