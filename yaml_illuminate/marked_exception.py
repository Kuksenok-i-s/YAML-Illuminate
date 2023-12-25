from yaml.nodes import Node, ScalarNode, SequenceNode
from typing import List, Union, Any, Iterable
from yaml import ScalarNode
import sys, traceback


def exc_hook(type, value, tb):
    trace = traceback.format_tb(tb, limit=1)
    trace = trace[0].split("\n")[0]
    exc = traceback.format_exception_only(type, value)[0]
    print(trace + "\n" + exc)


class GenericException(Exception):
    ...


class GenericMarkedException(GenericException):
    def __init__(
        self,
        node: Node = None,
        message: str = None,
        context: str = None,
        input_list: List[Any] = None,
        description: str = None,
    ):
        if node is not None:
            self.node = node
        else:
            raise Exception("Unable to track down Exception location in initial YAML")
        self.message = message
        self.input_list = input_list
        self.description = description
        self.context = context
        super().__init__(self.message)

    @property
    def main_error_location(self) -> str:
        if isinstance(self.node, Iterable):
            return "Possible errors locations ".join([str(i.start_mark) for i in self.node])
        else:
            return self.node.start_mark

    @staticmethod
    def additional_error_locations(additional_nodes: Union[ScalarNode, SequenceNode, List[Union[ScalarNode, SequenceNode]]]) -> Union[str, List[str]]:
        if isinstance(additional_nodes, Iterable):
            return "Possible errors locations ".join([str(i.start_mark) for i in additional_nodes])
        else:
            return [additional_nodes.node.start_mark]

    @property
    def main_error_value(self) -> Any:
        if isinstance(self.node, Iterable):
            return "Possible errors values ".join([str(i.value) for i in self.node])
        else:
            return self.node.value

    @staticmethod
    def additional_error_values(additional_nodes: Union[ScalarNode, SequenceNode, List[Union[ScalarNode, SequenceNode]]]) -> Any:
        if isinstance(additional_nodes, Iterable):
            return "Possible errors values ".join([str(i.value) for i in additional_nodes])
        else:
            return [additional_nodes.value]

    def find_discrepant_elements(self):
        discrepant_elements = []
        for i in enumerate(self.input_list):
            if type(i[1]) != type(next(enumerate(self.input_list))[1]):
                discrepant_elements.append(i[1])
        return discrepant_elements

    def __str__(self):
        lines = []
        if self.input_list:
            lines.append("\nPossibly discrepant elements")
            lines.append("".join(map(str, self.find_discrepant_elements())))
        lines.append(f"Main problem{str(self.main_error_location)}")
        lines.append(f'Error value is "{str(self.main_error_value)}"')
        if self.description is not None:
            lines.append(self.description)
        if self.message is not None:
            lines.append(self.message)
        return "\n".join(map(str, lines))
