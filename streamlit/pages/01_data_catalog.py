import streamlit as st
import pandas as pd
from kedro.io import DataCatalog
from streamlit_ydata_profiling import st_profile_report
from pathlib import Path
from kedro.framework.project import configure_project
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from ydata_profiling import ProfileReport

st.title("Data Catalog from Kedro")

# Small descriptive text below title
st.markdown(
    "<small>This page lets you explore and generate profiling reports for datasets configured in our Kedro Data Catalog.</small>",
    unsafe_allow_html=True,
)

# Configure Kedro project
package_name = Path(__file__).parent.name
configure_project(package_name)

conf_path = str(Path("..") / settings.CONF_SOURCE)
conf_loader = OmegaConfigLoader(conf_source=conf_path)
catalog = conf_loader["catalog"]

# Initialize session state for selected dataset and report button
if "selected_dataset" not in st.session_state:
    st.session_state.selected_dataset = ""
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

# Dropdown for selecting dataset
choice = st.selectbox("**Available Dataset:**", list(catalog.keys()))

# Reset report state if dataset changes
if choice != st.session_state.selected_dataset:
    st.session_state.selected_dataset = choice
    st.session_state.report_generated = False

st.write(
    "Important: Do not try to generate a report on a non-csv object of the Data Catalog"
)

# Load dataset
catalog[choice]["filepath"] = "../" + catalog[choice]["filepath"]
datacatalog = DataCatalog.from_config(catalog)
dataset = datacatalog.load(choice)

# Prepare profile report
profile = ProfileReport(dataset, title=f"{choice} Profiling Report", minimal=True)

# Button to generate report, toggles report display state
if st.button("**Generate report on data**"):
    st.session_state.report_generated = True

# Display report only if generated
if st.session_state.report_generated:
    st_profile_report(profile, navbar=True)
