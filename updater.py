import json
import os
import sys
import subprocess
import urllib.request
from packaging import version
import tempfile

class Updater:
    def __init__(self, config_url, current_version):
        self.config_url = config_url
        self.current_version = version.parse(current_version)
        self.latest_version_info = None

    def check_for_updates(self):
        """Verifica se há uma nova versão disponível."""
        try:
            with urllib.request.urlopen(self.config_url) as response:
                self.latest_version_info = json.loads(response.read().decode('utf-8'))

            latest_version = version.parse(self.latest_version_info['version'])

            if latest_version > self.current_version:
                return True
        except Exception as e:
            print(f"Erro ao verificar atualizações: {e}")
        return False

    def download_update(self):
        """Baixa o executável da nova versão."""
        if not self.latest_version_info:
            return None

        url = self.latest_version_info['url']
        filename = os.path.basename(url)
        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, filename)

        try:
            with urllib.request.urlopen(url) as response, open(download_path, 'wb') as out_file:
                out_file.write(response.read())
            return download_path
        except Exception as e:
            print(f"Erro ao baixar a atualização: {e}")
            return None

    def apply_update(self, download_path):
        """Cria e executa um script .bat para aplicar a atualização."""
        if not download_path:
            return False

        executable_path = sys.executable
        current_dir = os.path.dirname(executable_path)

        # O nome do .exe atual (ex: app.exe)
        current_exe_name = os.path.basename(executable_path)

        # O nome do .exe baixado pode ser diferente, vamos usar o nome do atual
        new_exe_path = os.path.join(current_dir, current_exe_name)

        bat_path = os.path.join(tempfile.gettempdir(), 'update.bat')

        with open(bat_path, 'w') as bat_file:
            bat_file.write(f'@echo off\n')
            bat_file.write(f'echo Aguardando o aplicativo fechar...\n')
            bat_file.write(f'timeout /t 2 /nobreak > nul\n') # Espera 2 segundos
            bat_file.write(f'echo Substituindo o arquivo...\n')
            bat_file.write(f'move /y "{download_path}" "{new_exe_path}"\n')
            bat_file.write(f'echo Atualização concluída! Reiniciando o aplicativo...\n')
            bat_file.write(f'start "" "{new_exe_path}"\n')
            bat_file.write(f'del "{bat_path}"\n') # Auto-deleção

        try:
            # Executa o .bat em um novo processo e se desvincula dele
            subprocess.Popen(bat_path, creationflags=subprocess.DETACHED_PROCESS, shell=True)
            return True
        except Exception as e:
            print(f"Erro ao executar o script de atualização: {e}")
            return False
