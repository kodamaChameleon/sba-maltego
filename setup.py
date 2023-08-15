import subprocess
from modules import ckan_api

# Install required python dependencies
def install_requirements():
    subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])

# Build config file for easy importation
def build_config():
    subprocess.check_call(['python3', 'project.py', 'list'])

# Dowload packages from SBA
def download_packages():

    supported_packages = [
        "ppp-foia"
    ]

    for package in supported_packages:
        data = ckan_api.dataset(package)
        data.fetch_csv()

if __name__ == '__main__':
    install_requirements()
    download_packages()
    build_config()