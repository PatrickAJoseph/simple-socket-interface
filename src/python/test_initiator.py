import ssi
from ssi import SSI
from ssi import SSI_role

x = SSI(SSI_role.SSI_ROLE_INITIATOR, 3300, 3301, 5.0, 5.0)

print(x.query("add", ["1", "2", "3"]))
print(x.query("subtract", ["1", "2"]))
print(x.query("multiply", ["4", "5", "6"]))