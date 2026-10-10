# Technical Challenges and Engineering Solutions

This document logs the real-world engineering obstacles encountered during system implementation, how they were diagnosed, and how they were resolved.

---

## Challenge 1: macOS OpenMP Native Runtime Linkage for XGBoost
- **Symptom:** Importing `xgboost` inside the virtual environment failed with `dlopen(...libxgboost.dylib): Library not loaded: @rpath/libomp.dylib`.
- **Root Cause:** XGBoost relies on LLVM OpenMP (`libomp.dylib`) for parallel gradient boosting computation. On macOS ARM64 without system-wide Homebrew binaries in `/opt/homebrew/opt/libomp`, the dynamic linker could not locate `@rpath/libomp.dylib`.
- **Engineering Solution:** 
  1. Extracted the official macOS ARM64 `libomp.dylib` from the LLVM release.
  2. Placed the shared library directly in the virtual environment's native library directory: `.venv/lib/python3.9/site-packages/xgboost/lib/`.
  3. Invoked `install_name_tool -add_rpath @loader_path` using CommandLineTools developer directory to instruct macOS dyld to search the local directory.
  4. Result: XGBoost 2.1.4 imported and trained natively on Apple Silicon with full multicore acceleration.

---

## Challenge 2: Class Imbalance vs Naive Accuracy Illusion
- **Symptom:** In a retail banking churn dataset with 20.37% churn and 79.63% retention, standard unweighted classifiers can achieve ~80% accuracy by trivially predicting `0` (retained) for all customers, missing 100% of at-risk relationships.
- **Root Cause:** Standard loss functions minimize total classification error across the majority class, penalizing false alarms more than missed minority churners.
- **Engineering Solution:**
  1. Configured minority class weighting: `scale_pos_weight = 3.91` in XGBoost and `class_weight='balanced_subsample'` in Random Forest.
  2. Conducted probability threshold tuning strictly on a dedicated validation split (searching thresholds from 0.10 to 0.90 to maximize minority F1-score).
  3. Built an interactive threshold simulator in Streamlit allowing business users to tune the cutoff live based on the cost of customer outreach vs the value of saved account deposits.

---

## Challenge 3: Eliminating Data Leakage in Feature Engineering
- **Symptom:** In many portfolio projects, scalers (StandardScaler) and encoders (OneHotEncoder) are fitted across the entire dataset before splitting, causing test-set variance and mean to leak into training representations.
- **Root Cause:** Ad-hoc pandas feature transformations executed outside a formalized Scikit-learn estimator interface.
- **Engineering Solution:**
  1. Created a custom `CustomerFeatureEngineer` inheriting from Scikit-learn's `BaseEstimator` and `TransformerMixin`.
  2. Nested feature engineering within a unified `Pipeline` and `ColumnTransformer`.
  3. Ensured `pipeline.fit(X_train)` is executed strictly on the training partition.
  4. Serialized the entire preprocessor pipeline as `preprocessor.joblib`, guaranteeing identical feature calculations during live single-customer and batch inference.

---

## Challenge 4: Operating System Limitations with Power BI Desktop
- **Symptom:** Master build requirements specified Power BI deliverables, but the runtime environment is macOS ARM64 where Power BI Desktop cannot execute natively.
- **Engineering Solution:**
  1. Refused to fabricate a fake `.pbix` binary or claim execution on an unsupported platform.
  2. Exported a fully scored, model-enriched dataset (`data/exports/powerbi_churn_dataset.csv`) with predictions, risk tiers, and timestamps.
  3. Authored production-ready DAX measure scripts (`powerbi/DAX_Measures.md`).
  4. Designed an enterprise star-schema specification and visual dashboard guide (`powerbi/Data_Model_Specification.md` and `powerbi/Dashboard_Design_Guide.md`), allowing Windows Power BI users to import and reproduce the 4-page dashboard in under 5 minutes.

---

## Challenge 5: Distinguishing Statistical Attribution from Causal Proof
- **Symptom:** Stakeholders frequently misinterpret high feature importance (e.g., German accounts having high churn) as a direct cause, assuming that changing a feature or reaching out to a customer guarantees retention.
- **Engineering Solution:**
  1. Implemented SHAP TreeExplainer for mathematically rigorous, directional attribution of local predictions.
  2. Embedded prominent governance disclosures across the interface stating that SHAP values reflect statistical associations within observational data, not proved causality.
  3. Designed a business retention simulator with adjustable intervention success rates (default 25%) and recommended randomized A/B holdout testing prior to large-scale marketing spend.
