import pkg_resources
import trafaret as T
from trafaret_config import parse_and_validate, ConfigError

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

def config_yaml(config, _yaml=None, config_file=None):
    package = config.registry.package
    config_file = '/'.join(('config', config_file or 'config.yaml'))
    config_dir = pkg_resources.resource_string(package, config_file)

    if _yaml is None:
        _yaml = {}
    yaml = config.registry.get('__trafaret', None)
    if yaml is None:
        yaml = trafaret_yaml
    yaml = yaml.merge(_yaml)
    try:
        settings = parse_and_validate(
            config_dir.decode('utf-8'),
            yaml,
            filename='config.yaml')
    except ConfigError as e:
        e.output()
        raise e

    return settings


def includeme(config):
    def add_trafaret_validator(cfg, yaml=None, **kwargs):
        """Augment the :term:`deployment settings` with one or more
            key/value pairs.

            You may pass a dictionary::

               config.add_settings({'external_uri':'http://example.com'})

            Or a set of key/value pairs::

               config.add_settings(external_uri='http://example.com')
        """
        cfg.add_settings(config_yaml(cfg, _yaml=yaml, **kwargs))
    config.add_directive('add_config_validator', add_trafaret_validator)
