import streamlit as st

st.set_page_config(page_title="Kedro Streamlit App", layout="wide")

st.markdown("# Kedro App Manager")

# App Documentation with more formal, polished text
st.markdown("### App Documentation")
st.markdown("""
This app helps you explore datasets, track experiments, visualize pipelines, and run your Kedro workflows all in one place. Use the sidebar to navigate through the different features and get started quickly.
""")

# Group info in bullet points
st.markdown(
    """
    **Our group:**
    - Afonso Gamito, nº 20240752
    - Gonçalo Pacheco, nº 20240695
    - Hugo Fonseca, nº 20240520
    - Nuno Nunes, nº 20240560
    """
)

# How to Use This Application with new page names and formal tone
st.markdown("### How to Use This Application")
st.markdown(
    """
    This application consists of the following pages, each dedicated to specific functionalities:

    - **Home Page:** Provides an introduction and documentation of the application.
    - **Data Catalog:** Allows users to browse and analyze datasets incorporated within the Kedro project.
    - **MLflow UI:** Integrates MLflow capabilities for experiment tracking, model management, and deployment.
    - **Pipelines Viz:** Offers an interactive graphical visualization of Kedro pipelines to understand the data flow and dependencies.
    - **Run Pipelines:** Enables execution and monitoring of Kedro pipelines directly from the interface.

    Please navigate through the menu to access these features.
    """
)
