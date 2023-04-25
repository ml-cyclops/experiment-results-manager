import posixpath
from typing import List, Optional

from fsspec import AbstractFileSystem

from experiment_results_manager.fsspec_util import get_fs_from_uri

EXPERIMENT_FILE_NAME = ".erm_experiment.json"
VARIANT_FILE_NAME = ".erm_variant.json"
RUN_METADATA_FILE_NAME = "erm_metadata.json"


def remove_scheme_if_exists(uri: str) -> str:
    split_uri = uri.split("://", 1)
    if len(split_uri) == 2:
        return split_uri[1]
    elif len(split_uri) == 1:
        return uri
    else:
        raise ValueError(
            f"Cannot parse URI that contains more than one instance of '://' - {uri}"
        )


def list_experiments(
    registry_uri: str, fs: Optional[AbstractFileSystem] = None
) -> List[str]:
    """
    List experiments in the given registry.

    Args:
        registry_uri (str): The URI of the registry to list experiments for.
        fs (Optional[fsspec.AbstractFileSystem]): The filesystem to use to access the
            registry, by default None.

    Returns:
        List[str]: A list of experiment names.

    """
    if fs is None:
        fs = get_fs_from_uri(registry_uri)

    registry_uri_without_scheme = remove_scheme_if_exists(registry_uri)

    paths = fs.glob(posixpath.join(registry_uri, "**", EXPERIMENT_FILE_NAME))
    experiments = []
    for path in paths:
        path = remove_scheme_if_exists(path)
        experiment_id = path[
            len(registry_uri_without_scheme) + 1 : -len(EXPERIMENT_FILE_NAME) - 1
        ]
        experiments.append(experiment_id)
    return experiments


def list_variants(
    registry_uri: str, experiment_id: str, fs: Optional[AbstractFileSystem] = None
) -> List[str]:
    """
    List the variants available for an experiment in the given registry URI and
        experiment ID.

    Args:
        registry_uri (str): The URI of the registry to list the variants from.
        experiment_id (str): The ID of the experiment to list the variants from.
        fs (Optional[fsspec.AbstractFileSystem], optional): The filesystem to use
            to access the registry.
            If None, a new one will be created for the given experiment ID.
            Defaults to None.

    Returns:
        List[str]: A list of variant names stored for the experiment.
    """
    if fs is None:
        fs = get_fs_from_uri(registry_uri)

    experiment_uri_without_scheme = remove_scheme_if_exists(
        posixpath.join(registry_uri, experiment_id)
    )
    paths = fs.glob(
        posixpath.join(registry_uri, experiment_id, "**", VARIANT_FILE_NAME)
    )
    variants = []
    for path in paths:
        path = remove_scheme_if_exists(path)
        experiment_id = path[
            len(experiment_uri_without_scheme) + 1 : -len(VARIANT_FILE_NAME) - 1
        ]
        variants.append(experiment_id)

    return variants


def list_runs(
    registry_uri: str,
    experiment_id: str,
    variant_id: str,
    fs: Optional[AbstractFileSystem] = None,
) -> List[str]:
    """
    List the runs for the given experiment and variant.

    Args:
        registry_uri (str): The URI of the registry where the experiment is stored.
        experiment_id (str): The ID of the experiment.
        variant_id (str): The ID of the variant.
        fs (Optional[fsspec.AbstractFileSystem], optional): The filesystem to use.
            If None, a new filesystem will be created using fsspec.
            Defaults to None.

    Returns:
        List[str]: A list of strings representing the runs for the given experiment
            and variant.
    """
    if fs is None:
        fs = get_fs_from_uri(registry_uri)

    variant_uri_without_scheme = remove_scheme_if_exists(
        posixpath.join(registry_uri, experiment_id, variant_id)
    )
    paths = fs.glob(
        posixpath.join(
            registry_uri, experiment_id, variant_id, "**", RUN_METADATA_FILE_NAME
        )
    )
    runs = []
    for path in paths:
        path = remove_scheme_if_exists(path)
        experiment_id = path[
            len(variant_uri_without_scheme) + 1 : -len(RUN_METADATA_FILE_NAME) - 1
        ]
        runs.append(experiment_id)

    return runs


def get_latest_run_for_variant(
    registry_uri: str,
    experiment_id: str,
    variant_id: str,
    fs: Optional[AbstractFileSystem] = None,
) -> str:
    """
    Get the latest run for the given experiment and variant.

    Args:
        registry_uri (str): The URI of the registry where the experiment is stored.
        experiment_id (str): The ID of the experiment.
        variant_id (str): The ID of the variant.
        fs (Optional[AbstractFileSystem], optional): The filesystem to use.
            If None, a new filesystem will be created using fsspec.
            Defaults to None.

    Returns:
        str: The latest run for the given experiment and variant.
    """
    if fs is None:
        fs = get_fs_from_uri(registry_uri)
    runs = list_runs(registry_uri, experiment_id, variant_id, fs)
    runs.sort()
    return runs[-1]
