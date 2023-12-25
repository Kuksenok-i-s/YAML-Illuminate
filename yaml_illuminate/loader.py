import yaml
import sys

from typing import Callable, Dict, Any

from yaml_illuminate.meta_loader import MLoader, ManifestWrapper



def loader_decorator(constructors):
    def decorator(cls):
        class AddLoaders(cls):
            if constructors:
                for key, value in constructors.items():
                    cls.add_constructor(key, value)
        return AddLoaders
    return decorator

def marked_load(stream, Loader, constructors:Dict[str, Callable]  = None, mark_objects: bool = True)->Any:
    @loader_decorator(constructors)
    class _Tmp(Loader):
        ...

    if Loader is MLoader and not mark_objects:
        loader = ManifestWrapper(stream=None, mark_objects=mark_objects, root_path=None)
        return yaml.load(stream=stream, Loader=loader)
    else:
        loader = _Tmp(stream)
    return loader.get_single_data()

sys.setrecursionlimit(200)

