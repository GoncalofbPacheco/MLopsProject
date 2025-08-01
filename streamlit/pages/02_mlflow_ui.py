# streamlit libray
import streamlit as st
import streamlit.components.v1 as components
from streamlit_ydata_profiling import st_profile_report
from pathlib import Path
from kedro.framework.project import configure_project
import time
import requests

package_name = Path(__file__).parent.name
configure_project(package_name)

KEDRO_VIZ_SERVER_URL = "http://127.0.0.1:4141/"
MLFLOW_SERVER_URL = "http://127.0.0.1:8080/"

if "kedro_viz_started" not in st.session_state:
    st.session_state["kedro_viz_started"] = False

if "mlflow" not in st.session_state:
    st.session_state["mlflow"] = False

st.title("MLflow UI")

# Small descriptive text below title
st.markdown(
    "This page displays the MLflow UI embedded for experiment tracking and model management."
)
st.markdown(
    "Please note: In MLflow, change the experiment name from **default** to **mlopsproject**."
)
unsafe_allow_html = (True,)


def launch_mlflow_server(reporter):
    if not st.session_state["mlflow"]:
        import os
        import subprocess
        import threading

        def _run_job(job):
            print(f"\nRunning job: {job}\n")
            proc = subprocess.Popen(job)
            proc.wait()
            return proc

        reporter.warning("Starting visualization server...")
        time.sleep(3)

        good_process = subprocess.run(
            [
                "mlflow",
                "server",
                "--host=127.0.0.1",
                "--port=8080",
                "--artifacts-destination=./ml_artifacts",
                "--default-artifact-root=./ml_artifacts",
            ],
            capture_output=True,
            text=True,
        )
        reporter.info("Waiting for server response...")
        time.sleep(3)

        retries = 5
        while True:
            reporter.info("Waiting for server response...")
            resp = None
            try:
                resp = requests.get(MLFLOW_SERVER_URL)
            except:
                pass
            if resp and resp.status_code == 200:
                st.session_state["mlflow"] = True
                reporter.empty()
                break
            else:
                time.sleep(1)
            retries -= 1
            if retries < 0:
                reporter.info(
                    'Right click on the empty iframe and select "Reload frame"'
                )
                break


def show_mlflow():
    st.subheader("MLflow UI")

    reporter = st.empty()

    st.write("Visualization available at http://localhost:8080/")

    launch_mlflow_server(reporter)

    if st.session_state["mlflow"]:
        st.caption("This interactive pipeline visualization.")
        components.iframe(MLFLOW_SERVER_URL, width=1500, height=800)


show_mlflow()
