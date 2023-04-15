import base64
from typing import List, Set

import plotly.io
from plotly.offline import get_plotlyjs

from experiment_results_manager.artifact import ArtifactType
from experiment_results_manager.experiment_run import ExperimentRun
from experiment_results_manager.render_html import dicts_to_html_table


def compare_runs(*runs: ExperimentRun) -> str:
    html = ""
    html += "<h2>Params</h2>"
    html += dicts_to_html_table([er.params for er in runs])
    html += "<h2>Metrics</h2>"
    html += dicts_to_html_table([er.metrics for er in runs])
    html += "<h2>Artifacts</h2>"

    artifact_keys_set: Set[str] = set()
    for er in runs:
        artifact_keys_set.update(er.artifacts.keys())
    artifact_keys: List[str] = list(artifact_keys_set)
    artifact_keys.sort()

    add_plotlyjs_to_html = False
    for k in artifact_keys:
        html += f"<h3>{k}</h3>"
        for i, run in enumerate(runs):
            if k in run.artifacts:
                html += f"<h4>Run {i+1}</h4>"
                artifact = run.artifacts[k]
                if artifact.artifact_type == ArtifactType.PLOTLY_JSON:
                    render_pl_fig = plotly.io.from_json(artifact.bytes.decode("utf-8"))
                    add_plotlyjs_to_html = True
                    html += render_pl_fig.to_html(
                        full_html=False, include_plotlyjs=False
                    )
                elif artifact.artifact_type == ArtifactType.IMAGE_PNG:
                    b64_img = base64.b64encode(artifact.bytes)
                    html += '<img src="data:image/png;base64,'
                    html += b64_img.decode("utf-8")
                    html += '">'

    if add_plotlyjs_to_html:
        _window_plotly_config = """\
            <script type="text/javascript">\
            window.PlotlyConfig = {MathJaxConfig: 'local'};\
            </script>"""
        load_plotlyjs = """\
            {win_config}
            <script type="text/javascript">{plotlyjs}</script>\
            """.format(
            win_config=_window_plotly_config, plotlyjs=get_plotlyjs()
        )
        html = load_plotlyjs + html

    html = "<html><body>" + html + "</body></html>"
    return html
