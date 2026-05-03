import ssi
from ssi import SSI
from ssi import SSI_role

x = SSI(SSI_role.SSI_ROLE_RESPONDER, 3300, 3301, 5.0, 5.0)

print(x.read_from_initiator())