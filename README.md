
# Code Description
The main function in this script connects to an FTP server using the paramiko library and downloads a list of files from a remote directory. It first sets up logging and loads environment variables from a .env file. It then retrieves the FTP server details from the environment variables and checks if they are provided.

The script defines the list of files to download, the remote directory to download files from, and the local directory to save the downloaded files. It creates the local directory if it doesn't exist.

The script creates a transport object and connects to the FTP server using the provided hostname, username, and password. It then creates an SFTP client from the transport object and changes the current directory to the remote directory.

The script enters a loop that runs 30 times with a 2-minute delay between each iteration. In each iteration, it retrieves the directory and file listing from the remote directory. It loops through each file in the directory and checks if it is in the list of files to download. If it is, the script constructs the local file path, retrieves the remote file's modification time, and compares it with the local file's modification time. If the local file is newer or the same, the script skips the download. Otherwise, it attempts to download the file using the SFTP client's get() method and removes the file from the list of files to download. If the file does not exist on the remote server, the script prints an error message.

After each iteration, the script checks if all files have been downloaded. If they have, it breaks out of the loop. Otherwise, it delays for 2 minutes before the next iteration.

Finally, the script closes the SFTP client and transport connection.

# Contribute 
Before you can contribute to this code, you need to clone this repository and set up your local environment.

## Setting up a Virtual Environment
A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated Python virtual environments for them. Here's how to set it up:

Install the virtualenv package:
pip install virtualenv
Navigate to your project directory and create a virtual environment. We'll name it .venv:
cd your-project-directory
virtualenv .venv
Activate the virtual environment:
On Windows, run:
.venv\Scripts\activate
On Unix or MacOS, run:
source .venv/bin/activate

## Importing the requirements.txt file
After setting up and activating the virtual environment, you can install the required packages using the requirements.txt file:

pip install -r requirements.txt

## Setting up the .env file
This script uses environment variables to securely store the FTP server details. These are stored in a .env file in the root directory of the project. Here's an example of what it should look like:

FTP_HOSTNAME=your_hostname
FTP_USERNAME=your_username
FTP_PASSWORD=your_password
Replace your_hostname, your_username, and your_password with your actual FTP server details.

