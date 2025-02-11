"""
Programme de synchronisation de fichiers avec un serveur FTP
"""
import ftplib
import os
import time
import base64

FICHIER_IMPORTER = ('.html', '.php', '.css', '.py')

# ------------------- FileZilla ------------------- #
SERVER = 'etu-mysql.iut2.univ-grenoble-alpes.fr'
REMOTE_FOLDER = 'web/prog_web/' # Toute l'arborescence contenu actuellement dans le dossier du script sera synchronisée avec le serveur FTP

# ------------------- CyberDuck ------------------- #
# Installer les modules watchdog
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    os.system('pip install watchdog')
    print('Redémarrer le programme !')
    exit()
# ------------------------------------------------- #

def get_credentials() -> tuple:
    """
    Demande les identifiants de connexion au serveur FTP si le fichier credentials.txt n'existe pas
    Sinon les récupère dans le fichier credentials.txt

    Returns:
    - credentials (tuple): username, password
    """
    path = os.path.join(os.path.dirname(__file__), 'credentials.txt')
    if not os.path.exists(path):
        username = input('Identifiant UGA: ')
        password = input('Mdp UGA: ')
        with open(path, 'w', encoding='utf-8') as file:
            encoded_username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
            encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
            file.write(f'{encoded_username}:{encoded_password}')
    with open(path, 'r', encoding='utf-8') as file:
        liste = file.read().strip().split(':')
        username = liste[0]
        password = liste[1]
        username = base64.b64decode(username).decode('utf-8')
        password = base64.b64decode(password).decode('utf-8')
    return username, password

def connect_ftp(server, username, password) -> ftplib.FTP:
    """
    Connection à un serveur FTP

    Args:
    - server (str): Adresse du serveur FTP
    - username (str): Username
    - password (str): MDP

    Returns:
    - ftp (ftplib.FTP): FTP connection
    """
    ftp = ftplib.FTP(server)
    ftp.login(user=username, passwd=password)
    return ftp


def upload_file(ftp, file_path, remote_path):
    """
    Upload un fichier sur le serveur FTP

    Args:
    - ftp (ftplib.FTP): Connection FTP
    - file_path (str): Chemin du fichier local
    - remote_path (str): Chemin du fichier sur le serveur
    """
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_path}', file)

def create_remote_directory(ftp, remote_directory):
    """
    Créé un dossier sur le serveur FTP

    Args:
    - ftp (ftplib.FTP): Connection FTP
    - remote_directory (str): Chemin du fichier sur le serveur
    """
    dirs = remote_directory.split('/')
    path = ''
    for file in dirs:
        path = f"{path}/{file}" if path else file
        try:
            ftp.mkd(path)
        except ftplib.error_perm as e:
            if not str(e).startswith('550'):
                raise

def sync_folder(ftp, local_folder, remote_folder):
    """
    Fonction de synchronisation de fichiers

    Args:
    - ftp (ftplib.FTP): Connection FTP
    - local_folder (str): Chemin du dossier local
    - remote_folder (str): Chemin du dossier sur le serveur
    """
    print('Synchronisation en cours...')
    for root, dirs, files in os.walk(local_folder):
        for file in dirs:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            remote_path = os.path.join(remote_folder, relative_path).replace('\\', '/')
            create_remote_directory(ftp, remote_path)
        for file in files:
            if not file.endswith(FICHIER_IMPORTER):
                continue
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            remote_path = os.path.join(remote_folder, relative_path).replace('\\', '/')
            upload_file(ftp, local_path, remote_path)


class SyncEventHandler(FileSystemEventHandler):
    """
    Ajoute un événement de synchronisation lorsqu'un fichier est modifié
    """
    def __init__(self, connexion_ftp, local_folder, remote_folder):
        self.connexion_ftp = connexion_ftp
        self.local_folder = local_folder
        self.remote_folder = remote_folder

    def on_modified(self, event):
        if any(event.src_path.endswith(ext) for ext in FICHIER_IMPORTER):
            sync_folder(self.connexion_ftp, self.local_folder, self.remote_folder)
            print(f'Synchronisation de {event.src_path} terminée')

    def on_moved(self, event):
        if any(event.dest_path.endswith(ext) for ext in FICHIER_IMPORTER):
            # Supprimer l'ancien fichier du serveur FTP
            old_file_path = os.path.relpath(event.src_path, self.local_folder)
            remote_old_file_path = os.path.join(self.remote_folder, old_file_path).replace("\\", "/")
            try:
                self.connexion_ftp.delete(remote_old_file_path)
                print(f'Ancien fichier supprimé : {remote_old_file_path}')
            except ftplib.error_perm as e:
                print(f'Erreur lors de la suppression de {remote_old_file_path} : {e}')

            # Synchroniser le dossier pour ajouter le nouveau fichier
            sync_folder(self.connexion_ftp, self.local_folder, self.remote_folder)
            print('Fichier renommé, synchronisation terminée')

    def on_deleted(self, event):
        if any(event.src_path.endswith(ext) for ext in FICHIER_IMPORTER):
            # Supprimer le fichier du serveur FTP
            file_path = os.path.relpath(event.src_path, self.local_folder)
            remote_file_path = os.path.join(self.remote_folder, file_path).replace("\\", "/")
            try:
                self.connexion_ftp.delete(remote_file_path)
                print(f'Fichier supprimé : {remote_file_path}')
            except ftplib.error_perm as e:
                print(f'Erreur lors de la suppression de {remote_file_path} : {e}')

def main():
    """
    Fonction principale
    """
    username, password = get_credentials()
    local_folder = os.path.dirname(__file__)

    connexion_ftp = connect_ftp(SERVER, username, password)

    event_handler = SyncEventHandler(connexion_ftp, local_folder, REMOTE_FOLDER)
    observer = Observer()
    observer.schedule(event_handler, path=local_folder, recursive=True)
    observer.start()

    try:
        print('Synchronisation activée ✅')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
