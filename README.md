# Simple Socket Interface

This is a simple request-response based protocol in which a request message containing a command name and arguments (as strings) are passed via one socket and response is read through another socket. Whenever the receiver detectes a command being sent, it will call a suitable callback function in its application layer and send over a response message.

## Request packet syntax

{type: "request", command: "__command_name__", cmdargs: ["__arg1__", "__arg2__", "__arg3__", ..., "__argn__" ]}

**type**: Indicates the type of the message (request/response)

**command**: Name of the command/function to be executed in the receiver. The receiver extracts this string and compares it against available commands in its command table.

**cmdargs**: The arguments for the command in the form of strings.

## Response packet syntax

The receiver sends its response through the second socket in the following format:

{type: "response", command: "__command_name__", retargs: ["__arg1__", "__arg2__", "__arg3__", ..., "__argn__" ]}

**type**: Indicates the type of the message (request/response)

**command**: Name of the command/function to be executed in the receiver. The receiver extracts this string and compares it against available commands in its command table.

**retargs**: The value of the return arguments in string format

## Software flow

Initiator side software flow

```mermaid
graph TD
    A[Application code] --SSP.send(command, args)--> B{Is command found in command list ?}
    B -- Yes --> C[Convert command to request JSON string structure]
    C --> E[Try to send over string over socket]
    E --> F{Packet sent successfully ?}
    F -- Yes --> G[Wait for response packet from server]
    F -- No --> H[Return with error code RQST_TIMEOUT] --> A
    B -- No --> D[Return CMD_NOT_FOUND error code]
    G ---> I{Received response packet from server within timeout}
    I --Yes-->J[Decode the received response packet and store the response arguments/values passed from the server and return status OK]-->A
    I --No--> K[Return error code RSP_TIMEOUT]-->A
    D --> A
```

Responder side software flow

```mermaid
graph TD
    A[Wait for command from initiator] --> B{Received command from initiator ?} --No command--> A

    B --Yes--> C{Is command present in the responder's command list ?}

    C --No--> D[Return error code UNKNOWN_CMD] --> A

    C --Yes--> E[Call the callback function present in the callback list to process received command]

    E --Yes--> A