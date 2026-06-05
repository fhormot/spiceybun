from enum import Enum
from typing import Literal, Union
import copy

class Variable:
        class _Type(Enum):
                VARIABLE = 'variable'
                LIBRARY = 'library'
                EQUATION = 'equation'

        # Define allowed types for type hints
        TypeLiteral = Literal['variable', 'equation', 'library']

        def __init__(self, name: str, type: TypeLiteral = 'variable') -> None:
                self._name = name
                self._type = self._Type(type).value
                self._value = ''
                self._path = ''

                if self._type == self._Type.LIBRARY.value:
                        self._path = name

        def get_name(self) -> str:
                return self._name
        
        def get_value(self) -> str:
                return self._value
        
        def get_value_definition(self) -> str:                     
                if self._type == self._Type.EQUATION.value:
                        return f".param {self._name}='{self._value}'"

                if self._type == self._Type.LIBRARY.value:
                        return f'.lib {self._path} {self._value}'

                # Variable
                return f'.param {self._name}={self._value}'
        
        def set_value(self, value: str) -> None:
                self._value = value

        def get_split(self) -> list:
                if not isinstance(self._value, list):
                        return [self]

                return_list = []

                for idx, variable in enumerate(self.get_value()):
                        object_copy = copy.deepcopy(self)

                        object_copy.set_value(variable)
                        return_list.append(object_copy)

                return return_list