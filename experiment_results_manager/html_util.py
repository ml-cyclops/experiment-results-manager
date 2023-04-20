import io
from datetime import datetime
from typing import Any, Dict, List, Set

import matplotlib.axes
import matplotlib.figure


def dicts_to_html_table(data: List[Dict[str, Any]], model_name: str = "") -> str:
    # Get all the unique keys from all the dictionaries
    keys: Set[str] = set()
    for d in data:
        keys.update(d.keys())

    # Create the header row
    html = "<table><tr><th></th>"
    for i in range(len(data)):
        html += f"<th>{model_name} {i+1}</th>"
    html += "</tr>"

    # Create the data rows
    for key in keys:
        html += f"<tr><td>{key}</td>"
        for d in data:
            value = d.get(key, "")
            html += f"<td>{value}</td>"
        html += "</tr>"

    # Close the table
    html += "</table>"

    return html


def timestamps_to_html_table(
    experiment_ids: List[str],
    variant_ids: List[str],
    run_ids: List[str],
    timestamps: List[datetime],
) -> str:
    html = (
        "<table><tr><th></th><th>Experiment id</th><th>Variant id</th>"
        "<th>Run id</th><th>Timestamp (UTC)</th></tr>"
    )
    for i, experiment_id in enumerate(experiment_ids):
        html += (
            f"<tr><td>Run {i+1}</td><td>{experiment_id}</td><td>{variant_ids[i]}</td>"
            f"<td>{run_ids[i]}</td><td>{timestamps[i]}</td></tr>"
        )
    html += "</table>"
    return html


def matplotlib_fig_to_bytes(
    fig: matplotlib.figure.Figure, format: str = "png"
) -> bytes:
    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format=format, bbox_inches="tight")
    img_bytes.seek(0)
    return img_bytes.getvalue()
