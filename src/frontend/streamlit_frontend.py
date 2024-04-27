# ruff: noqa : F401
import io
import tempfile
from io import StringIO

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Transaction Prediction",
    page_icon="💸",
    initial_sidebar_state="expanded",
)


def evaluate_response(response):
    if response.status_code == 422:
        st.warning(response.json()["detail"])
        return None
    if response.status_code not in [200, 422]:
        st.warning("Backend service may be down!!")
        return None
    data = response.content
    csv_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    print(csv_file.name)
    if data:
        return pd.read_csv(io.BytesIO(data)).to_csv(index=False).encode("utf-8")
    else:
        st.warning("Something went Wrong!!")


@st.cache_data
def download_sample_file():
    response = requests.get("http://backend:8000/download_sample/")
    return evaluate_response(response)


def predict_endpoint(csv_file_path: str):
    files = {"file": open(csv_file_path, "rb")}
    response = requests.post("http://backend:8000/upload_file_predict/", files=files)
    return evaluate_response(response)


def main():
    st.title("💸Santander Customer Transaction Prediction")
    st.sidebar.title("Sample Data files")

    # sidebar layout
    st.sidebar.markdown("---")
    st.sidebar.markdown("Download sample file")
    st.sidebar.markdown(
        "Sample file used for adding data samples, which can then be uploaded to prediction service."
    )
    csv = download_sample_file()
    st.sidebar.download_button(
        label="Download sample CSV",
        data=csv,
        file_name="large_df.csv",
        mime="text/csv",
    )

    st.markdown(
        """
        - This is frontend of an application to serve prediction for famous Santender Dataset.
        - To know more about Santander, refer [this](https://www.kaggle.com/competitions/santander-customer-transaction-prediction/overview).
        - Its simple and straight forward, download sample file from left sidebar,
        update its contents with data on which you want to perform predictions. Upload the file below.
        - View results in application or download prediction csv.
        """
    )
    csv_file_buffer = st.file_uploader("Upload CSV for prediction", type=["csv"])
    csv_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    if csv_file_buffer:
        file_bytes = io.BytesIO(csv_file_buffer.read())
        with open(csv_file.name, "wb") as f:
            f.write(file_bytes.read())
    if csv_file_buffer:
        if df := predict_endpoint(csv_file.name):
            st.info("Prediction Completed!! Click below to download file.")
            col1, col2 = st.columns(2)
            with col2:
                st.download_button(
                    label="Download predictions CSV",
                    data=df,
                    file_name="predictions.csv",
                    mime="text/csv",
                )
            with col1:
                if st.button("View Prediction Dataframe"):
                    st.dataframe(
                        pd.read_csv(StringIO(df.decode("utf-8")), sep=","),
                        hide_index=True,
                    )


if __name__ == "__main__":
    main()
