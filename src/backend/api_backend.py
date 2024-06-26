# ruff: noqa : F401

import os
import pickle as pkl
from contextlib import asynccontextmanager
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import uvicorn
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

ml_models = {}

description = """
Backend service for Transaction predicion!

You will be able to:

* **Check if service is up (Ping!)** (_implemented_).
* **Download sample file** (_implemented_).
* **Upload file for prediction** (_implemented_).
"""


def predict_from_model(df: pd.DataFrame):
    # sourcery skip: inline-immediately-returned-variable
    model = ml_models.get("classification_model")
    preds = model.predict_proba(df)  # type: ignore
    return preds


def respond_with_csv_file(df: pd.DataFrame, file_name: str):
    # sourcery skip: inline-immediately-returned-variable
    stream = StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment;filename={file_name}.csv",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
    return response


@asynccontextmanager
async def lifespan(app: FastAPI | APIRouter):
    # Load the ML model
    curr_file_path = Path(os.path.abspath(__file__)).parent
    with open(f"{curr_file_path}/dummy_clf.pkl", "rb") as f:
        model = pkl.load(f)
    ml_models["classification_model"] = model
    ml_models["classification_predictions"] = predict_from_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/",
    redoc_url=None,
    title="Transaction Prediction",
    contact={
        "name": "Udit Manav",
        "url": "https://www.linkedin.com/in/uditmanav17/",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    description=description,
    version="0.0.1",
)


@app.get("/ping", tags=["heartbeat"])
def greet_world():
    return "pong!"


def verify_df(df: pd.DataFrame):
    columns = ["ID_code"] + [f"var_{i}" for i in range(200)]
    columns = set(columns)
    return len(columns) == len(columns.intersection(set(df.columns)))


@app.get("/download_sample", tags=["download_sample_file"])
def download_sample_file():
    curr_file_path = Path(os.path.abspath(__file__)).parent
    df = pd.read_csv(rf"{str(curr_file_path)}/test2.csv")
    return respond_with_csv_file(df, "sample_file")


@app.post("/upload_file_predict", tags=["batch_predict"])
async def upload_file_predict(file: UploadFile = File(...)):
    contents = file.file.read()
    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        if not verify_df(df):
            raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong file format or missing columns!",
        ) from e
    df_ids = df.pop("ID_code")
    predictions = np.round(ml_models["classification_predictions"](df)[:, 1], 3)

    df2 = pd.DataFrame({"ID_code": df_ids.values, "target_probab_1": predictions})
    return respond_with_csv_file(df2, "predictions")


if __name__ == "__main__":
    uvicorn.run("api_backend:app", reload=True, port=8080)
