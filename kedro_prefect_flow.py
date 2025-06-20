from kedro.framework.session import KedroSession
from prefect import flow, task

@task
def run_kedro_pipeline():
    with KedroSession.create(package_name="mlopsproject") as session:
        session.run()           # default pipeline registry
@flow(name="full_kedro_run")
def full_kedro_run():
    run_kedro_pipeline()
