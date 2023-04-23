import json
import posixpath
from datetime import datetime
from typing import Dict, Optional, Union

import fsspec
from pydantic import BaseModel

from experiment_results_manager.artifact import Artifact, ArtifactBase
from experiment_results_manager.experiment_run import ExperimentRun
from experiment_results_manager.fsspec_util import (
    get_fs_from_uri,
    read_file,
    write_to_file,
)
from experiment_results_manager.registry import get_latest_run_for_variant


class ExperimentRunMetadata(BaseModel):
    timestamp_utc: datetime
    experiment_id: str
    variant_id: str
    run_id: str
    params: Dict[str, Union[str, int, float]]
    metrics: Dict[str, Union[str, int, float]]
    dicts: Dict[str, Dict[str, Union[str, int, float]]]
    artifacts: Dict[str, ArtifactBase]


def save_run_to_registry(
    er: ExperimentRun,
    experiment_registry_path: str,
    fs: Optional[fsspec.AbstractFileSystem] = None,
    overwrite: bool = False,
) -> str:
    """
    Saves an ExperimentRun object to a registry on a file system.

    Args:
        er (ExperimentRun): The ExperimentRun object to save.
        experiment_registry_path (str): The path to the experiment registry directory.
        fs (Optional[fsspec.AbstractFileSystem]): The file system to use.
            If None, get_fs_from_uri(experiment_registry_path) is used.
        overwrite (bool): Whether to overwrite an existing run with the same ID.
            If False and a run with the same ID exists, a ValueError is raised.

    Returns:
        str: The path to the saved run.
    """
    if fs is None:
        fs = get_fs_from_uri(experiment_registry_path)

    # Create the experiment registry file
    registry_file_path = posixpath.join(experiment_registry_path, ".erm_registry.json")
    if not fs.exists(registry_file_path):
        file_contents = {
            "created_timestamp_utc": datetime.utcnow().isoformat(),
        }
        write_to_file(json.dumps(file_contents), registry_file_path)

    # Create the experiment file if it doesn't exist
    experiment_file_path = posixpath.join(
        experiment_registry_path, er.experiment_id, ".erm_experiment.json"
    )
    if not fs.exists(experiment_file_path):
        file_contents = {
            "experiment_id": er.experiment_id,
            "created_timestamp_utc": datetime.utcnow().isoformat(),
        }
        write_to_file(json.dumps(file_contents), experiment_file_path)

    # Create the variant file
    variant_file_path = posixpath.join(
        experiment_registry_path, er.experiment_id, er.variant_id, ".erm_variant.json"
    )
    if not fs.exists(variant_file_path):
        file_contents = {
            "variant_id": er.variant_id,
            "created_timestamp_utc": datetime.utcnow().isoformat(),
        }
        write_to_file(json.dumps(file_contents), variant_file_path)

    run_path = posixpath.join(
        experiment_registry_path, er.experiment_id, er.variant_id, er.run_id
    )
    save_run_to_path(er, run_path, fs=fs, overwrite=overwrite)
    return run_path


def save_run_to_path(
    er: ExperimentRun,
    path: str,
    fs: Optional[fsspec.AbstractFileSystem] = None,
    overwrite: bool = False,
) -> None:
    """
    Save an experiment run to a file system path.

    Args:
        er (ExperimentRun): The experiment run to save.
        path (str): The path to save the experiment run to.
        fs (Optional[fsspec.AbstractFileSystem], optional): The file system to use. Defaults to None.
        overwrite (bool, optional): Whether to overwrite an existing experiment run at the same path. Defaults to False.

    Raises:
        FileExistsError: If a run already exists at the given path and `overwrite` is set to False.

    Returns:
        None
    """
    if fs is None:
        fs = get_fs_from_uri(path)

    run_metadata_file_path = posixpath.join(path, "erm_metadata.json")
    if fs.exists(run_metadata_file_path) and not overwrite:
        raise FileExistsError(
            f"A run already exists at {path}, set overwrite=True to overwrite"
        )

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
    write_to_file(er_metadata_json, run_metadata_file_path)

    artifacts_dir = posixpath.join(path, "artifacts")
    for a in er.artifacts.keys():
        write_to_file(
            er.artifacts[a].bytes,
            posixpath.join(artifacts_dir, er.artifacts[a].filename),
        )
    print(f"experiment run saved to {path}")


def load_run_from_registry(
    experiment_registry_path: str,
    experiment_id: str,
    variant_id: str = "main",
    run_id: Optional[str] = None,
) -> ExperimentRun:
    """
    Load an experiment run from its registry path.

    Args:
        experiment_registry_path (str): The root path of the experiment registry.
        experiment_id (str): The ID of the experiment.
        variant_id (str, optional): The ID of the variant. Defaults to "main".
        run_id (str, optional): The ID of the run. If not provided, the latest run
            for the variant is used.

    Returns:
        ExperimentRun: The loaded experiment run.

    Raises:
        ValueError: If the experiment or variant ID is invalid.
        FileNotFoundError: If the run path does not exist.

    """
    if run_id is None:
        run_id = get_latest_run_for_variant(
            experiment_registry_path, experiment_id, variant_id
        )

    run_path = posixpath.join(
        experiment_registry_path, experiment_id, variant_id, run_id
    )

    return load_run_from_path(run_path)


def load_run_from_path(run_path: str) -> ExperimentRun:
    """Load an ExperimentRun object from a given path.

    Args:
        run_path (str): The path to the ExperimentRun directory.

    Returns:
        ExperimentRun: An ExperimentRun object populated with data from the given path.
    """
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
