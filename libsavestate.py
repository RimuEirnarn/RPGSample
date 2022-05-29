"""Lib Save State"""

from pickle import Unpickler, UnpicklingError
from typing import Union
from builtins import int as b_int, float as b_float, str as b_str, tuple as b_tuple, list as b_list, dict as b_dict, bool as b_bool
from io import BytesIO

# State files must NOT imports any objects. Anything that's besides int, float, string, bytes, tuple, list, dict, and bool is raised.


class ReturnState(Unpickler):

    def find_class(self, module: str, name: str) -> Union[int, str, float, bytes, tuple, list, dict, bool]:
        if name in ('int', 'str', 'float', 'bytes', 'tuple', 'dict', 'bool'):
            return globals().get(f"b_{name}")
        raise UnpicklingError(f"As for module {module}: {name} is prohibited.")

    @staticmethod
    def unload(data: Union[str, bytes]) -> Union[int, str, float, bytes, tuple, list, dict, bool]:
        if isinstance(data, str):
            data = data.decode()
        return ReturnState(BytesIO(data)).load()


if __name__ == '__main__':
    from pickle import dumps

    function = dumps
    x = dumps(function)
    print(ReturnState.unload(x))
    exit(0)
