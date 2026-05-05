from enum import Enum
import socket
from typing import ByteString
from typing import Callable
from typing import List

class SSI_role(Enum):
    SSI_ROLE_INITIATOR = 0
    SSI_ROLE_RESPONDER = 1

class SSI_status(Enum):
    SSI_OK = 0
    SSI_CMD_NOT_FOUND = 1
    SSI_RQST_TIMEOUT = 2
    SSI_RSP_TIMEOUT = 3
    SSI_CMD_DUPLICATE = 4

class SSI:

    def __init__(self, role: SSI_role,
                 rqst_port:int, 
                 rsp_port:int,
                 rqst_timeout: float,
                 rsp_timeout:float):

        self.__role = role
        self.__rqst_port = rqst_port
        self.__rsp_port = rsp_port
        self.__rqst_timeout = rqst_timeout
        self.__rsp_timeout = rsp_timeout
        self.__iwrr_socket : socket.socket
        self.__irrw_socket : socket.socket
        self.__host = "127.0.0.1"
        self.__command_list : List[(str, Callable)] = []

        # Check arguments.

        if self.__rsp_timeout < 0 or self.__rqst_timeout < 0:
            raise ValueError("Timeouts cannot be negative !")
        
        if self.__rsp_port > 4000 or self.__rsp_port < 3300:
            raise ValueError("Supported port numbers are between 3300 and 4000")
        
        if self.__rqst_port > 4000 or self.__rqst_port < 3300:
            raise ValueError("Supported port numbers are between 3300 and 4000")
        
        if self.__role != SSI_role.SSI_ROLE_INITIATOR and self.__role != SSI_role.SSI_ROLE_RESPONDER:
            raise ValueError("Invalid role assigned !")
        
        # Create required socket connections

        if( role == SSI_role.SSI_ROLE_INITIATOR ):

            self.__irrw_socket = socket.socket()
            self.__irrw_socket.connect( ( self.__host, self.__rsp_port ) )

            self.iwrr_listen_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

            self.iwrr_listen_socket.bind( ( self.__host, self.__rqst_port ) )

            self.iwrr_listen_socket.listen()

            (self.__iwrr_socket, self.iwrr_address) = self.iwrr_listen_socket.accept()


        if( role == SSI_role.SSI_ROLE_RESPONDER ):

            self.irrw_listen_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

            self.irrw_listen_socket.bind( ( self.__host, self.__rsp_port ) )

            print("Listening for a connection on ({_address}, {_port})".format(_address = self.__host, _port = self.__rsp_port))

            self.irrw_listen_socket.listen()

            (self.__irrw_socket, self.irrw_address) = self.irrw_listen_socket.accept()

            print("Accepted a socket connection from the initiator")

            self.__iwrr_socket = socket.socket()
            self.__iwrr_socket.connect( ( self.__host, self.__rqst_port ) )

            print("Connected to responder socket successfully")

    def __read_from_initiator(self) -> bytearray:

        data = b""

        while b'\n' not in data:
            chunk = self.__iwrr_socket.recv(1)
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        
        return data

    def __read_from_responder(self) -> bytearray:

        data = b""

        while b'\n' not in data:
            chunk = self.__irrw_socket.recv(1)
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        
        return data

    def __write_to_initiator(self, payload: bytearray):
        self.__irrw_socket.sendall(payload)
    
    def __write_to_responder(self, payload: bytearray):
        self.__iwrr_socket.sendall(payload)
    
    def add_command(self, command: str, callback: Callable) -> SSI_status:

        if( self.__role == SSI_role.SSI_ROLE_INITIATOR ):
            return SSI_status.SSI_OK

        command_found = False

        for entry in self.__command_list:

            if entry[0] == command or entry[1] == callback:
                command_found = True
                break
        
        if(command_found == False):
            self.__command_list.append((command, callback))
            return SSI_status.SSI_OK
        
        return SSI_status.SSI_CMD_DUPLICATE

    def __get_command_callback(self, command: str) -> Callable:

        for entry in self.__command_list:

            if entry[0] == command:

                return entry[1]
        
        return Callable(None)

    def remove_command(self, command: str) -> SSI_status:

        if( self.__role == SSI_role.SSI_ROLE_INITIATOR ):
            return SSI_status.SSI_OK
        
        index = 0

        for entry in self.__command_list:

            if entry[0] == command:
                self.__command_list.remove((command,self.__get_command_callback(command)))
                return SSI_status.SSI_OK

            index = index + 1
        
        return SSI_status.SSI_CMD_NOT_FOUND

    def __send(self, command: str, args: List[str]):

        if self.__role == SSI_role.SSI_ROLE_INITIATOR:

            request_string = "{type: \"request\", "
            request_string += "command: \"{_command}\", ".format(_command = command)
            request_string += "cmdargs: ["

            args_valid = True

            if( args == None ):
                args_valid = False
            else:
                if( len(args) == 0 ):
                    args_valid = False

            if args_valid == True:
                for index in range(0,len(args)-1):
                    request_string += "\"{_arg}\",".format(_arg = args[index])
                
                request_string += "\"{_args}\"]".format(_args = args[len(args) - 1])
                request_string += "}\n"
            else:
                request_string += "NONE]}\n"

            self.__write_to_responder(bytearray(request_string, encoding = 'utf-8'))

        if self.__role == SSI_role.SSI_ROLE_RESPONDER:

            response_string = "{type: \"response\", "
            response_string += "command: \"{_command}\", ".format(_command = command)
            response_string += "retargs: ["

            for index in range(0,len(args)-1):
                response_string += "\"{_arg}\",".format(_arg = args[index])
            
            response_string += "\"{_args}\"]".format(_args = args[len(args) - 1])
            response_string += "}\n"

            self.__write_to_initiator(bytearray(response_string, encoding = 'utf-8'))
    
    def query(self, command: str, args: List[str]) -> List[str]:

        if self.__role == SSI_role.SSI_ROLE_INITIATOR:
            self.__send(command, args)
            response = (self.__read_from_responder()).decode('utf-8')

            args = response[ response.find("[") + 1: response.find("]") ]

            arg_list: str = []

            n_args = int( args.count("\"") / 2 )

            for i in range(0, n_args):

                index_1 = args.find("\"")

                remaining = args[args.find("\"") + 1 : ]

                index_2 = remaining.find("\"")

                arg = args[ index_1 + 1 : index_2 + 1 ]

                arg_list.append(arg)
                args = args[ index_2 + 3 : ]

            return arg_list
    
    def serve(self):

        if self.__role is SSI_role.SSI_ROLE_RESPONDER:

            request = (self.__read_from_initiator()).decode('utf-8')

            print("Received payload from initiator: {_payload}".format(_payload = request))

            command_start_index = request.find("command: \"") + len("command: \"")
            command = request[command_start_index:]
            command_end_index = command.find("\"")
            command = command[:command_end_index]

            args = request[ request.find("[") + 1: request.find("]") ]

            arg_list: str = []

            n_args = int( args.count("\"") / 2 )

            for i in range(0, n_args):

                index_1 = args.find("\"")

                remaining = args[args.find("\"") + 1 : ]

                index_2 = remaining.find("\"")

                arg = args[ index_1 + 1 : index_2 + 1 ]

                arg_list.append(arg)
                args = args[ index_2 + 3 : ]

            # Find command in the command list

            for entry in self.__command_list:

                if entry[0] == command:

                    retargs = entry[1](command, arg_list)

                    if retargs == None:
                        retargs = ["__None__"]
                    else:
                        if( len(retargs) == 0 ):
                            retargs = ["__None__"]
 
                    self.__send(command,retargs)
                    break