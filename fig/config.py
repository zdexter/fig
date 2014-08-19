"""Load and validate a fig configuration file.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from collections import namedtuple
import errno
import functools
import re

import colander
from colander import SchemaNode as Node
import yaml

from fig.cli import errors
from fig.packages import six


DOCKER_CONFIG_KEYS = [
    'command',
    'detach',
    'dns',
    'domainname',
    'entrypoint',
    'environment',
    'hostname',
    'image',
    'mem_limit',
    'net',
    'ports',
    'privileged',
    'stdin_open',
    'tty',
    'user',
    'volumes',
    'volumes_from',
    'working_dir'
]


DOCKER_CONFIG_HINTS = {
    'link'      : 'links',
    'port'      : 'ports',
    'privilege' : 'privileged',
    'priviliged': 'privileged',
    'privilige' : 'privileged',
    'volume'    : 'volumes',
    'workdir'   : 'working_dir',
}


VALID_NAME_CHARS = '[a-zA-Z0-9]'


class ConfigError(ValueError):
    pass


def require_dict(value, config_path):
    if not isinstance(value, dict):
        raise ConfigError("Config in \"%s\" is not a dict." % config_path)


def validate_name(value, value_type):
    if not re.match('^%s+$' % VALID_NAME_CHARS, value):
        raise ConfigError(
            'Invalid %s name "%s" - only %s are allowed' % (
                value_type,
                value,
                VALID_NAME_CHARS))


def optional_list(type_, **kwargs):
    return Node(colander.Sequence(accept_scalar=True),
                Node(type_),
                missing=colander.drop,
                **kwargs)


class ServiceConfigSchema(colander.Schema):
    schema_type = functools.partial(colander.Mapping, unknown='preserve')

    detach       = Node(colander.Boolean(), missing=colander.drop)
    dns          = optional_list(colander.String())
    links        = optional_list(colander.String())
    ports        = optional_list(colander.String())
    volumes      = optional_list(colander.String())
    volumes_from = optional_list(colander.String())
    environment  = Node(colander.Mapping(unknown='preserve'), 
                        missing=colander.drop)


def validate_service_config(name, config):
    validate_name(name, "service name")
    if 'image' in config and 'build' in config:
        raise ConfigError('Service %s has both an image and build path '
                          'specified. A service can either be built to '
                          'image or use an existing image, not both.' % name)

    supported_options = DOCKER_CONFIG_KEYS + ['build', 'expose']

    for k in config:
        if k not in supported_options:
            msg = "Unsupported config option for %s service: '%s'" % (name, k)
            if k in DOCKER_CONFIG_HINTS:
                msg += " (did you mean '%s'?)" % DOCKER_CONFIG_HINTS[k]
            raise ConfigError(msg)

    config['name'] = name
    try:
        return name, ServiceConfigSchema().deserialize(config)
    except colander.Invalid as exc:
        raise ConfigError(exc)


def validate_config(config, config_path):
    require_dict(config, config_path)
    # TODO: return as list
    return dict((name, validate_service_config(name, service))
                for name, service in six.iteritems(config))


# TODO: move project name parsing here
ProjectConfig = namedtuple('ProjectConfig', 'name services')


def get_config(config_path):
    try:
        with open(config_path, 'r') as fh:
            config = yaml.safe_load(fh)
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise errors.FigFileNotFound(config_path)
        raise errors.UserError(six.text_type(e))

    return validate_config(config, config_path)
