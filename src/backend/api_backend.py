# ruff: noqa : F401

import os
from contextlib import asynccontextmanager
from io import StringIO
from pathlib import Path

import pandas as pd
import uvicorn
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

ml_models = {}


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


def respond_with_csv_file(df: pd.DataFrame, file_name: str):
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
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/",
    redoc_url=None,
)


@app.get("/ping", tags=["heartbeat"])
def greet_world():
    return "pong!"


def verify_df(df: pd.DataFrame):
    columns = ["ID_code"] + [f"var_{i}" for i in range(200)]
    columns = set(columns)
    return len(columns) == len(columns.intersection(set(df.columns)))


@app.get("/download_sample", tags=["sample_file"])
def download_sample_file():
    curr_file_path = Path(os.path.abspath(__file__)).parent
    df = pd.read_csv(rf"{str(curr_file_path)}/test2.csv")
    return respond_with_csv_file(df, "sample_file")


@app.post("/upload_file_predict", tags=["predict"])
async def upload_file_predict(file: UploadFile = File(...)):
    contents = file.file.read()
    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        if not verify_df(df):
            raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong file format or missing columns",
        ) from e
    # replace any missing row value with mean
    # MODEL PREDICTION HERE
    df["target"] = 0
    df2 = df[["ID_code", "target"]]
    return respond_with_csv_file(df2, "predictions")


if __name__ == "__main__":
    uvicorn.run("api_backend:app", reload=True, port=8080)
