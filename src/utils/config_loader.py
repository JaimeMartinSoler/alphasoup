import yaml

from utils.path_utils import get_fullpath_from_root

PATH_CONFIG = get_fullpath_from_root("config/config.yml")
ENCODING_CONFIG = "utf8"


def _load_config_file(path, encoding=ENCODING_CONFIG):
    with open(path, encoding=encoding) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config


CONFIG = _load_config_file(PATH_CONFIG)
