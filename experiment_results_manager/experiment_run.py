import os
from datetime import datetime
from typing import Any, Dict, Optional, Union

import matplotlib.axes
import matplotlib.figure
import plotly

from experiment_results_manager.artifact import Artifact, ArtifactType
from experiment_results_manager.html_util import matplotlib_fig_to_bytes


class ExperimentRun:
    """
    Example usage:
    ```python
    import experiment_results_manager as erm
    from IPython.display import display, HTML
    import seaborn as sns

    # Creating arbitrary plot to log later
    tips = sns.load_dataset('tips')
    mpl_fig = sns.barplot(x='day', y='total_bill', data=tips)

    # Create an experiment run
    er = erm.ExperimentRun(
        experiment_id="my_experiment",
        variant_id="main"
    )

    # Log relevant data
    er.log_param("objective", "rmse")
    er.log_metric("rmse", "0.9")
    er.log_figure(mpl_fig, "ROC Curve")
    er.log_text("lorem ipsum...", "text")

    # Generate HTML
    html = erm.compare_runs(er)
    display(HTML(html))

    # Save the run to access later
    saved_path = erm.save_run_to_registry(er, "s3:///erm-registry")

    # Load a previous run
    er2 = erm.load_run_from_path(saved_path)

    # Compare the current run with a previous one
    html = erm.compare_runs(er, er2)
    display(HTML(html))
    ```
    """

    def __init__(
        self,
        experiment_id: str,
        variant_id: str = "main",
        run_id: Optional[str] = None,
        timestamp_utc: Optional[datetime] = None,
        params: Optional[Dict[str, Union[str, int, float]]] = None,
        metrics: Optional[Dict[str, Union[str, int, float]]] = None,
        dicts: Optional[Dict[str, Dict[str, Any]]] = None,
        artifacts: Optional[Dict[str, Artifact]] = None,
    ) -> None:
        """
        Initializes a new `ExperimentRun` object with the given experiment_id,
        `variant_id`, `run_id`, and `timestamp_utc`. If `timestamp_utc` is not provided,
        it defaults to the current UTC datetime. If `run_id` is not provided, it
        is generated from the `timestamp_utc` using the format "%Y_%m_%d__%H_%M_%S".
        """

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
        self.params: Dict[str, Union[str, int, float]] = (
            params if params is not None else {}
        )
        self.metrics: Dict[str, Union[str, int, float]] = (
            metrics if metrics is not None else {}
        )
        self.dicts: Dict[str, Dict[str, Any]] = dicts if dicts is not None else {}
        self.artifacts: Dict[str, Artifact] = artifacts if artifacts is not None else {}

    def log_param(self, key: str, value: Union[str, int, float]) -> None:
        """Logs a parameter to the experiment run."""
        self.params[key] = value

    def log_metric(self, key: str, value: Union[str, int, float]) -> None:
        """Logs a metric to the experiment run."""
        self.metrics[key] = value

    def log_artifact(
        self,
        src_path_or_bytes: Union[str, bytes],
        artifact_id: str,
        filename: Union[str, None] = None,
        artifact_type: ArtifactType = ArtifactType.BINARY,
    ) -> None:
        """
        Logs an artifact to the experiment run.
        :param str|bytes src_path_or_bytes: The path or byte array to the artifact.
        :param str artifact_id: The id of the artifact.
        :param str|None filename: The run-relative filename of the artifact.
        :param ArtifactType artifact_type: The type of the artifact.
        """
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

    def log_dict(
        self, dict_name: str, data: Dict[str, Union[str, int, float, Any]]
    ) -> None:
        """Logs a dictionary of `data` with the given `dict_name`."""
        if dict_name not in self.dicts:
            self.dicts[dict_name] = {}
        self.dicts[dict_name].update(data)

    def log_figure(
        self,
        fig: Union[
            plotly.graph_objs.Figure, matplotlib.figure.Figure, matplotlib.axes.Axes
        ],
        artifact_id: str,
    ) -> None:
        """Logs a figure to the experiment run."""
        if isinstance(fig, plotly.graph_objs.Figure):
            # Plotly figure
            data = fig.to_json().encode("utf-8")
            filename = f"{artifact_id}.plotly.json"
            artifact_type = ArtifactType.PLOTLY_JSON
        elif isinstance(fig, matplotlib.figure.Figure):
            # Matplotlib figure
            data = matplotlib_fig_to_bytes(fig, format="png")
            filename = f"{artifact_id}.png"
            artifact_type = ArtifactType.PNG
        elif isinstance(fig, matplotlib.axes.Axes):
            # Matplotlib figure
            data = matplotlib_fig_to_bytes(fig.get_figure(), format="png")
            filename = f"{artifact_id}.png"
            artifact_type = ArtifactType.PNG
        else:
            raise Exception(f"Unsupported figure type {type(fig)}")

        self.log_artifact(data, artifact_id, filename, artifact_type)

    def log_image(
        self,
        src_path_or_bytes: Union[str, bytes],
        artifact_id: str,
        filename: Optional[str] = None,
    ) -> None:
        """
        Logs an image with the given artifact_id and either the path to the image file
        (src_path_or_bytes is a string) or the contents of the image file
        (src_path_or_bytes is bytes). If a filename is not provided, the artifact_id
        is used as the filename. The image is stored as a PNG artifact in the artifacts
        dictionary of the ExperimentRun object.
        """

        if filename is None:
            filename = artifact_id
        self.log_artifact(
            src_path_or_bytes,
            artifact_id=artifact_id,
            filename=filename,
            artifact_type=ArtifactType.PNG,
        )

    def log_metrics(self, data: Dict[str, Union[str, int, float]]) -> None:
        """Appends `data` to the `metrics` dict."""
        self.metrics.update(data)

    def log_params(self, data: Dict[str, Union[str, int, float]]) -> None:
        """Appends `data` to the `params` dict."""
        self.params.update(data)

    def log_text(self, text: Union[str, bytes], artifact_id: str) -> None:
        """
        Logs `text` with the given `artifact_id` and `text` (`str` or `bytes` that
        represent utf-8). The text is stored as a binary artifact in the
        ExperimentRun.
        """
        if isinstance(text, str):
            data = text.encode("utf-8")
        elif isinstance(bytes, str):
            data = text

        self.log_artifact(data, artifact_id, artifact_id, ArtifactType.BINARY)
