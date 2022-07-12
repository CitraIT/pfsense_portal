import json
import random
from threading import Thread
import socket
import sys
import ipdb
from select import select
import ssl
import os
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Firewall
from .forms import FirewallForm



SOCKET_BIND_ADDR = '0.0.0.0'

#
#
#
@login_required
def index(request):
    firewalls = Firewall.objects.all()
    return render(request, 'firewall/firewall.html', context={'firewalls': firewalls})



#
#
#
@login_required
def add_firewall(request):
    submitted = False
    if request.method == "POST":
        form = FirewallForm(request.POST)
        if form.is_valid():
            firewall = form.save()
            return HttpResponseRedirect(f'/firewall/')
    else:
        form = FirewallForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'firewall/add.html', context={'form':form, 'submitted':submitted})



#
#
#
@login_required
def edit_firewall(request, firewall_id):
    if request.method == "GET":
        firewall = Firewall.objects.get(id=firewall_id)
        form = FirewallForm(instance=firewall)
        return render(request, "firewall/edit.html", {'form': form, 'firewall': firewall})
    elif request.method == "POST":
        firewall = Firewall.objects.get(id=firewall_id)
        form = FirewallForm(request.POST, instance=firewall)
        submitted = False
        if form.is_valid():
            form.save()
            submitted = True
            return render(request, "firewall/edit.html", {'form': form, 'submitted': submitted, 'firewall': firewall })
        else:
            return render(request, "firewall/edit.html", {'form': form})



#
#
#
@login_required
def delete_firewall(request, firewall_id):
    firewall = Firewall.objects.get(id=firewall_id)
    firewall.delete()
    return render(request, "firewall/delete.html", {'firewall': firewall, 'submitted': True})



#
#
#
def connect_firewall(request, api_key):
    firewall = Firewall.objects.get(api_key=api_key)
    firewall.is_online = True

    print(f'received a new request for firewall with api_key {api_key}')
    print(f'firewall have name of {firewall.name}')
    # TODO: make random port not conflict with others in use
    #port = 45000
    port = random.choice([x for x in range(44000, 45000)])
    #user_reverse_port = random.choice([x for x in range(44000, 45000)])
    #firewall.user_reverse_port = user_reverse_port

    firewall.control_channel_port = port
    firewall.save()
    # 
    t = Thread(target=start_new_proxy_thread, args=(api_key, port), daemon=True)
    #t = Thread(target=start_new_control_channel, args=(api_key, port), daemon=True)
    t.start()
    resp = {'authorization': 'ok', 'control_port': port}
    return HttpResponse(json.dumps(resp))



