## Basically this script would be called from the CI-CD test main core script
## and then woudld ask for the path of the local dockerfile or docker-compose.yaml
## and then the target port and then any addtional deployment things into it like network
## This would then deploy that target project container locally and also verify if 
## that is running and is accesible locally 
## It would be trigerred with the target project path and the also add the port-number
## needed to be published and hence avoid conflicts
## hence execute in step-by-step manner like initially docker compose up and then ask for 
## special docker run command which is project specific that with all the flags and etc
## hence initially docker compose up 
## then the custom docker run command with all the needed flags to be triggered and
## then published to the target port
## hence this would basically serve as a customizable template for target-project's automation
import os
import subprocess
import argparse
import sys
import yaml

def ensure_pyyaml_installed():
    """
    Ensures that the pyyaml module is installed. Installs it if missing.
    """
    try:
        import yaml
    except ImportError:
        print("PyYAML is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        print("PyYAML installed successfully.")
        import yaml  # Import after installation to confirm success

def execute_command(command):
    """
    Executes a shell command and returns the output or error.
    """
    try:
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, check=True
        )
        print(f"Output:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error:\n{e.stderr}")
        return None

# def deploy_docker_compose(project_path):
    """
    Deploys the application using docker-compose.yaml from the specified project path.
    """
    compose_file = os.path.join(project_path, "docker-compose.yml")
    if os.path.exists(compose_file):
        print("Found docker-compose.yaml. Running docker-compose up...")
        execute_command(f"docker-compose -f {compose_file} up -d")
        return True
    else:
        raise FileNotFoundError("No docker-compose.yaml found in the target project path.")

def deploy_docker_compose_or_file(project_path):
    """
    Deploys the application using docker-compose.yaml or Dockerfile from the specified project path.
    """
    compose_file = os.path.join(project_path, "docker-compose.yml")
    dockerfile = os.path.join(project_path, "Dockerfile")

    if os.path.exists(compose_file):
        print("Found docker-compose.yaml. Running docker-compose up...")
        execute_command(f"docker-compose -f {compose_file} up -d")
        return True
    elif os.path.exists(dockerfile):
        print("docker-compose.yaml not found. Found Dockerfile. Building and running Docker container...")
        execute_command(f"docker build -t my-app {project_path}")
        execute_command("docker run -d my-app")
        return True
    else:
        raise FileNotFoundError("Neither docker-compose.yaml nor Dockerfile found in the target project path.")

 # def get_service_urls(project_path):
    """
    Parses the docker-compose.yaml file to extract all service URLs.
    """
    import yaml

    compose_file = os.path.join(project_path, "docker-compose.yml")
    if not os.path.exists(compose_file):
        raise FileNotFoundError("No docker-compose.yaml found in the target project path.")

    with open(compose_file, "r") as file:
        compose_data = yaml.safe_load(file)

    service_urls = []
    for service_name, service_data in compose_data.get("services", {}).items():
        ports = service_data.get("ports", [])
        for port in ports:
            # Extract host port (format: "host:container" or "host:container/protocol")
            host_port = port.split(":")[0]
            service_urls.append(f"http://localhost:{host_port}")

    return service_urls

def deploy_docker_compose_or_file(project_path):
    """
    Deploys the application using docker-compose.yaml or Dockerfile from the specified project path.
    Parses service URLs from the respective file.
    """
    compose_file = os.path.join(project_path, "docker-compose.yml")
    dockerfile = os.path.join(project_path, "Dockerfile")

    service_urls = []

    def parse_docker_compose_services(compose_file):
        """
        Parses the docker-compose.yml file and extracts all service URLs.
        """
        with open(compose_file, 'r') as file:
            compose_data = yaml.safe_load(file)

        services = compose_data.get('services', {})
        for service, details in services.items():
            ports = details.get('ports', [])
            for port in ports:
                if isinstance(port, str):
                    host_port = port.split(":")[0]
                    service_urls.append(f"http://localhost:{host_port}")
                elif isinstance(port, int):
                    service_urls.append(f"http://localhost:{port}")

    def parse_dockerfile_services(dockerfile):
        """
        Parses the Dockerfile to infer exposed ports and constructs service URLs.
        """
        with open(dockerfile, 'r') as file:
            for line in file:
                if line.strip().startswith("EXPOSE"):
                    ports = line.strip().split()[1:]
                    for port in ports:
                        service_urls.append(f"http://localhost:{port}")

    if os.path.exists(compose_file):
        print("Found docker-compose.yaml. Running docker-compose up...")
        execute_command(f"docker-compose -f {compose_file} up -d")
        parse_docker_compose_services(compose_file)
    elif os.path.exists(dockerfile):
        print("docker-compose.yaml not found. Found Dockerfile. Building and running Docker container...")
        execute_command(f"docker build -t my-app {project_path}")
        execute_command("docker run -d my-app")
        parse_dockerfile_services(dockerfile)
    else:
        raise FileNotFoundError("Neither docker-compose.yaml nor Dockerfile found in the target project path.")

    return service_urls



def main():
    ensure_pyyaml_installed()

    parser = argparse.ArgumentParser(description="Automate Docker container deployment.")
    parser.add_argument(
        "--project_path",
        type=str,
        required=True,
        help="Path to the target project containing docker-compose.yaml.",
    )
    args = parser.parse_args()

    print("Starting Docker Deployment Automation...")
    project_path = args.project_path

    # Change directory to the project path
    os.chdir(project_path)

    # Deploy Docker Compose
    try:
        #deploy_docker_compose(project_path)

        deploy_docker_compose_or_file(project_path)

        #service_urls = get_service_urls(project_path)

        service_urls = deploy_docker_compose_or_file(project_path)
        print("Deployment successful! Access your application at:")
        for url in service_urls:
            print(f"- {url}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
