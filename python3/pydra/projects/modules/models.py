"""
`Module` for organizing attiributes defined in a module
"""
from enum import Enum, auto
from typing import Any, Dict, Tuple, Generator
from dataclasses import dataclass


def __is_dunder(attr_name: str) -> bool:
    """ check if a given attr_name is `double underscored` one.
    """
    return (
        attr_name.startswith('__') and
        attr_name.endswith('__')
    )


def attr_iter(attr: Any) -> Generator[Tuple[str, Any], None, None]:
    for inner_attr_name in dir(attr):
        if __is_dunder(inner_attr_name):
            continue

        inner_attr = getattr(attr, inner_attr_name)
        yield (inner_attr_name, inner_attr)


class FuncDeclType(Enum):

    TOP_LEVEL = auto()
    CLASS = auto()
    INSTANCE = auto()


@dataclass(frozen=True)
class Function:
    """ Function represents one function
    """

    name: str
    line_begin: int
    line_end: int
    func_decl_type: FuncDeclType

    def to_test(self) -> 'Function':
        return Function(
            name=f'test_{self.name}',
            line_begin=-1,  # TODO
            line_end=-1,  # TODO
            func_decl_type=FuncDeclType.INSTANCE,
        )


@dataclass(frozen=True)
class Class:
    """ Class represents one class
    """

    name: str
    line_begin: int
    line_end: int
    function_map: Dict[str, Function]

    def to_test(self) -> 'Class':
        return Class(
            name=f'Test{self.name}',
            line_begin=-1,  # TODO
            line_end=-1,  # TODO
            function_map={
                f.name: f for f in
                (
                    f.to_test()
                    for f in self.function_map.values()
                )
            },
        )

    def sub(self, _class: 'Class') -> 'Class':
        return Class(
            name=self.name,
            line_begin=-1,  # TODO
            line_end=-1,  # TODO
            function_map={
                k: v for k, v in
                self.function_map.items()
                if k not in _class.function_map
            },
        )


@dataclass(frozen=True)
class Module:
    """ Module represents one module(file)
    """

    function_map: Dict[str, Function]
    class_map: Dict[str, Class]

    def sub(self, _module: 'Module') -> 'Module':
        """ Subtraction of module.

        It returns subtracted module which has attributes
        that are defined in self and not-defined in _module.
        """
        sub_class_map = {
            k: v.sub(_module.class_map[k])
            for k, v in self.class_map.items()
        }
        sub_class_map = {
            k: v for k, v in sub_class_map.items()
            if v.function_map
        }

        return Module(
            function_map={
                k: v for k, v in
                self.function_map.items()
                if k not in _module.function_map
            },
            class_map=sub_class_map,
        )

    def to_test(self) -> 'Module':
        """ Convert self to module for test script.
        """
        return Module(
            function_map={},
            class_map={
                **{
                    c.name: c for c in
                    (
                        _class.to_test() for _class in
                        self.class_map.values()
                    )
                },
                **{
                    'Test': Class(
                        'Test',
                        -1,
                        -1,
                        {
                            f.name: f for f in
                            (
                                function.to_test() for function in
                                self.function_map.values()
                            )
                        }
                    )
                },
            },
        )