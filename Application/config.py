from .utils import JsonConfiguration

__all__ = (
    "get_config",
)

_CONFIG_FILE = "server_cfg.json"
_DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 9001
    },
    "database": {
        "host": "localhost",
        "id": "project",
        "password": "toor",
        "encoding": "UTF-8",
        "pool": {
            "min": 2,
            "max": 10,
            "increment": 1
        }
    }
}

_CONFIG = JsonConfiguration(_CONFIG_FILE)
_CONFIG.load()
_CONFIG.set_default(_DEFAULT_CONFIG)
_CONFIG.save()


def get_config():
    return _CONFIG
