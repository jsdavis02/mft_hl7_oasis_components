# Created June 2019.
# Updates firewall ports on OASIS servers
# Usage: python update_fw.py -o add -n 9999 -p tcp
import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--operation", dest="operation", help="adds or deletes a port")
parser.add_argument("-n", "--port", dest="port_number", help="port number to be added")
parser.add_argument("-p", "--protocol", dest="protocol", help="protocol to be added")
parser.add_argument("-l", "--list", dest="list_ports", help="specify all, lists all open ports")
parser.add_argument("-r", "--refresh", dest="refresh",  help="specify all, executes firewall refresh")
parser.add_argument("-c", "--check", dest="check_port", help="executes netstat and looks for listen mode for specified port")
args = parser.parse_args(sys.argv[1:])

if args.port_number is not None and args.protocol is not None and args.operation == 'add':
    print("Adding port "+args.port_number+" with protocol "+args.protocol+".")
    open_port_cmd = "sudo firewall-cmd --zone=public --add-port="+args.port_number+"/"+args.protocol+" --permanent"
    os.system(open_port_cmd)
    refresh_cmd = "sudo firewall-cmd --reload"
    os.system(refresh_cmd)

elif args.port_number is not None and args.protocol is not None and args.operation == 'remove':
    print("Removing port "+args.port_number+" with protocol "+args.protocol+".")
    close_port_cmd = "sudo firewall-cmd --zone=public --remove-port="+args.port_number+"/"+args.protocol
    os.system(close_port_cmd)
    refresh_cmd = "sudo firewall-cmd --reload"
    os.system(refresh_cmd)

elif args.list_ports is not None:
    list_port_cmd = "sudo firewall-cmd --list-all"
    os.system(list_port_cmd)

elif args.refresh is not None:
    refresh_cmd = "sudo firewall-cmd --reload"
    os.system(refresh_cmd)

elif args.check_port is not None:
    check_port_cmd = "netstat -na | grep "+args.check_port+" | grep LISTEN"
    os.system(check_port_cmd)

else:
    print("No firewall changes made.")
    exit(0)
    