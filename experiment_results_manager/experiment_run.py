import os
from datetime import datetime
from typing import Any, Dict, Optional

import matplotlib.axes
import matplotlib.figure
import plotly

from experiment_results_manager.artifact import Artifact, ArtifactType
from experiment_results_manager.html_util import matplotlib_fig_to_bytes


class ExperimentRun:
    timestamp_utc: datetime
    experiment_id: str
    variant_id: str
    run_id: str
    params: Dict[str, str | int | float]
    metrics: Dict[str, str | int | float]
    dicts: Dict[str, Dict[str, str | int | float]]
    artifacts: Dict[str, Artifact]

    def __init__(
        self,
        experiment_id: str,
        variant_id: str = "main",
        run_id: Optional[str] = None,
        timestamp_utc: Optional[datetime] = None,
    ) -> None:
        if timestamp_utc is None:
            self.timestamp_utc = datetime.utcnow()
        else:
            self.timestamp_utc = timestamp_utc

        if run_id is None:
            self.run_id = self.timestamp_utc.strftime("%Y_%m_%d__%H_%M_%S")
        else:
            self.run_id = run_id

        self.variant_id = variant_id
        self.experiment_id = experiment_id
        self.params: Dict[str, str | int | float] = {}
        self.metrics: Dict[str, str | int | float] = {}
        self.dicts: Dict[str, Dict[str, Any]] = {}
        self.artifacts: Dict[str, Artifact] = {}

    def log_param(self, key: str, value: str | int | float) -> None:
        self.params[key] = value

    def log_metric(self, key: str, value: str | int | float) -> None:
        self.metrics[key] = value

    def log_artifact(
        self,
        src_path_or_bytes: str | bytes,
        artifact_id: str,
        filename: str | None = None,
        artifact_type: ArtifactType = ArtifactType.BINARY,
    ) -> None:
        if isinstance(src_path_or_bytes, bytes):
            # Create an artifact from the byte array
            if filename is None:
                raise ValueError(
                    "filename must be provided when src_path_or_bytes is a byte array"
                )
            artifact = Artifact(artifact_id, filename, artifact_type, src_path_or_bytes)
        else:
            # Read the file and create an artifact from its contents
            with open(src_path_or_bytes, "rb") as f:
                data = f.read()
            filename = os.path.basename(src_path_or_bytes)
            artifact = Artifact(artifact_id, filename, artifact_type, data)

        self.artifacts[artifact_id] = artifact

    def log_dict(self, dict_name: str, data: Dict[str, str | int | float]) -> None:
        if dict_name not in self.dicts:
            self.dicts[dict_name] = {}
        self.dicts[dict_name].update(data)

    def log_figure(
        self,
        fig: plotly.graph_objs.Figure | matplotlib.figure.Figure | matplotlib.axes.Axes,
        artifact_id: str,
    ) -> None:
        if isinstance(fig, plotly.graph_objs.Figure):
            # Plotly figure
            data = fig.to_json().encode("utf-8")
            filename = f"{artifact_id}.plotly.json"
            artifact_type = ArtifactType.PLOTLY_JSON
        elif isinstance(fig, matplotlib.figure.Figure):
            # Matplotlib figure
            data = matplotlib_fig_to_bytes(fig)
            filename = f"{artifact_id}.png"
            artifact_type = ArtifactType.IMAGE_PNG
        elif isinstance(fig, matplotlib.axes.Axes):
            # Matplotlib figure
            data = matplotlib_fig_to_bytes(fig.get_figure())
            filename = f"{artifact_id}.png"
            artifact_type = ArtifactType.IMAGE_PNG
        else:
            raise Exception(f"Unsupported figure type {type(fig)}")

        self.log_artifact(data, artifact_id, filename, artifact_type)

    def log_image(
        self,
        src_path_or_bytes: str | bytes,
        artifact_id: str,
        filename: Optional[str] = None,
    ) -> None:
        if filename is None:
            filename = artifact_id
        self.log_artifact(
            src_path_or_bytes,
            artifact_id=artifact_id,
            filename=filename,
            artifact_type=ArtifactType.IMAGE_PNG,
        )

    def log_metrics(self, data: Dict[str, str | int | float]) -> None:
        self.metrics.update(data)

    def log_params(self, data: Dict[str, str | int | float]) -> None:
        self.params.update(data)

    def log_text(self, text: str | bytes, artifact_id: str) -> None:
        if isinstance(text, str):
            data = text.encode("utf-8")
        elif isinstance(bytes, str):
            data = text

        self.log_artifact(data, artifact_id, artifact_id, ArtifactType.BINARY)
