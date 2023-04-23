---
hide:
  - navigation
---

# 🔬 ERM: Experiment Results Manager

Light-weight alternative to `mlflow` experiment tracking that doesn't require kubernetes. Useful tool to compare metrics between training attempts in your model training workflow

## ✨ Features

- 📈 Track plots, metrics, & other data
- 👀 Side-by-side comparison 
- 💾 Experiment registry 
- ⛅️ Supports S3, GCS, Azure and others (via `fsspec`)

## 🚀 Examples & Demos
- Quick and easy: [serialize_and_deserialize.ipynb](https://github.com/ml-cyclops/experiment-results-manager/blob/main/examples/serialize_and_deserialize.ipynb)
- Practical but more involved: [compare_runs.ipynb](https://github.com/ml-cyclops/experiment-results-manager/blob/main/examples/compare_runs.ipynb)
- Browse the registry: [browse_registry.ipynb](https://github.com/ml-cyclops/experiment-results-manager/blob/main/examples/browse_registry.ipynb)


## ✅ Get Started
#### Installation
```sh

pip install experiment-results-manager \
  gcsfs \
  s3fs
# install s3fs if you plan to store data in s3
# install gcsfs if you plan to store data in google cloud storage
```

#### Basic Usage
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
saved_path = erm.save_run_to_registry(er, "s3://erm-registry")

```
<hr>
<p align="center" style="text-align: center; color: gray; font-size: 10px;">
Made with ❤️ in Berlin
</p>
