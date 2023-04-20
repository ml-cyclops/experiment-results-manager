import posixpath
from dataclasses import dataclass
from enum import Enum

import fsspec


class ArtifactType(str, Enum):
    PNG = "png"
    JPG = "jpg"
    PLOTLY_JSON = "plotly_json"
    HTML = "html"
    BINARY = "binary"


@dataclass
class ArtifactBase:
    id: str
    filename: str
    artifact_type: ArtifactType


@dataclass
class Artifact(ArtifactBase):
    bytes: bytes


def artifact_metadata_to_artifact(
    artifact_metadata: ArtifactBase, experiment_run_path: str
) -> Artifact:
    artifact_path = posixpath.join(experiment_run_path, artifact_metadata.filename)
    with fsspec.open(artifact_path, "r") as f:
        data = f.read()
    return Artifact(
        artifact_metadata.id,
        artifact_metadata.filename,
        artifact_metadata.artifact_type,
        data,
    )
