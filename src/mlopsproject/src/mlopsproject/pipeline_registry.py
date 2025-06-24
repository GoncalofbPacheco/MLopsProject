"""Project pipelines."""

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from mlopsproject.pipelines import ingestion as ingestion_pipeline
from mlopsproject.pipelines import data_unit_tests as data_unit_tests_pipeline
from mlopsproject.pipelines import split_data as split_data_pipeline  

def register_pipelines() -> dict[str, Pipeline]:
    pipelines = find_pipelines()
    pipelines["ingestion"] = ingestion_pipeline.create_pipeline()
    pipelines["data_unit_tests"] = data_unit_tests_pipeline.create_pipeline()
    pipelines["split_data"] = split_data_pipeline.create_pipeline()  
    pipelines["__default__"] = sum(pipelines.values())
    return pipelines


