import os
import requests
import re
from pathlib import Path
from django.db import models


#
#
#
class PFSense:
    
    def __init__(self, url, username, password):
        """
        
        """
        self.url = url
        self.username = username
        self.password = password
        __csrf_magic = ""
        requests.urllib3.disable_warnings()
        self.http_session = requests.session()
        req = self.get_landing_page()
        
        
    def get_landing_page(self):
        """

        """
        req = self.http_session.get(self.url, verify=False)
        if not req.ok:
            print(f'Error requesting firewall landing page at: {pfsense_url}')
        else:
            self.__csrf_magic = re.findall("name='__csrf_magic' value=\"(sid:[a-z0-9,;:]+)\"", req.text)[0]
    
    
    def login(self):
        """
        
        """
        form_data = {
            "usernamefld" : self.username,
            "passwordfld" : self.password,
            "login" : "Sign+In",
            "__csrf_magic" : self.__csrf_magic
        }

        headers = {'content-type': 'application/x-www-form-urlencoded' }
        req = self.http_session.post(self.url, data=form_data, headers=headers, verify=False)
        if req.ok:
            if 'Username or Password incorrect' in req.text:
                print(f'Nome de usuario ou senha invalidos...')
            else:
                self.__csrf_magic = re.findall("name='__csrf_magic' value=\"(sid:[a-z0-9,;:]+)\"", req.text)[0]
                print(f'Successfull login!')
        else:
            pass
    
    
    def backup_config(self, path=None):
        """
        
        """
        form_data = {
            "__csrf_magic": self.__csrf_magic,
            "backuparea": "",
            "donotbackuprrd": "yes",
            "encrypt_password": "",
            "encrypt_password_confirm": "",
            "download": "Download configuration as XML",
            "restorearea": "",
            "decrypt_password": ""   
        }

        req = self.http_session.post(self.url + "/diag_backup.php", data=form_data, verify=False)
        if req.ok:
            # get filename
            filename = req.headers['Content-Disposition'].split("=")[-1]
            #save file
            if path is not None:
                output_file_path = path
            else:
                output_file_path = Path( os.curdir ).resolve().joinpath("files/backup/" + filename)
            f = open(output_file_path, "w+")
            f.write(req.text)
            f.close()
            return str(output_file_path)



