from pathlib import Path
from typing import Union
from yaml import ScalarNode, SequenceNode
from yaml_illuminate.loader import marked_load
from yaml_illuminate.meta_loader import MLoader
from pprint import pprint


class TestUsage:
    def test_tag_constructor(self, include_nodes: Union[ScalarNode, SequenceNode] = None):
        print(include_nodes)
        return include_nodes


test_includes = {
    "!test_tag": TestUsage.test_tag_constructor,
}


with open(Path("Examples/example.yaml"), "r") as str_io:
    test_manifest = marked_load(str_io, MLoader, test_includes, mark_objects=True)
pprint(test_manifest)
