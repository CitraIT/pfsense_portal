#!/usr/local/bin/python3.8
import subprocess
import sys
import socket
import json
from select import select
import requests
import ssl
#import ipdb

# real firewall addresses (localhost)
from urllib3.exceptions import NewConnectionError

LOCAL_ENDPOINT_ADDR = '127.0.0.1'
LOCAL_ENDPOINT_PORT = 8008

# proxy server where to connect and receive requests
server_address = '192.168.0.175'
server_port = 8000

customer_data = {
        "api_key": "2267071a298e42f58c885d64df38647d"
}


if __name__ == "__main__":

    while True:
        # Connect to portal
        # authenticating on portal
        print(f'requesting firewall registration on proxy')
        try:
            req = requests.get(f'http://{server_address}:{server_port}/firewall/connect/{customer_data["api_key"]}')
        except [NewConnectionError, ConnectionError]:
            print(f'connection error with {server_address}:{server_port}')
            continue
        else:
            print(f'requesting firewall registration on proxy done!')

        # parsing result
        server_data = json.loads(req.text)
        if (server_data["authorization"]) == "ok":
            print(f'authorization ok.')
        else:
            print(f'authorization error! check with support!')
            sys.exit(2)

        # connecting to a controle channel where to retrieve commands to execute
        control_port = int(server_data["control_port"])
        print(f'connecting with proxy {server_address} on port {control_port}')

        # setup ssl secure context
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslctx.check_hostname = False
        sslctx.verify_mode = ssl.CERT_NONE
        print(f'creating socket with control endpoint')
        control_endpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'wrapping socket for tls connection')
        secure_proxy_endpoint = sslctx.wrap_socket(control_endpoint, server_hostname="localhost")
        print(f'connecting to control endpoint')
        try:
            secure_proxy_endpoint.connect((server_address, control_port))
        except:
            print(f'error connecting to control endpoint')
            continue

        
        
        # waiting to process requests from control channel
        """
        while True:
            try:
                print(f'waiting for new control requests arrive...')
                control_request = secure_control_endpoint.recv(8192)
                if not control_request:
                    print(f'broken socket detected. stopping')
                    secure_control_endpoint.close()
                    break
            except ConnectionResetError:
                secure_control_endpoint.close()
                break

            # decode request as json
            json_request = json.loads(control_request.decode())
            print(f'received request: ')
            print(json_request)
            print(f'operation: {json_request["op"]}')
            print(f'payload: {json_request["payload"]}')

            if json_request["op"] == 'ping':
                json_response = json.dumps({'success': 'true', 'result': 'pong'})
            elif json_request["op"] == 'quit':
                json_response = json.dumps({'success': 'true', 'result': 'endpoint is shutdown down...'})
            elif json_request["op"] == 'getHostname':
                fw_hostname = subprocess.run("hostname", capture_output=True).stdout.decode().strip()
                json_response = json.dumps({'success': 'true', 'result': {'hostname': fw_hostname}})
            else:
                print(f'unknown operation received in control channel! aborting...')
                break

            # sending response back
            print(f'sending back response as\n{json_response}')
            secure_control_endpoint.sendall(json_response.encode('utf-8'))

            if json_request["op"] == 'quit':
                secure_control_endpoint.close()
                sys.exit(0)
        """








        while True:
            print(f'waiting for new proxy requests arrive...')
            # parse http request from proxy request
            # parse initial browser request
            browser_request = secure_proxy_endpoint.recv(8192)
            if not browser_request:
                print(f'broken socket detected. stopping')
                secure_proxy_endpoint.close()
                break

            request_header_end_index = browser_request.index(b'\r\n\r\n')
            request_headers_txt = browser_request[:request_header_end_index]
            request_body_txt    = browser_request[request_header_end_index+4:]
            request_method, request_url, request_http_version = request_headers_txt[:request_headers_txt.index(b'\r\n')].split(b' ')

            # parse headers in a dict
            # remove first line (request line)
            request_headers_txt = request_headers_txt[request_headers_txt.index(b'\r\n')+2:]
            request_headers = {}
            for header_line in request_headers_txt.split(b'\r\n'):
                header_name, header_value = [ header_line[:header_line.index(b':')].decode(), header_line[header_line.index(b':')+1:].decode()  ]
                request_headers[header_name] = header_value.strip()
            print(f'----- debug headers: ----')
            for k,v in request_headers.items():
                print(f'{k}: {v}')
            print(request_headers)

            # iterate if there is more data
            if request_method == b'POST':
                while len(request_body_txt) < int(request_headers["Content-Length"]):
                    print(f'response body less than content-length. waiting next chuck')
                    request_body_txt += secure_proxy_endpoint.recv(8192)
                    print(f'chunk received')



            # sending received data to real firewall
            if request_method == b'GET':
                req = requests.get(f'http://{LOCAL_ENDPOINT_ADDR}:{LOCAL_ENDPOINT_PORT}{request_url.decode()}', headers=request_headers, allow_redirects=False)
            elif request_method == b'POST':
                post_data = request_body_txt.decode()
                req = requests.post(f'http://{LOCAL_ENDPOINT_ADDR}:{LOCAL_ENDPOINT_PORT}{request_url.decode()}', data=post_data, headers=request_headers, allow_redirects=False)
            else:
                print(f'NOT GET REQUEST')
                print(f'request method {request_method}')


            # send data back to user proxy.
            print(f'sending data back to proxy')
            response = b''
            response = b'HTTP/1.1 ' + (str(req.status_code) + " " + req.reason).encode('utf-8') + b'\r\n'
            print(f'answering headers: {req.headers}')
            for header_key, header_value in req.headers.items():
                if header_key.lower() == "content-encoding":
                    print(f'skipping conte-encoding header')
                    continue
                if header_key.lower() == "transfer-encoding":
                    print(f'transfer-encoding header')
                    continue
                response += (header_key + ": " + header_value + "\r\n").encode('utf-8')
            
            print(f'patching content-length..')
            response += ("Content-Length" + ": " + str(len(req.content)) + "\r\n").encode('utf-8')
            response += b'\r\n'
            response += req.content
            print(f'sending back:')
            # print(response)
            try:
                secure_proxy_endpoint.sendall(response)
            except:
                print(f'error sending response backup to proxy. connection closed?')
            print(f'sent')
















