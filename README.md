# ERM: Experiment Results Manager

## Get Started

```sh

pip install experiment-results-manager \
  gcsfs \
  s3fs
# install s3fs if you plan to store data in s3
# install gcsfs if you plan to store data in google cloud storage
```

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

## Screenshots
<img width="680" alt="image" src="https://user-images.githubusercontent.com/1297369/233116615-dd85a795-4b73-4be9-bced-42ebad5ea164.png">
