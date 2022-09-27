# pfsense_portal
Web Portal for Managing pfSense Instances


Instalação:


Instalar o pacote System Patches.
Adicioanr o Patch: nginx_path_listen_localhost.
Aplicar o Patch adicionado.
Acessar a página System -> Advanced e salvar a configuração apenas para atualizar o patch.


# Instalar a lib requests no python dentro do pfSense


cd
curl -OL https://github.com/kennethreitz/requests/zipball/master
tar -zxvf master
rm -rf master
cd kennethreitz-requests-*
/usr/local/bin/python3.8 setup.py install




