import json
import posixpath
from datetime import datetime
from typing import Dict, Union

import fsspec
from pydantic import BaseModel

from experiment_results_manager.artifact import Artifact, ArtifactBase
from experiment_results_manager.experiment_run import ExperimentRun


class ExperimentRunMetadata(BaseModel):
    timestamp_utc: datetime
    experiment_id: str
    variant_id: str
    run_id: str
    params: Dict[str, Union[str, int, float]]
    metrics: Dict[str, Union[str, int, float]]
    dicts: Dict[str, Dict[str, Union[str, int, float]]]
    artifacts: Dict[str, ArtifactBase]


def write_to_file(str_or_bytes: Union[str, bytes], uri: str) -> None:
    with fsspec.open(uri, "wb") as f:
        if isinstance(str_or_bytes, str):
            data = str_or_bytes.encode("utf-8")
        else:
            data = str_or_bytes
        f.write(data)


def read_file(uri: str) -> bytes:
    with fsspec.open(uri, "rb") as f:
        return f.read()  # type: ignore


def save_run_to_registry(er: ExperimentRun, experiment_registry_path: str) -> str:
    """
    Saves an experiment run and all its artifacts to the experiment registry.
    The path will be "{experiment_registry_path}/{experiment_id}/{variant_id}/{run_id}"
    """
    run_path = posixpath.join(
        experiment_registry_path, er.experiment_id, er.variant_id, er.run_id
    )
    save_run_to_path(er, run_path)
    return run_path


def save_run_to_path(er: ExperimentRun, path: str) -> None:
    er_metadata = ExperimentRunMetadata(
        timestamp_utc=er.timestamp_utc,
        experiment_id=er.experiment_id,
        variant_id=er.variant_id,
        run_id=er.run_id,
        params=er.params,
        metrics=er.metrics,
        dicts=er.dicts,
        artifacts=dict(
            [
                (
                    a,
                    ArtifactBase(
                        er.artifacts[a].id,
                        er.artifacts[a].filename,
                        er.artifacts[a].artifact_type,
                    ),
                )
                for a in er.artifacts.keys()
            ]
        ),
    )

    er_metadata_json = er_metadata.json()
    write_to_file(er_metadata_json, posixpath.join(path, "erm_metadata.json"))

    for a in er.artifacts.keys():
        write_to_file(
            er.artifacts[a].bytes,
            posixpath.join(path, "artifacts", er.artifacts[a].filename),
        )
    print(f"experiment run saved to {path}")


def load_run_from_registry(
    experiment_registry_path: str, experiment_id: str, variant_id: str, run_id: str
) -> ExperimentRun:
    run_path = posixpath.join(
        experiment_registry_path, experiment_id, variant_id, run_id
    )

    return load_run_from_path(run_path)


def load_run_from_path(run_path: str) -> ExperimentRun:
    er_metadata_dict = json.loads(
        read_file(posixpath.join(run_path, "erm_metadata.json")).decode("utf-8")
    )
    er_metadata = ExperimentRunMetadata(**er_metadata_dict)

    artifacts = {}
    for a in er_metadata.artifacts.keys():
        artifact_base = er_metadata.artifacts[a]
        data = read_file(posixpath.join(run_path, "artifacts", artifact_base.filename))
        artifacts[a] = Artifact(
            artifact_base.id, artifact_base.filename, artifact_base.artifact_type, data
        )

    er = ExperimentRun(
        er_metadata.experiment_id,
        er_metadata.variant_id,
        er_metadata.run_id,
        er_metadata.timestamp_utc,
    )

    er.artifacts = artifacts
    er.dicts = er_metadata.dicts
    er.params = er_metadata.params
    er.metrics = er_metadata.metrics
    return er
