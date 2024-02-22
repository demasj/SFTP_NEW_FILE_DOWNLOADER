import time
import logging
import os
import json
import paramiko
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv


def main():
    """
    This code snippet is a script that connects to an FTP server using the paramiko library and downloads a list of files from a remote directory. 

    The script first sets up logging and loads environment variables from a .env file. It then retrieves the FTP server details from the environment variables and checks if they are provided. 

    Next, the script defines the list of files to download, the remote directory to download files from, and the local directory to save the downloaded files. 
    It creates the local directory if it doesn't exist.

    The script creates a transport object and connects to the FTP server using the provided hostname, username, and password. 
    It then creates an SFTP client from the transport object and changes the current directory to the remote directory.

    The script enters a loop that runs 30 times with a 2-minute delay between each iteration. In each iteration, 
    it retrieves the directory and file listing from the remote directory. 
    It loops through each file in the directory and checks if it is in the list of files to download. 
    If it is, the script constructs the local file path, retrieves the remote file's modification time, 
    and compares it with the local file's modification time. If the local file is newer or the same, 
    the script skips the download. Otherwise, it attempts to download the file using the SFTP client's get() method and removes the file from the list of files to download. 
    If the file does not exist on the remote server, the script prints an error message.

    After each iteration, the script checks if all files have been downloaded. If they have, it breaks out of the loop. Otherwise, it delays for 2 minutes before the next iteration.

    Finally, the script closes the SFTP client and transport connection.

    Note: This code snippet assumes that the necessary dependencies (paramiko, logging, dotenv) are installed and the environment variables (FTP_HOSTNAME, FTP_USERNAME, FTP_PASSWORD) are properly set.
    """
    logger = logging.getLogger('paramiko')
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler('logging/sftp.log', when='midnight', interval=1, backupCount=7)
    logger.addHandler(handler)

    load_dotenv()

    hostname = os.environ.get('FTP_HOSTNAME')
    username = os.environ.get('FTP_USERNAME')
    password = os.environ.get('FTP_PASSWORD')

    if not hostname or not username or not password:
        raise ValueError('FTP server details are not provided in the environment variables.')

    # Load the JSON file
    with open('file_list.json', 'r') as f:
        file_list = json.load(f)

    # Load files to list variable
    files_to_download = file_list['files']

    # Set remote and local locations
    remote_directory = 'files'
    local_directory = 'downloads'

    os.makedirs(local_directory, exist_ok=True)

    transport = paramiko.Transport((hostname, 22))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(remote_directory)

    for _ in range(30):
        remote_files = sftp.listdir()

        for file_name in remote_files:
            if file_name in files_to_download:
                local_file = os.path.join(local_directory, file_name)

                remote_file_info = sftp.stat(file_name)
                remote_mtime = remote_file_info.st_mtime

                if os.path.exists(local_file):
                    local_mtime = os.path.getmtime(local_file)

                    if local_mtime >= remote_mtime:
                        print(f'Skipping download of {file_name}. The file is not newer.')
                        continue

                print(f'Trying to download {file_name} to {local_file}')

                try:
                    sftp.get(file_name, local_file)
                    print(f'Successfully downloaded {file_name} to {local_directory}')
                    files_to_download.remove(file_name)
                except FileNotFoundError:
                    print(f'Failed to download {file_name}. The file does not exist.')

        if not files_to_download:
            break

        time.sleep(120)

    sftp.close()
    transport.close()

if __name__ == "__main__":
    main()
