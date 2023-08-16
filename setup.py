import subprocess
from modules import ckan
import json

# Install required python dependencies
def install_requirements():
    subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])

# Build config file for easy importation
def build_config():
    subprocess.check_call(['python3', 'project.py', 'list'])

# Dowload packages from SBA
def download_packages():

    with open("data/supported_packages.json", 'r') as f:
        supported_packages = json.load(f)

    for package in supported_packages:
        data = ckan.dataset(package)
        data.fetch_csv()

if __name__ == '__main__':
    install_requirements()
    download_packages()
    build_config()