# start_new_control_channel
# starts a new socket (control channel) with the remote firewall agent
# its used to send commands from the portal app to the firewall agent
def start_new_control_channel(api_key, port):
    firewall = Firewall.objects.get(api_key=api_key)
    print(f'starting a new control channel for firewall {firewall.name}')
    # ssl context for secure connection between the proxy and the firewall endpoint
    control_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    print(f'trying to load reverse_endpoint certificate and private key from dir')
    control_ctx.load_cert_chain('reverse_endpoint.pem', 'reverse_endpoint.key')

    # setup connection to remote firewall endpoint
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.bind((SOCKET_BIND_ADDR, port))
    control_socket.listen(10)
    control_socket_secure = control_ctx.wrap_socket(control_socket, server_side=True)
    print(f'waiting for firewall control connection on {SOCKET_BIND_ADDR}:{port}...')
    firewall_endpoint, firewall_addr = control_socket_secure.accept()
    print(f'[proxy] firewall successfully connected  from {firewall_endpoint.getpeername()}')

    # open a local socket to wait for local commands to send to this firewall
    # see a list if example commands bellow.
    local_command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # local_port = random.choice([x for x in range(45000, 46000)])
    local_port = 45256
    print(f'local port for control channel: {local_port}')
    local_command_socket.bind(('127.0.0.1', local_port))
    local_command_socket.listen()
    firewall.local_command_port = local_port
    firewall.save()

    while True:
        try:
            print(f'waiting for new local control channel connection...')
            local_socket, _ = local_command_socket.accept()
            print(f'connection received')
            request = local_socket.recv(8196)
            print(f'request receiving from local control channel')
            print(request)
            firewall_endpoint.sendall(request)
            print(f'data sent though remote control channel')
            response = firewall_endpoint.recv(8196)
            print(f'data recvd from remote control channel')
            print(response)
            local_socket.sendall(response)
            print(f'data sent to local control channel')
            # local_socket.close()
        except:
            print(f'exception in socket send/receive')
            firewall_endpoint.close()
            break
        # finally:
        #     local_socket.close()
    """
    //TODO
    // TESTAR USUÁRIO CLICAR EM GERENCIAR O Firewall
    // VAI CHAMAR VIEW QUE VAI ENVIAR COMANDO PARA O SOCKET LOCAL
    // QUE VAI CHEGAR NA THREAD OUVINDO NA PORTA LOCAL
    // QUE VAI ENVIAR COMANDO PARA O FIREWALL REMOTO
    // QUE VAI CONECTAR EM OUTRA PORTA LOCAL
    // ESTA OUTRA PORTA LOCAL VAI EXECUTAR O PROXY DAS CONEXÕES
    // QUE VAI FAZER UM TUNEL DIRETO ENTRE O USUÁRIO E O FIREWALL REMOTO (webgui)
    """

    # sending test commands:
    # print(f'sending test commands...')
    # print(f'sending `ping` command')
    # ping_command = {'op': 'ping', 'payload': 'ping'}
    # firewall_endpoint.sendall(json.dumps(ping_command).encode('utf-8'))
    # print(f'sent: {ping_command}')
    # print(f'waiting for command response...')
    # response = firewall_endpoint.recv(8196)
    # print(f'received response: ')
    # print(response.decode())

    # sending quit command
    # print(f'sending quit command:')
    # quit_command = {'op': 'quit', 'payload': 'shutdown please...'}
    # firewall_endpoint.sendall(json.dumps(quit_command).encode('utf-8'))
    # print(f'sent: {quit_command}')
    # print(f'waiting for response...')
    # response = firewall_endpoint.recv(8196)
    # print(f'received response...')
    # print(response.decode())
    # firewall_endpoint.close()

    # # sending getHostname command
    # print(f'sending command: getHostname')
    # getHostname_command = {'op': 'getHostname', 'payload': ''}
    # firewall_endpoint.sendall(json.dumps(getHostname_command).encode('utf-8'))
    # print(f'sent: {getHostname_command}')
    # print(f'waiting for response...')
    # response = firewall_endpoint.recv(8196)
    # print(f'received response...')
    # print(response.decode())
    # #firewall_endpoint.close()
    #
    # # sending quit command
    # print(f'sending quit command:')
    # quit_command = {'op': 'quit', 'payload': 'shutdown please...'}
    # firewall_endpoint.sendall(json.dumps(quit_command).encode('utf-8'))
    # print(f'sent: {quit_command}')
    # print(f'waiting for response...')
    # response = firewall_endpoint.recv(8196)
    # print(f'received response...')
    # print(response.decode())
    # firewall_endpoint.close()
    # return






