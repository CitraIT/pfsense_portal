#!/usr/local/bin/python3.8

import sys
import socket
import json
from select import select
import requests
#import ipdb

#LOCAL_ENDPOINT_ADDR = '127.0.0.1'
LOCAL_ENDPOINT_ADDR = '127.0.0.1'
LOCAL_ENDPOINT_PORT = 8008
server_address = '192.168.0.175'
server_port = 8000

customer_data = {
        "api_key": "2267071a298e42f58c885d64df38647d"
}


if __name__ == "__main__":

    # authenticating on portal
    print(f'requeseting firewall registration on proxy')
    req = requests.get(f'http://{server_address}:{server_port}/firewall/connect/{customer_data["api_key"]}')
    print(f'requeseting firewall registration on proxy done!')

    # parsing result
    server_data = json.loads(req.text)
    if(server_data["authorization"]) == "ok":
        print(f'authorization ok.')
    else:
        print(f'authorization error! check with support!')
        sys.exit(2)



    # connecting to reverse proxy if we shall proceed
    proxy_port = int(server_data["proxy_port"])
    print(f'connecting with proxy {server_address} on proxy port {proxy_port}')
    proxy_endpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_endpoint.connect((server_address, proxy_port))


    # waiting for new requests to pass to real firewall
    while True:
        print(f'waiting for new proxy requests arrive...')
        # parse http request from proxy request
        # parse initial browser request
        browser_request = proxy_endpoint.recv(8192)
        if not browser_request:
            continue
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
        print(f'----- debug headers: ----')
        # for k,v in request_headers.items():
            # print(f'{k}: {v}')
        #print(request_headers)

        # iterate if there is more data
        if request_method == b'POST':
            while len(request_body_txt) < int(request_headers["Content-Length"]):
                print(f'response body less than content-length. waiting next chuck')
                request_body_txt += proxy_endpoint.recv(8192)
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
        print(response)
        proxy_endpoint.sendall(response)
        print(f'sent')

