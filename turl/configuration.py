import argparse
import http
import pathlib
import re
import uuid

import randomname
import yaml
from schema import Optional, Or, Schema


def is_url(host_string):
    return bool(re.search("^https?://", host_string))


def is_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def is_valid_http_code(value):
    try:
        http.HTTPStatus(value)
        return True
    except ValueError:
        return False


class Configuration:
    _config: dict
    _parser: argparse.ArgumentParser
    _args: argparse.Namespace

    configuration_schema = {
        "version": Or(str, int, float),
        Optional("logger", default={"level": "debug"}): {
            "level": Or("debug", "error", "critical", "warning")
        },
        "turl": {
            "hosts": {
                is_url: Or(
                    None,
                    {
                        Optional("rate", default=1): Or(int, float),
                        Optional("search_pattern", default=None): str,
                    },
                )
            }
        },
        "kafka": {
            "producer": {"bootstrap.servers": str, Optional(str): object},
            "consumer": {
                "bootstrap.servers": str,
                Optional("group.id", default=randomname.get_name()): str,
                Optional(str): object,
            },
            "topics": {"producer": list, "consumer": list},
        },
        "pg": {str: Or(str, int)},
    }

    def __init__(self, filepath=None):
        self._config = dict()
        self._parser = argparse.ArgumentParser(
            description="Turl's command line arguments"
        )
        self._parser.add_argument(
            "--configuration",
            type=str,
            help="path to the yaml configuration file",
            required=False,
            default="",
        )
        self._args = self._parser.parse_args()
        self.filepath = filepath

        if not self.args.configuration and not self.filepath:
            raise ValueError("Please provide configuration file through class or argv")

    @property
    def config(self) -> dict:
        return self._config

    @property
    def args(self) -> argparse.Namespace:
        return self._args

    def fetch_from_file(self) -> dict:
        with pathlib.Path(self.args.configuration or self.filepath) as filepath:
            self._config = yaml.load(filepath.read_text(), Loader=yaml.SafeLoader)
        self._config = self.validate()
        return self._config

    def validate(self) -> dict:
        return Schema(self.configuration_schema).validate(
            self._config, ignore_extra_keys=False
        )

    def __getitem__(self, item):
        return self._config[item]
