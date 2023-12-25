from typing import Any
from yaml import Node


class AbsTypes:
    def __init__(self, mark_objects: bool = True) -> None:
        self.mark_objects = mark_objects
    class MarkedDict(dict):
        ...

    class MarkedStr(str):
        ...

    class MarkedList(list):
        ...

    class MarkedInt(int):
        ...

    class MarkedFloat(float):
        ...

    def redefine_type(self, object: Any = None) -> Any:
        if not self.mark_objects:
            return object
        if isinstance(object, dict):
            return self.MarkedDict(object)
        elif isinstance(object, list):
            return self.MarkedList(object)
        elif isinstance(object, str):
            return self.MarkedStr(object)
        elif isinstance(object, float):
            return self.MarkedFloat(object)
        elif isinstance(object, int):
            return self.MarkedInt(object)
        else:
            return object

    def add_node_attr(self, object: Any, node: Node) -> None:
        if isinstance(object, bool) or not self.mark_objects:
            return object
        u = self.redefine_type(object=object)
        setattr(u, "yaml_node", node)
        return u
