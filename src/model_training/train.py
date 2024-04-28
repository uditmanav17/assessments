# ruff: noqa : F401
# %%
import os
import pickle as pkl
from pathlib import Path

# %%
import gdown as g
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import MinMaxScaler

RANDOM_STATE = 42


# %%
def download_train_data(out_file_path, id_="1YH12g1xl4pMTi27PPSncxTpXbJWH8z_a"):
    if not Path(out_file_path).exists():
        g.download(id=id_, output=out_file_path)
    return pd.read_csv(out_file_path)


# %%
def build_classifier(model_hyper_params: dict):
    return LogisticRegression(**model_hyper_params)


# %%
def preprocess_data(
    data: pd.DataFrame,
    prep: Pipeline,
):
    return prep.fit_transform(data)


# %%
def train_model(train_X: pd.DataFrame, train_y: pd.DataFrame, model):
    model.fit(train_X, train_y)
    return model


# %%
def classification_metrics(model, X, y):
    preds = model.predict(X)
    accuracy = accuracy_score(y, preds)
    precision = precision_score(y, preds)
    recall = recall_score(y, preds)
    f1 = f1_score(y, preds)
    print(f"Accuracy - {accuracy}")
    print(f"Precision - {precision}")
    print(f"Recall - {recall}")
    print(f"F1-score - {f1}")
    probs = model.predict_proba(X)[:, 1]
    print(f"ROC AUC Score (Primary Objective) - {roc_auc_score(y, probs)}")


# %%
if __name__ == "__main__":
    train_data = download_train_data("./train.csv")
    train_df, valid_df = train_test_split(
        train_data,
        test_size=0.3,
        random_state=RANDOM_STATE,
        stratify=train_data["target"],
    )
    train_X = train_df.copy()
    train_ids = train_X.pop("ID_code")
    train_y = train_X.pop("target")
    # %%
    preprocessing_pipeline = Pipeline(
        [
            ("impute", SimpleImputer()),
            ("scaling", MinMaxScaler()),
        ]
    )
    processed_data_x = preprocess_data(train_X, preprocessing_pipeline)
    train_X_processed = pd.DataFrame(processed_data_x, columns=train_X.columns)
    print("Processed train data - ")
    print(train_X_processed.head())
    # %%
    log_reg_hyper_params = {
        "C": 0.01,
        "n_jobs": -1,
        "max_iter": 100,
        "class_weight": "balanced",
    }
    train_pipeline = Pipeline(
        [
            ("preprocessing", preprocessing_pipeline),
            ("model", build_classifier(log_reg_hyper_params)),
        ]
    )
    # %%
    model = train_model(train_X, train_y, train_pipeline)
    # %%
    print("Metrics on Train Data -")
    classification_metrics(model, train_X, train_y)
    # %%
    print("Metrics on Valid Data -")
    valid_X = valid_df.copy()
    valid_ids = valid_X.pop("ID_code")
    valid_y = valid_X.pop("target")
    classification_metrics(model, valid_X, valid_y)
    # %%
    model_out_path = r"src/backend/dummy_clf.pkl"
    with open(model_out_path, "wb") as f:
        pkl.dump(model, f)
    print("Good, All Done!")

# %%
