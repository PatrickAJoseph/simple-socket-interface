import ssi
from ssi import SSI
from ssi import SSI_role
from typing import List

def command_1_callback(command: str, args: List[str]) -> List[str]:
    print("Command 1 callback executed")

def command_2_callback(command: str, args: List[str]) -> List[str]:
    print("Command 2 callback executed")

def command_3_callback(command: str, args: List[str]) -> List[str]:
    print("Command 3 callback executed")

x = SSI(SSI_role.SSI_ROLE_RESPONDER, 3300, 3301, 5.0, 5.0)

x.add_command("COMMAND_1", command_1_callback)
x.add_command("COMMAND_2", command_2_callback)
x.add_command("COMMAND_3", command_3_callback)

print(x.command_list)

x.remove_command("COMMAND_2")

print(x.command_list)