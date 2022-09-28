# pfsense_portal
Web Portal for Managing pfSense Instances


Instalação:


Instalar o pacote System Patches.
Adicioanr o Patch: nginx_path_listen_localhost.
Aplicar o Patch adicionado.
Acessar a página System -> Advanced e salvar a configuração apenas para atualizar o patch.
Acessar o console do firewall e reiniciar o serviço WebConfigurator (opção 11)


# Instalar a lib requests no python dentro do pfSense
Habilitar o serviço SSH, acessar o firewall via SSH e executar os comandos abaixo

cd
curl -OL https://github.com/kennethreitz/requests/zipball/master
tar -zxvf master
rm -rf master
cd kennethreitz-requests-*
/usr/local/bin/python3.8 setup.py install


instalar o arquivo portal_endpoint.sh
chmod +x /usr/local/etc/rc.d/portal_endpoint.sh

instalar o arquivo portal_endpoint.py
chmod +x /usr/local/sbin/portal_endpoint.py

iniciar o serviço portal_endpoint






