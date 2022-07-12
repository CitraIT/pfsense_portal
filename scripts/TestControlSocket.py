import socket
import sys
import json

test_port =45256

def send_command(json_command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', test_port))
    # sending getHostname command
    print(f'sending command: {json_command["op"]}')

    s.sendall(json.dumps(json_command).encode('utf-8'))
    print(f'sent: {json_command}')
    print(f'waiting for response...')
    response = s.recv(8196)
    print(f'received response...')
    print(response.decode())
    s.close()
    return json.loads(response.decode())



if __name__ == '__main__':
    # test getHostnameCommand
    getHostname_command = {'op': 'getHostname', 'payload': ''}
    send_command(getHostname_command)

    # test quitCommand
    quit_command = {'op': 'quit', 'payload': 'shutdown please...'}
    send_command(quit_command)

