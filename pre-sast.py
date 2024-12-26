# Creation of automated GitHub Public Repository / Fetch the Public Repository Details
# But as this is a Jenkins based CI/CD pipeline provisioning hence now it would be 
# a further step : NO LINK-UP YET.

# A Python based Module that would parse the current user's project directory make 
# and would make sure and identify that it's a Node based Application Project. 
# Indentify all the components that it has and then get's ready for further Implementation
# Also create the entire project's Docker Image Locally.
# Target Project Type : Node.js based Sample Application with an Allied DockerFile. 
# This module script should also be able to extract the exact full directory path
# allied to this actual project so as to supply it to various tool's docker images for 
# further operations and etc .. 
# As a response the tool should also be returning the final msg that " Project Setup Done .  Ready to Be Staged "

import os
import subprocess
import json

def is_node_project(directory):
    """Check if the directory is a Node.js project by looking for package.json."""
    package_json_path = os.path.join(directory, 'package.json')
    return os.path.isfile(package_json_path)

def get_project_name(directory):
    """Extract the project name from the package.json file."""
    package_json_path = os.path.join(directory, 'package.json')
    try:
        with open(package_json_path, 'r') as f:
            package_json = json.load(f)
        return package_json.get('name', 'node-app')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading package.json: {e}")
        return 'node-app'

def get_project_path():
    """Get the full path of the current project directory."""
    return os.path.abspath(os.getcwd())

def docker_image_exists(image_name):
    """Check if a Docker image with the given name already exists locally."""
    try:
        output = subprocess.check_output(['docker', 'images', '-q', image_name]).strip()
        return len(output) > 0  # If output is non-empty, the image exists
    except subprocess.CalledProcessError as e:
        print(f"Error checking for Docker image: {e}")
        return False

def build_docker_image(directory, image_name):
    """Build the Docker image for the Node.js project."""
    print(f"Building Docker image '{image_name}' for the project in {directory}...")
    try:
        subprocess.check_call(['docker', 'build', '-t', image_name, directory])
        print(f"Docker image '{image_name}' built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Docker image '{image_name}'. Error: {e}")
        return False
    return True

def main():
    """Main function to orchestrate the project setup."""
    project_directory = get_project_path()
    
    # Step 1: Check if it's a Node.js project
    if not is_node_project(project_directory):
        print("This directory is not a Node.js project. Please ensure a valid project with package.json exists.")
        return

    # Step 2: Get the project name from package.json
    project_name = get_project_name(project_directory)

    # Step 3: Check if the Docker image already exists
    if docker_image_exists(project_name):
        print(f"Docker image '{project_name}' already exists. Skipping build process.")
    else:
        # Step 4: Build Docker image with the project name
        if not build_docker_image(project_directory, project_name):
            return
    
    # Final message
    print(f"Project setup done. Docker image '{project_name}' is ready to be staged.")

if __name__ == "__main__":
    main()