"""
# Connect to portal
    while True:

        # authenticating on portal
        print(f'requeseting firewall registration on proxy')
        try:
            req = requests.get(f'http://{server_address}:{server_port}/firewall/connect/{customer_data["api_key"]}')
        except NewConnectionError:
            print(f'connection error with {server_address}:{server_port}')
            continue
        else:
            print(f'requeseting firewall registration on proxy done!')

        # parsing result
        server_data = json.loads(req.text)
        if(server_data["authorization"]) == "ok":
            print(f'authorization ok.')
        else:
            print(f'authorization error! check with support!')
            sys.exit(2)


        # connecting to a controle channel where to retrieve commands to execute
        proxy_port = int(server_data["proxy_port"])
        print(f'connecting with proxy {server_address} on proxy port {proxy_port}')

        # setup ssl secure context
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslctx.check_hostname = False
        sslctx.verify_mode = ssl.CERT_NONE
        proxy_endpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_proxy_endpoint = sslctx.wrap_socket(proxy_endpoint, server_hostname="localhost")
        secure_proxy_endpoint.connect((server_address, proxy_port))


        while True:
            print(f'waiting for new proxy requests arrive...')
            # parse http request from proxy request
            # parse initial browser request
            browser_request = secure_proxy_endpoint.recv(8192)
            if not browser_request:
                print(f'broken socket detected. stopping')
                secure_proxy_endpoint.close()
                break

            request_header_end_index = browser_request.index(b'\r\n\r\n')
            request_headers_txt = browser_request[:request_header_end_index]
            request_body_txt    = browser_request[request_header_end_index+4:]
            request_method, request_url, request_http_version = request_headers_txt[:request_headers_txt.index(b'\r\n')].split(b' ')

            #parse headers in a dict
            # remove first line (request line)
            request_headers_txt = request_headers_txt[request_headers_txt.index(b'\r\n')+2:]
            request_headers = {}
            for header_line in request_headers_txt.split(b'\r\n'):
                header_name, header_value = [ header_line[:header_line.index(b':')].decode(), header_line[header_line.index(b':')+1:].decode()  ]
                request_headers[header_name] = header_value.strip()
            #print(f'----- debug headers: ----')
            # for k,v in request_headers.items():
                # print(f'{k}: {v}')
            #print(request_headers)

            # iterate if there is more data
            if request_method == b'POST':
                while len(request_body_txt) < int(request_headers["Content-Length"]):
                    print(f'response body less than content-length. waiting next chuck')
                    request_body_txt += secure_proxy_endpoint.recv(8192)
                    print(f'chunk received')



            # sending received data to real firewall
            if request_method == b'GET':
                req = requests.get(f'http://{LOCAL_ENDPOINT_ADDR}:{LOCAL_ENDPOINT_PORT}{request_url.decode()}', headers=request_headers, allow_redirects=False)
            elif request_method == b'POST':
                post_data = request_body_txt.decode()
                req = requests.post(f'http://{LOCAL_ENDPOINT_ADDR}:{LOCAL_ENDPOINT_PORT}{request_url.decode()}', data=post_data, headers=request_headers, allow_redirects=False)
            else:
                print(f'NOT GET REQUEST')
                print(f'request method {request_method}')


            # send data back to user proxy.
            print(f'sending data back to proxy')
            response = b''
            response = b'HTTP/1.1 ' + (str(req.status_code) + " " + req.reason).encode('utf-8') + b'\r\n'
            #print(f'answering headers: {req.headers}')
            for header_key, header_value in req.headers.items():
                if header_key.lower() == "content-encoding":
                    print(f'skipping conte-encoding header')
                    continue
                if header_key.lower() == "transfer-encoding":
                    print(f'transfer-encoding header')
                    continue
                response += (header_key + ": " + header_value + "\r\n").encode('utf-8')

            print(f'patching content-length..')
            response += ("Content-Length" + ": " + str(len(req.content)) + "\r\n").encode('utf-8')
            response += b'\r\n'
            response += req.content
            print(f'sending back:')
            #print(response)
            try:
                secure_proxy_endpoint.sendall(response)
            except:
                print(f'error sending response backup to proxy. connection closed?')
            print(f'sent')
"""

