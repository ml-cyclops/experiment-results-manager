from dataclasses import dataclass
from enum import Enum


class ArtifactType(Enum):
    IMAGE_PNG = "png"
    PLOTLY_JSON = "plotly_json"
    HTML = "html"
    BINARY = "binary"


@dataclass
class Artifact:
    id: str
    filename: str
    bytes: bytes
    artifact_type: ArtifactType
