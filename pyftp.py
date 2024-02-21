import logging
import os
import paramiko
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('paramiko')
logger.setLevel(logging.DEBUG)

# Create a handler, to rotate the log every day and keep the last 7 days
handler = TimedRotatingFileHandler('sftp.log', when='midnight', interval=1, backupCount=7)
logger.addHandler(handler)

# FTP server details
hostname = 'localhost'
username = 'ftpuser'
password = 'ftppass'

# Remote directory to download files from
remote_directory = 'files'

# Local directory to save files
local_directory = 'downloads'

# Ensure local directory exists
os.makedirs(local_directory, exist_ok=True)

# Create a transport object
transport = paramiko.Transport((hostname, 22))

# Connect to the server
transport.connect(username=username, password=password)

# Create an SFTP client
sftp = paramiko.SFTPClient.from_transport(transport)

# Change to the remote directory
# Change the “current directory” of this SFTP session. Since SFTP doesn’t really have the concept of a current working directory, 
# this is emulated by Paramiko. Once you use this method to set a working directory, 
# all operations on this SFTPClient object will be relative to that path. You can pass in None to stop using a current working directory.
sftp.chdir(remote_directory)

# Get the directory and file listing
remote_files = sftp.listdir()

# Loop through each file in the directory
for file_name in remote_files:
    local_file = os.path.join(local_directory, file_name)

    # Get remote file modification time
    remote_file_info = sftp.stat(file_name)
    remote_mtime = remote_file_info.st_mtime

    if os.path.exists(local_file):
        # Get local file modification time
        local_mtime = os.path.getmtime(local_file)

        # If the local file is newer or the same, skip the download
        if local_mtime >= remote_mtime:
            print(f'Skipping download of {file_name}. The file is not newer or the same.')
            continue

    print(f'Trying to download {file_name} to {local_file}')

    # Download each file to the local directory
    try:
        sftp.get(file_name, local_file)
        print(f'Successfully downloaded {file_name} to {local_directory}')
    except FileNotFoundError:
        print(f'Failed to download {file_name}. The file does not exist.')

# Close the connection
sftp.close()
transport.close()