
import sys
import os
import time
import zipfile
import subprocess
import shutil

def main():
    try:
        # The script is called with: python install_update.py <zip_path> <app_path> <app_pid>
        zip_path = sys.argv[1]
        app_path = sys.argv[2]
        app_pid = int(sys.argv[3])

        # 1. Wait for the main application to exit by checking if the PID is still active
        while True:
            try:
                os.kill(app_pid, 0)
                time.sleep(0.5)
            except OSError:
                # PID does not exist, so the process has terminated
                break

        # The parent application's directory
        install_dir = os.path.dirname(app_path)

        # 2. Unzip the update to a temporary directory
        temp_update_dir = os.path.join(os.path.dirname(zip_path), 'temp_update')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_update_dir)

        # 3. Replace the old files with the new ones
        # A simple but effective method: move the old dir, move the new dir in its place.
        old_app_backup_dir = os.path.join(install_dir, '..', 'UniversalConverter_old')
        if os.path.exists(old_app_backup_dir):
             shutil.rmtree(old_app_backup_dir)

        # Move current installation to a backup location
        shutil.move(install_dir, old_app_backup_dir)

        # Move the new version into the original location
        # The unzipped content is assumed to be in a directory inside temp_update_dir
        # This needs to be robust. Let's assume the unzipped folder is 'UniversalConverter'.
        # This part might need adjustment depending on how the zip is structured.
        # Let's assume for now that the contents are directly inside `temp_update_dir`
        shutil.move(temp_update_dir, install_dir)

        # 4. Relaunch the application
        subprocess.Popen([app_path])

        # 5. Clean up
        os.remove(zip_path)
        shutil.rmtree(old_app_backup_dir, ignore_errors=True)

    except Exception:
        # If anything goes wrong, try to restore the backup
        if 'install_dir' in locals() and 'old_app_backup_dir' in locals():
            if not os.path.exists(install_dir) and os.path.exists(old_app_backup_dir):
                shutil.move(old_app_backup_dir, install_dir)
        # We can't do much more here, but at least we tried to recover.
        pass

if __name__ == "__main__":
    main()
