import sys
import pkg_resources
import trafaret as T
from trafaret_config import parse_and_validate, ConfigError

from baka.log import log

trafaret_yaml = T.Dict({
    T.Key('package'): T.String(),
    T.Key('baka'): T.Dict({
        T.Key('debug_all', default=False): T.Bool(),
        T.Key('meta', optional=True): T.Dict({
            T.Key('version', optional=True): T.String(),
            T.Key('app', optional=True): T.String(),
        })
    }),
})


def merge_yaml(cls, config):
    return cls.merge(config)

def config_yaml(registry, _yaml=None, config_file=None):
    if _yaml is None:
        _yaml = {}
    yaml = registry.trafaret
    yaml = trafaret_yaml if yaml is None else yaml
    return yaml.merge(_yaml)

def validator_settings(registry, settings):
    config_file = '/'.join(('config', settings.get('config') or 'config.yaml'))
    config_dir = pkg_resources.resource_string(registry.package, config_file)
    yaml = registry.trafaret
    if yaml is None:
        yaml = trafaret_yaml
    try:
        settings = parse_and_validate(
            config_dir.decode('utf-8'),
            yaml,
            filename='config.yaml')
    except ConfigError as e:
        e.output()
        log.error(e)
        sys.exit(1)

    return settings


def add_validator_settings(config):
    settings = config.get_settings()
    config.add_settings(validator_settings(config.registry, settings))


def add_trafaret_validator(config, yaml=None):
    """Augment the :term:`deployment settings` with one or more
        key/value pairs.

        You may pass a dictionary::

           config.add_settings({'external_uri':'http://example.com'})

        Or a set of key/value pairs::

           config.add_settings(external_uri='http://example.com')
    """
    config.registry.trafaret = config_yaml(config.registry, _yaml=yaml)


def includeme(config):
    config.add_directive('add_config_validator', add_trafaret_validator)
    config.add_directive('get_settings_validator', add_validator_settings)
