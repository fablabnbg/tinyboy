#!/bin/sh
# pronterface and pronsole speak xmlrpc
/bin/echo -e "POST /RPC2 HTTP/1.1\r\nContent-Length: 100\r\n\r\n<?xml version='1.0'?>\n<methodCall>\n<methodName>status</methodName>\n<params>\n</params>\n</methodCall>"  | nc localhost 7978
