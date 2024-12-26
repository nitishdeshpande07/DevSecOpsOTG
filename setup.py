# This is the module that would be initally responsible for the following activities 
# And hence we have to implment the following functionalities as objectives :
# Pre-Requisites : Docker and Node should be pre-installed. 
# 1. Installing the following needed dependencies locally on the machine that it will
# be deployed. 

# - Creation of automated GitHub Public Repository / Fetch the Public Repository Details Script
# - OWASP IDE Vuln-Scanner (Download + Setup)
# - Semgrep OSS (Download + Setup)
# - Jenkins Docker Image (Download + Setup)
# - Creation of the Project's Docker Image (Docker Image Creation)
# - ZAP Docker Image local (Download + Setup)

# 2. A Python based Module that would parse the current user's project directory and would 
# - Indentify all the components that it has and then get's ready for further Implementation

# Target Project Type : Node.js based Sample Application with an Allied DockerFile

import os
import platform
import subprocess
import sys

# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")
    else:
        print(f"Directory {directory} already exists.")

# Function to check if a Docker image exists locally
def check_docker_image_exists(image_name):
    try:
        output = subprocess.check_output(['docker', 'images', '-q', image_name])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False 

# Function to pull Docker images
def pull_docker_image(image_name):
    if check_docker_image_exists(image_name):
        print(f"Docker image {image_name} already exists. Skipping pull.")
    else:
        try:
            print(f"Pulling Docker image {image_name}...")
            subprocess.check_call(['docker', 'pull', image_name])
            print(f"Docker image {image_name} pulled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to pull Docker image {image_name}. Error: {e}")

# Function to setup Jenkins Docker container
def setup_jenkins_container():
    pull_docker_image('jenkins/jenkins:lts')

# Function to pull ZAP Docker image
def pull_zap_docker_image():
    pull_docker_image('zaproxy/zap-stable')

# Function to pull OWASP Dependency Check Docker image
def pull_owasp_dependency_check():
    pull_docker_image('owasp/dependency-check')

# Function to pull Semgrep Docker image
def pull_semgrep_docker_image():
    pull_docker_image('returntocorp/semgrep')

# Function to check if Docker is running
def check_docker_status():
    try:
        # Check if Docker is running
        subprocess.check_call(['docker', 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Docker is running.")
    except subprocess.CalledProcessError:
        print("Docker is not running. Please start Docker and try again.")
        sys.exit(1)

# Main function to orchestrate the setup
def main():
    # Step 1: Create the dependencies folder
    dependencies_dir = "dependencies"
    create_directory(dependencies_dir)

    # Step 2: Check the platform (Windows or Linux) and manage Docker accordingly
    current_platform = platform.system()
    
    if current_platform == "Linux":
        # Linux requires manually starting Docker daemon
        check_docker_status()  # Ensure Docker is running, if not, exit
    elif current_platform == "Windows":
        # On Windows, Docker Desktop must be running; check Docker status
        print("Checking if Docker Desktop is running on Windows...")
        check_docker_status()
    else:
        print(f"Unsupported platform: {current_platform}")
        sys.exit(1)

    # Step 3: Pull OWASP Dependency Check Docker image
    pull_owasp_dependency_check()

    # Step 4: Pull Semgrep Docker image
    pull_semgrep_docker_image()

    # Step 5: Setup Jenkins Docker container
    setup_jenkins_container()

    # Step 6: Pull ZAP Docker image
    pull_zap_docker_image()

if __name__ == "__main__":
    main() 