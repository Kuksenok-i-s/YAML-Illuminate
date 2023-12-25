import yaml

from yaml import MarkedYAMLError, ScalarNode, SequenceNode
from yaml.nodes import MappingNode

from typing import Any, Dict, List, TextIO, Iterable, NamedTuple, Union
from collections import namedtuple

from pathlib import Path

from yaml_illuminate.objmaker import AbsTypes
from collections import namedtuple


class ManifestWrapper:
    def __init__(self, stream, root_path: Path, mark_objects: bool, ) -> None:
        self.root_path = root_path
        self.stream = stream
        self.mark_objects = mark_objects

    def __call__(self, stream) -> Any:
        return MLoader(
            stream=stream,
            root_path=self.root_path,
            mark_objects = self.mark_objects
        )


class ManifestLoaderMeta(type):
    def __new__(metacls, __name__, __bases__, __dict__):
        """Add include constructor to class."""
        cls = super().__new__(metacls, __name__, __bases__, __dict__)
        cls.add_constructor("!include", cls.process_include)
        cls.add_constructor("tag:yaml.org,2002:map", cls.construct_mapping)
        cls.add_constructor("tag:yaml.org,2002:seq", cls.construct_sequence)
        return cls


class MLoader(
    yaml.SafeLoader,
    metaclass=ManifestLoaderMeta,
):
    def __init__(self, stream: TextIO, root_path: Path = None, mark_objects=True,):
        super().__init__(stream)
        if root_path is None:
            try:
                self._root_path = Path(stream.name).parent
            except AttributeError:
                self._root_path = Path.cwd()
        else:
            self._root_path = Path(root_path)
        self.mark_objects = mark_objects
    include_paths: List[str] = []

    def construct_mapping(self, node, deep: bool = True):
        type_redefiner = AbsTypes(self.mark_objects)
        if isinstance(node, MappingNode):
            self.flatten_mapping(node)
        g: Dict[str, Any] = super().construct_mapping(node, deep=deep)
        g: Dict[str, Any] = type_redefiner.add_node_attr(g, node)
        if isinstance(node.value, Iterable):
            for i, key in enumerate(g):
                g[key] = type_redefiner.add_node_attr(g[key], node.value[i][1])
                if isinstance(node.value[i], Iterable) and not isinstance(node.value[i], MappingNode):
                    tmp_list = []
                    if isinstance(node.value[i][0], ScalarNode):
                        continue
                    for f in list(zip(g[key], node.value[i])):
                        tmp_list.append(type_redefiner.add_node_attr(f[0], f[1][1]))
                    g[key] = tmp_list
                else:
                    g[key] = type_redefiner.add_node_attr(g[key], node.value[i][1])
        return type_redefiner.add_node_attr(g, node)

    def construct_sequence(self, node, deep=True):
        python_objects = []
        type_redefiner = AbsTypes()
        for child in node.value:
            python_objects.append(type_redefiner.add_node_attr(self.construct_object(child, deep=deep), node))
        return python_objects

    @staticmethod
    def _process_many(include_nodes: Union[ScalarNode, SequenceNode]) -> List[ScalarNode]:
        if isinstance(include_nodes, ScalarNode):
            yield include_nodes
        elif isinstance(include_nodes, SequenceNode):
            if len({value.value for value in include_nodes.value}) != len([value.value for value in include_nodes.value]):
                raise MarkedYAMLError(
                    problem="Check config, possibly you refereed same file several times",
                    problem_mark=include_nodes.start_mark,
                )
            else:
                for i in include_nodes.value:
                    yield i
        else:
            raise MarkedYAMLError(
                problem=f"Unexpected yaml Node value, expected ScalarNode or SequenceNode, but got: {type(include_nodes)}",
                problem_mark=include_nodes.start_mark,
            )

    def iter_include_node(self, include_nodes: Union[List[ScalarNode], SequenceNode]) -> ScalarNode:
        YamlIncInfo: NamedTuple = namedtuple("YamlIncInfo", ["include_node", "file_location", "include_nodes"])
        for include_node in self._process_many(include_nodes):
            file_location = Path.absolute(Path.joinpath(Path(self._root_path), include_node.value))
            self.include_paths.append(file_location)
            if len(set(self.include_paths)) != len(self.include_paths):
                raise MarkedYAMLError(
                    problem=f"Duplicate import found: {include_node.value}",
                    problem_mark=include_nodes.start_mark,
                )

            yield YamlIncInfo(include_node, file_location, include_nodes)

    def process_include(self, include_nodes: Union[List[ScalarNode], SequenceNode] = None) -> List[str]:
        _includes = []
        for include_node in self.iter_include_node(include_nodes):
            try:
                with open(include_node.file_location, "r") as file_io:
                    if include_node.file_location.suffix in [".yaml", ".yml"]:
                        try:
                            wrap_loader = ManifestWrapper(
                                stream=None,
                                root_path=self._root_path,
                                mark_objects=self.mark_objects
                            )
                            tmp_include = yaml.load(file_io, wrap_loader)
                            if self.mark_objects:
                                setattr(tmp_include, "include", True)
                            _includes.append(tmp_include)
                        except MarkedYAMLError as error:
                            raise MarkedYAMLError(
                                problem=f'\n Incorrect yml file: {include_node.file_location} \n Problem is "{error.problem}", \n Problem location "{error.problem_mark}"',
                                problem_mark=f"Originally coming from {include_nodes.start_mark}",
                            )
                        except Exception as error:
                            raise Exception(error)
            except FileNotFoundError as error:
                raise FileNotFoundError(f"Unable to find file {error.filename}")
            except RecursionError as error:
                raise RecursionError(f"Recursive import found. Please check file '{include_node.value}'{include_node.start_mark}")
        return _includes
