import joblib, pathlib, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
from . import data
from .config import FEATURES, LABELS
PATH = pathlib.Path(__file__).resolve().parents[1] / "models" / "placement_model.joblib"

def train(df, save=True):
    X, y = df[FEATURES], df["label"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, stratify=y, random_state=42)
    clf = RandomForestClassifier(300, max_depth=8, min_samples_leaf=5, class_weight="balanced",
                                 random_state=42, n_jobs=-1)
    cv = cross_val_score(clf, Xtr, ytr, cv=5, scoring="f1_macro")
    clf.fit(Xtr, ytr)
    rep = classification_report(yte, clf.predict(Xte), output_dict=True, zero_division=0)
    bundle = {"clf": clf, "features": FEATURES, "n_train": len(df),
              "cv_f1_macro": (float(cv.mean()), float(cv.std())), "test_f1_macro": rep["macro avg"]["f1-score"],
              "importance": dict(zip(FEATURES, map(float, clf.feature_importances_)))}
    if save: PATH.parent.mkdir(exist_ok=True); joblib.dump(bundle, PATH)
    return bundle

def load_or_train():
    if PATH.exists():
        try: return joblib.load(PATH)
        except Exception: pass  # e.g. sklearn version mismatch -> retrain
    return train(data.generate())

def predict(bundle, df):
    p = bundle["clf"].predict_proba(df[FEATURES]); cls = list(bundle["clf"].classes_)
    probs = pd.DataFrame(p, columns=cls, index=df.index).reindex(columns=LABELS, fill_value=0.0)
    return probs.idxmax(axis=1), probs

if __name__ == "__main__":
    b = train(data.generate())
    print(f"CV macro-F1 {b['cv_f1_macro'][0]:.3f}+-{b['cv_f1_macro'][1]:.3f} | test {b['test_f1_macro']:.3f} (synthetic data)")
