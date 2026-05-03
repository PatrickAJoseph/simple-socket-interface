import ssi
from ssi import SSI
from ssi import SSI_role
from typing import List

def command_1_callback(command: str, args: List[str]) -> List[str]:
    numbers: float = []

    result: float = 0

    for element in args:
        numbers.append(float(element))

    for element in numbers:
        result = result + element

    return [str(result)]

def command_2_callback(command: str, args: List[str]) -> List[str]:
    numbers: float = []

    result: float = 0

    for element in args:
        numbers.append(float(element))

    for element in numbers:
        result = result - element

    return [str(result)]

def command_3_callback(command: str, args: List[str]) -> List[str]:
    numbers: float = []

    result: float = 1

    for element in args:
        numbers.append(float(element))

    for element in numbers:
        result = result * element

    return [str(result)]


x = SSI(SSI_role.SSI_ROLE_RESPONDER, 3300, 3301, 5.0, 5.0)

x.add_command("add", command_1_callback)
x.add_command("subtract", command_2_callback)
x.add_command("multiply", command_3_callback)

while True:
    x.serve()