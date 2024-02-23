import time
import logging
import os
import json
import paramiko
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv


def main():
    """
    This code snippet defines a function named 'main' that performs the following tasks:
    - Sets up logging configuration and creates a logging directory
    - Loads environment variables using the 'dotenv' library
    - Retrieves FTP server details from environment variables and raises a ValueError if any of the details are missing
    - Loads a JSON file containing a list of files to download
    - Loads a JSON file containing configuration settings
    - Creates a local download directory if it doesn't exist
    - Establishes a connection to the FTP server using the 'paramiko' library
    - Iterates a specified number of times to check for new files on the FTP server
    - Retrieves a list of remote files
    - Checks if each file in the remote file list is in the list of files to download
    - Compares the modification time of the local file with the remote file and skips the download if the local file is newer
    - Downloads the remote file to the local directory if it is not already present or if the remote file is newer
    - Removes the downloaded file from the list of files to download
    - Sleeps for a specified delay before checking for new files again
    - Closes the SFTP connection and the transport connection

    The 'main' function is called when the script is run as the main module.
    """
    logging_directory = 'logging'
    os.makedirs(logging_directory, exist_ok=True)

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

    # Load config directory settings
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    remote_directory = config['ftp_remote_directory']
    local_directory = config['local_directory']

    # Crete download directory when not eixist
    os.makedirs(local_directory, exist_ok=True)

    transport = paramiko.Transport((hostname, 22))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(remote_directory)

    for _ in range(config['ftp_check_for_new_files_interations']):
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

        time.sleep(config['ftp_check_for_new_files_interations_delay'])

    sftp.close()
    transport.close()

if __name__ == "__main__":
    main()
