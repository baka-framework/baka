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

def config_yaml(package, _yaml, config_file=None):
    config_file = '/'.join(('config', config_file or 'config.yaml'))
    config_dir = pkg_resources.resource_string(package, config_file)

    try:
        settings = parse_and_validate(
            config_dir.decode('utf-8'),
            _yaml,
            filename='config.yaml')
    except ConfigError as e:
        e.output()
        raise e

    return settings
