"""Load and validate a fig configuration file.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import yaml

from fig.cli import errors
from fig.packages import six
from fig.service import ConfigError


def require_dict(value, value_path):
    if not isinstance(value, dict):
        raise ConfigError("Value \"%s\" at %s is not a dict.", % (
            value, value_path)
    return value


def get_config(config_path):
    try:
        with open(config_path, 'r') as fh:
            return require_dict(yaml.safe_load(fh))
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise errors.FigFileNotFound(config_path)
        raise errors.UserError(six.text_type(e))
