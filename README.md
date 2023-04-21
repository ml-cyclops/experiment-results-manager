# ERM: Experiment Results Manager

Light-weight alternative to `mlflow` experiment tracking that doesn't require kubernetes. Useful tool to compare metrics between training attempts in your model training workflow

### Features

- Track plots, metrics, & other data
- Experiment registry (supports S3, GCS, Azure and others via fsspec)
- Comparison view 

## Examples
- Quick and easy: [serialize_and_deserialize.ipynb](examples/serialize_and_deserialize.ipynb)
- Practical but more involved: [compare_runs.ipynb](examples/compare_runs.ipynb)

## Get Started
### Installation
```sh

pip install experiment-results-manager \
  gcsfs \
  s3fs
# install s3fs if you plan to store data in s3
# install gcsfs if you plan to store data in google cloud storage
```

### Basic Usage:
```python
import experiment_results_manager as erm

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

# Display the report (if you are in a notebook)
html = erm.compare_runs(er)
display(HTML(html))

# Save to registry
saved_path = erm.save_run_to_registry(er, "s3:///erm-registry")

```

## Screenshots
<img width="680" alt="image" src="https://user-images.githubusercontent.com/1297369/233116615-dd85a795-4b73-4be9-bced-42ebad5ea164.png">
