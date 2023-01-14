import os
import pathlib

ROOT_PATH = str(pathlib.Path(__file__).parent.parent.parent)
SRC_PATH = str(pathlib.Path(__file__).parent.parent)


def get_fullpath_from_root(path_rel):
    return _get_fullpath_from_parent(ROOT_PATH, path_rel)


def get_fullpath_from_src(path_rel):
    return _get_fullpath_from_parent(SRC_PATH, path_rel)


def _get_fullpath_from_parent(path_parent, path_rel):
    sep2 = f"{os.sep}{os.sep}"
    sep3 = f"{os.sep}{os.sep}"
    full_path = f"{path_parent}{os.sep}{path_rel}".replace(sep3, os.sep).replace(sep2, os.sep)
    return full_path
