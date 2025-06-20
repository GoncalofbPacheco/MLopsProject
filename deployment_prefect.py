from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer
from kedro_prefect_flow import full_kedro_run

Deployment(
    name="kedro-ci-cd",
    flow=full_kedro_run,
    infrastructure=DockerContainer(image="mlopsproject:latest"),
    work_pool_name="default-agent-pool",
).apply()
