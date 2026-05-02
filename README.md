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

## Software architecture

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -- Yes --> C[Great!]
    B -- No --> D[Fix it]
    D --> B