# ruff: noqa : F401

import streamlit as st

st.set_page_config(
    page_title="Santander Customer Transaction Prediction",
    page_icon="💸",
    initial_sidebar_state="expanded",
)


def main():
    st.title("Object Detection API")
    st.sidebar.title("Settings")

    # sidebar layout
    st.sidebar.markdown("---")
    confidence = st.sidebar.slider(
        "Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
    )


if __name__ == "__main__":
    main()
