#!/usr/bin/python
import xmlrpclib

rpc = xmlrpclib.ServerProxy('http://localhost:7978')
print rpc.status()
