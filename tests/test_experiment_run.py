import os
import tempfile

import matplotlib.pyplot as plt
import plotly.graph_objs as go
import pytest

from experiment_results_manager.artifact import ArtifactType
from experiment_results_manager.experiment_run import ExperimentRun


@pytest.fixture(scope="function")
def experiment_run():
    return ExperimentRun(experiment_id="test_experiment")


def test_log_param(experiment_run: ExperimentRun):
    experiment_run.log_param("param_key", "param_value")
    assert "param_key" in experiment_run.params
    assert experiment_run.params["param_key"] == "param_value"


def test_log_metric(experiment_run: ExperimentRun):
    experiment_run.log_metric("metric_key", 1.23)
    assert "metric_key" in experiment_run.metrics
    assert experiment_run.metrics["metric_key"] == 1.23


def test_log_dict(experiment_run: ExperimentRun):
    data = {"key1": 1, "key2": "value2"}
    experiment_run.log_dict("dict_name", data)
    assert "dict_name" in experiment_run.dicts
    assert experiment_run.dicts["dict_name"] == data


def test_log_artifact_bytes(experiment_run: ExperimentRun):
    data = b"test data"
    artifact_id = "test_artifact"
    file_name = "test_artifact.bin"
    experiment_run.log_artifact(data, artifact_id, file_name)
    assert "test_artifact" in experiment_run.artifacts
    assert experiment_run.artifacts["test_artifact"].id == "test_artifact"
    assert experiment_run.artifacts["test_artifact"].filename == file_name
    assert (
        experiment_run.artifacts["test_artifact"].artifact_type == ArtifactType.BINARY
    )
    assert experiment_run.artifacts["test_artifact"].bytes == data


def test_log_artifact_file(experiment_run: ExperimentRun):
    data = b"test data"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        filename = f.name
    artifact_id = "test_artifact"
    experiment_run.log_artifact(filename, artifact_id)
    assert "test_artifact" in experiment_run.artifacts
    assert experiment_run.artifacts["test_artifact"].id == "test_artifact"
    assert experiment_run.artifacts["test_artifact"].filename == os.path.basename(
        filename
    )
    assert (
        experiment_run.artifacts["test_artifact"].artifact_type == ArtifactType.BINARY
    )
    assert experiment_run.artifacts["test_artifact"].bytes == data
    os.unlink(filename)


def test_log_figure(experiment_run: ExperimentRun):
    fig = plt.figure()
    artifact_id = "test_artifact"
    experiment_run.log_figure(fig, artifact_id)
    assert "test_artifact" in experiment_run.artifacts
    assert experiment_run.artifacts["test_artifact"].id == "test_artifact"
    assert experiment_run.artifacts["test_artifact"].filename == f"{artifact_id}.png"
    assert experiment_run.artifacts["test_artifact"].artifact_type == ArtifactType.PNG
    assert experiment_run.artifacts["test_artifact"].bytes is not None
    plt.close(fig)

    fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
    artifact_id = "test_artifact2"
    experiment_run.log_figure(fig, artifact_id)
    assert "test_artifact2" in experiment_run.artifacts
    assert experiment_run.artifacts["test_artifact2"].id == "test_artifact2"
    assert (
        experiment_run.artifacts["test_artifact2"].filename
        == f"{artifact_id}.plotly.json"
    )
    assert (
        experiment_run.artifacts["test_artifact2"].artifact_type
        == ArtifactType.PLOTLY_JSON
    )
    assert experiment_run.artifacts["test_artifact2"].bytes is not None
