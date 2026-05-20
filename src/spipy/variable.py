class Variable:
        def __init__(self, name: str):
                self._name = name
                self._value = ''

        def get_name(self) -> str:
                return self._name
        
        def get_value(self) -> str:
                return self._value
        
        def get_value_definition(self) -> str:
                return f'.param {self._name}={self._value}'
        
        def set_value(self, value: str) -> None:
                self._value = value