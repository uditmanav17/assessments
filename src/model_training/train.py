# ruff: noqa : F401
# %%
import os
import pickle as pkl
from pathlib import Path

# %%
import gdown as g
import pandas as pd
from sklearn.base import TransformerMixin
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline

RANDOM_STATE = 42


# %%
class DummyTransformer(TransformerMixin):
    def __init__(self, **kwargs):
        self.params = kwargs

    def fit(self, X):
        return X

    def transform(self, X):
        return X

    def get_params(self):
        return self.params


# %%
def download_train_data(out_file_path, id_="1YH12g1xl4pMTi27PPSncxTpXbJWH8z_a"):
    if not Path(out_file_path).exists():
        g.download(id=id_, output=out_file_path)
    return pd.read_csv(out_file_path)


# %%
def build_classifier(model_hyper_params: dict, *args, **kwargs):
    return DummyClassifier(**model_hyper_params)


# %%
def split_data(df: pd.DataFrame):
    # Preprocessing data
    train_df, valid_df = train_test_split(
        df,
        test_size=0.3,
        random_state=RANDOM_STATE,
        stratify=df["target"],
    )
    return train_df, valid_df


# %%
def preprocess_data(
    data: pd.DataFrame,
    prep: Pipeline,
):
    return prep.transform(data)


# %%
def train_model(train_X: pd.DataFrame, train_y: pd.DataFrame, model):
    model.fit(train_X, train_y)
    return model


# %%
def classification_metrics(y, preds):
    accuracy = accuracy_score(y, preds)
    precision = precision_score(y, preds)
    recall = recall_score(y, preds)
    f1 = f1_score(y, preds)
    print(f"Accuracy - {accuracy}")
    print(f"Precision - {precision}")
    print(f"Recall - {recall}")
    print(f"F1-score - {f1}")


# %%
if __name__ == "__main__":
    train_data = download_train_data("./train.csv")
    train_df, valid_df = split_data(train_data)
    train_X = train_df.copy()
    train_y = train_X.pop("target")
    train_X_prep = Pipeline([("dummy", DummyTransformer())])
    train_y_prep = Pipeline([("dummy", DummyTransformer())])
    # %%
    train_X = preprocess_data(train_X, train_X_prep)
    train_y = preprocess_data(train_y, train_y_prep)
    model = build_classifier(model_hyper_params={"strategy": "uniform"})
    # %%
    model = train_model(train_X, train_y, model)
    train_preds = model.predict(train_X)
    print("Metrics on Train Data -")
    classification_metrics(train_y, train_preds)
    # %%
    print("Metrics on Valid Data -")
    valid_X = valid_df.copy()
    valid_y = valid_X.pop("target")
    valid_preds = model.predict(valid_X)
    classification_metrics(valid_y, valid_preds)
    # %%
    model_out_path = r"..\backend\dummy_clf.pkl"
    with open(model_out_path, "wb") as f:
        pkl.dump(model, f)
    print("Done!")


# %%
