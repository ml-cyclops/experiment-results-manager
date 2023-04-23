import os
from typing import Union

import fsspec


def get_fs_from_uri(uri: str) -> fsspec.AbstractFileSystem:
    return fsspec.filesystem(uri.split(":")[0])


def write_to_file(
    str_or_bytes: Union[str, bytes], uri: str, fs: fsspec.AbstractFileSystem = None
) -> None:
    if fs is None:
        fs = get_fs_from_uri(uri)

    fs.makedirs(os.path.dirname(uri), exist_ok=True)
    with fs.open(uri, "wb") as f:
        if isinstance(str_or_bytes, str):
            data = str_or_bytes.encode("utf-8")
        else:
            data = str_or_bytes
        f.write(data)


def read_file(uri: str) -> bytes:
    with fsspec.open(uri, "rb") as f:
        return f.read()  # type: ignore
