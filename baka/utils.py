import sys


def _split_spec(path):
    if ':' in path:
        package, subpath = path.split(':', 1)
        return package, subpath
    else:
        return None, path


def _path_setting(path, egg=None):
    package, subpath = _split_spec(path)
    if package is None:
        path = '{egg}:{static}'.format(static=subpath, egg=egg)
    else:
        path = '{egg}:{static}'.format(static=subpath, egg=package)
    return path


def _self_package(package):
    module = sys.modules[package]
    f = getattr(module, '__file__', '')
    if f in ['__init__.py', '__init__$py']:
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit('.', 1)[0]
    return sys.modules[package_name]