#
#
#
def start_new_proxy_thread(api_key, port):
    # ssl context for secure connection between the proxy and the firewall endpoint
    proxy_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    print(f'trying to load reverse_endpoint certificate and private key from dir')
    print(os.path.realpath(os.curdir))
    proxy_ctx.load_cert_chain('reverse_endpoint.pem', 'reverse_endpoint.key')

    firewall = Firewall.objects.get(api_key=api_key)

    # setup connection from remote firewall
    print(f'iniciando nova thread para proxy com api_key: {api_key}')
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((SOCKET_BIND_ADDR, port))
    proxy_socket.listen(10)
    proxy_socket_secure = proxy_ctx.wrap_socket(proxy_socket, server_side=True)

    print(f'waiting for firewall connection on {SOCKET_BIND_ADDR}:{port}...')
    firewall_endpoint, firewall_addr = proxy_socket_secure.accept()
    print(f'[proxy] firewall successfully connected  from {firewall_endpoint.getpeername()}')

    # wait connecton from remote user
    user_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    user_ctx.verify_mode = ssl.CERT_NONE
    print(f'trying to load reverse_proxy certificate and private key from dir')
    print(os.path.realpath(os.curdir))
    user_ctx.load_cert_chain('reverse_proxy.pem', 'reverse_proxy.key')
    # user_ctx.load_cert_chain('reverse_proxy.pem')

    user_port = firewall.user_reverse_port
    user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_user_socket = user_ctx.wrap_socket(user_socket, server_side=True)
    #user_socket.bind((SOCKET_BIND_ADDR, user_port))
    #user_socket.listen()
    secure_user_socket.bind((SOCKET_BIND_ADDR, user_port))
    secure_user_socket.listen()
    print(f'waiting for user connection on http://{SOCKET_BIND_ADDR}:{user_port}...')

    while True:
        # parse user browser request
        try:
            browser_endpoint, browser_addr = secure_user_socket.accept()
            browser_request = browser_endpoint.recv(8192)
        except ssl.SSLError:
            print('SSL Error. probably the client does not trust our self signed certificate yet...')
            continue
        except ConnectionAbortedError:
            print(f'browser request aborted...')
            continue
            #browser_endpoint.close()
        except OSError:
            print(f'OSError...')
            continue
        else:
            if not browser_request:
                print(f'empty request... skipping it')
                browser_endpoint.close()
                continue


        request_header_end_index = browser_request.index(b'\r\n\r\n')
        request_headers_txt = browser_request[:request_header_end_index]
        print(f'user browser headers: ')
        print(request_headers_txt)
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
        #print(request_headers)


        # sending received data to firewall endpoint
        firewall_endpoint.sendall(browser_request)

        # parsing response heades:
        #try:
        firewall_response = firewall_endpoint.recv(8192)
        #except OSError:
        #    print(f'oserror at reading data from firewall endpoint')
        print(f'debug firewall response')
        print(firewall_response[:100])
        if not firewall_response:
            browser_endpoint.sendall(firewall_response)
            print(f'sent')
            browser_endpoint.close()
            continue
        firewall_header_end_index = firewall_response.index(b'\r\n\r\n')
        firewall_headers_txt = firewall_response[:firewall_header_end_index]
        firewall_body_txt    = firewall_response[firewall_header_end_index+4:]

        #print(f'test response first header line: ')
        #print(firewall_headers_txt[:firewall_headers_txt.index(b'\r\n')].split(b' '))
        # response_version, response_status, response_reason = [x.strip() for x in firewall_headers_txt[:firewall_headers_txt.index(b'\r\n')].split(b' ') ]
        tmp_response_first_line = firewall_headers_txt[:firewall_headers_txt.index(b'\r\n')]
        response_version = tmp_response_first_line[:tmp_response_first_line.index(b' ')]

        tmp_response_first_line = tmp_response_first_line[tmp_response_first_line.index(b' ')+1:]
        response_status  = tmp_response_first_line[:tmp_response_first_line.index(b' ')]

        tmp_response_first_line = tmp_response_first_line[tmp_response_first_line.index(b' ')+1:]
        response_reason  = tmp_response_first_line
        #print(f'response debug: ')
        #print(f'version: {response_version}, status: {response_status}, reason: {response_reason}')
        #, response_reason = [x.strip() for x in ].split(b' ') ]


        firewall_headers_txt = firewall_headers_txt[firewall_headers_txt.index(b'\r\n')+2:]
        response_headers = {}
        for header_line in firewall_headers_txt.split(b'\r\n'):
            header_name, header_value = [ header_line[:header_line.index(b':')].decode(), header_line[header_line.index(b':')+1:].decode()  ]
            response_headers[header_name] = header_value.strip()

        # patch keep alive
        if not 'Connection' in response_headers:
            response_headers['Connection'] = 'close'
            print(f'patched CONNECTION header')
        #print(f'----- debug response headers: ----')
        #print(response_headers)
        #print(f'received content-length: {response_headers["Content-Length"]}')

        # iterate if there is more data
        while len(firewall_body_txt) < int(response_headers["Content-Length"]):
            print(f'response body less than content-length. waiting next chuck')
            firewall_body_txt += firewall_endpoint.recv(8192)
            print(f'chunk received')


        # send data back to user proxy.
        print(f'sending data back to browser')
        response = b''
        response = b'HTTP/1.1 ' + response_status + b' ' + response_reason + b'\r\n'
        #print(f'answering headers: {req.headers}')
        for header_key, header_value in response_headers.items():
            if header_key.lower() == "content-encoding":
                print(f'skipping conte-encoding header')
                continue
            if header_key.lower() == "transfer-encoding":
                print(f'transfer-encoding header')
                continue
            response += (header_key + ": " + header_value + "\r\n").encode('utf-8')

        print(f'patching content-length..')
        response += ("Content-Length" + ": " + str(len(firewall_body_txt)) + "\r\n").encode('utf-8')
        response += b'\r\n'
        response += firewall_body_txt
        print(f'sending back:')
        #print(response)
        try:
            browser_endpoint.sendall(response)
            print(f'sent')
        except ConnectionAbortedError:
            print(f'connection aborted by browser...')
        except BrokenPipeError:
            print(f'broken pipe with browser...')
        finally:
            browser_endpoint.close()

