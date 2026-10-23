import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

df = pd.read_csv("flood_training_data.csv")

print(f"Loaded {len(df)} real weather records")
print("Label distribution:")
print(df["Flood"].value_counts())

X = df.drop("Flood", axis=1)
y = df["Flood"]
n_safe  = (y == 0).sum()
n_flood = (y == 1).sum()
scale_pos_weight = n_safe / n_flood   
print(f"\nClass imbalance ratio (safe/flood): {scale_pos_weight:.2f}x")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print("\nTraining Ensemble Models on REAL historical flood data...")

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,  
    random_state=42,
    eval_metric="logloss",
    verbosity=0,
)
xgb_model.fit(X_train_scaled, y_train)
print("XGBoost trained")

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",           
    random_state=42,
)
rf_model.fit(X_train_scaled, y_train)
print("Random Forest trained")

logistic_poly = Pipeline([
    ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
    ("logreg", LogisticRegression(
        C=0.5,
        max_iter=2000,
        class_weight="balanced",       
        random_state=42,
    )),
])
logistic_poly.fit(X_train_scaled, y_train)
print("Logistic Regression with Polynomial Features trained")

model_package = {
    "xgb_model":    xgb_model,
    "rf_model":     rf_model,
    "logistic_poly": logistic_poly,
    "scaler":       scaler,
}
joblib.dump(model_package, "model/flood_model.pkl")
print("Ensemble models saved to model/flood_model.pkl")

print("\nModel Performance on held-out test set:")
models = {
    "XGBoost":            xgb_model,
    "Random Forest":      rf_model,
    "Logistic Poly":      logistic_poly,
}
for name, model in models.items():
    y_pred = model.predict(X_test_scaled)
    acc    = accuracy_score(y_test, y_pred)
    print(f"  {name}: {acc:.4f} accuracy")

xgb_prob      = xgb_model.predict_proba(X_test_scaled)[:, 1]
rf_prob       = rf_model.predict_proba(X_test_scaled)[:, 1]
logistic_prob = logistic_poly.predict_proba(X_test_scaled)[:, 1]
ensemble_prob = xgb_prob * 0.4 + rf_prob * 0.4 + logistic_prob * 0.2
ensemble_pred = (ensemble_prob > 0.5).astype(int)
print(f"\nEnsemble Accuracy: {accuracy_score(y_test, ensemble_pred):.4f}")
print("\nDetailed classification report:")
print(classification_report(y_test, ensemble_pred, target_names=["Safe", "Flood"]))