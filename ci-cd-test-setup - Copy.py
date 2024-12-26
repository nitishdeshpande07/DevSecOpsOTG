## Fully working and Creates the Poll SCM based Jobs on the Jenkins server
## Change 1 : Fully working CI/CD Setup Successfully and the jenkins config SUCCESS
## Change 2 : Now we have to add the the SecOps functionality locally for testing.
## Change 3 : Add the call to the external python module names sca.py from here post
import docker
from requests.auth import HTTPBasicAuth
import requests
import subprocess
import os 
import sys 
import time
import git
from github import Github

# User inputs
GITHUB_USERNAME = input("Enter your GitHub username: ").strip()
GITHUB_REPO = input("Enter the target GitHub repository (format: repo): ").strip()
GITHUB_REPO_URL=input("Repo URL:")

# GitHub Personal Access Token (PAT)
GITHUB_PAT = input("Enter the GITHUB PAT: ")

# Jenkins Configuration
JENKINS_PORT = 8080
ADMIN_USERNAME = "admin"
JENKINS_URL = f"http://localhost:{JENKINS_PORT}/jenkins"
SHARED_REPO_PATH = "/shared_repo"  # Directly use the Jenkins container's shared repository path
shared_volume_dir = input("Enter the local directory path for the shared volume for latest repo copies: ")
CENTRAL_RESULTS_DIR=input("Enter the local directory path for storing all the Central Security Scan Results : ")
# Docker Client
client = docker.from_env()

# Deployment Script based variables
#docker_build_cmd=input("Custom Docker Build Command with flags for target project")
#docker_run_cmd=input("Custom Docker Run command with flags for target project")
#target_dast_port=input("Target Port to run the project locally on:")
 
def is_docker_container_running(container_name):
    """Check if a Docker container is running."""
    try:
        container = client.containers.get(container_name)
        return container.status == "running"
    except docker.errors.NotFound:
        print(f"Container {container_name} not found.")
    except Exception as e:
        print(f"Error checking container status: {e}")
    return False

def get_jenkins_admin_password_from_file():
    """Retrieve Jenkins initial admin password from the container."""
    print("Retrieving Jenkins initial admin password from the file...")
    if not is_docker_container_running("jenkins_server"):
        print("Jenkins server container is not running. Start the container and try again.")
        return None
    try:
        container = client.containers.get("jenkins_server")
        password_file_path = "/var/jenkins_home/secrets/initialAdminPassword"
        result = container.exec_run(f"cat {password_file_path}")
        password = result.output.decode("utf-8").strip()
        print("Retrieved Jenkins admin password.")
        return password
    except Exception as e:
        print(f"Error retrieving the Jenkins admin password: {e}")
        return None

def get_jenkins_crumb(session, jenkins_url):
    """Retrieve Jenkins crumb for CSRF protection."""
    print("Retrieving Jenkins crumb for CSRF protection...")
    try:
        response = session.get(f"{jenkins_url}/crumbIssuer/api/json")
        if response.status_code == 200:
            crumb_data = response.json()
            print("Crumb retrieved successfully.")
            return {crumb_data['crumbRequestField']: crumb_data['crumb']}
        else:
            print(f"Failed to retrieve crumb: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error retrieving crumb: {e}")
    return None

#def create_jenkins_job(session, jenkins_url, admin_password, SHARED_REPO_PATH):
    """Create or update Jenkins job with Poll SCM configuration and wait for new commit content locally."""
    job_name = "GitHub_PollSCM_Integration"
    GITHUB_REPO_URL = f"https://{GITHUB_PAT}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"

    job_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
    <project>
        <actions/>
        <description>CI/CD Pipeline for GitHub Integration using Poll SCM</description>
        <scm class="hudson.plugins.git.GitSCM" plugin="git@latest">
            <configVersion>2</configVersion>
            <userRemoteConfigs>
                <hudson.plugins.git.UserRemoteConfig>
                    <url>{GITHUB_REPO_URL}</url>
                </hudson.plugins.git.UserRemoteConfig>
            </userRemoteConfigs>
            <branches>
                <hudson.plugins.git.BranchSpec>
                    <name>*/main</name>
                </hudson.plugins.git.BranchSpec>
            </branches>
            <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
            <submoduleCfg class="list"/>
            <extensions/>
        </scm>
        <triggers>
            <hudson.triggers.SCMTrigger>
                <spec>H/5 * * * *</spec> <!-- Poll SCM every 5 minutes -->
            </hudson.triggers.SCMTrigger>
        </triggers>
        <builders>
            <hudson.tasks.Shell>
                <command>
                echo "Triggering SecOps pipeline..."
                python /scripts/master_script.py {GITHUB_REPO_URL} {SHARED_REPO_PATH}
                echo "SecOps pipeline executed. Proceeding to SecOps Stage locally."
                </command>
            </hudson.tasks.Shell>
        </builders>
        <publishers/>
        <buildWrappers/>
    </project>"""

    headers = get_jenkins_crumb(session, jenkins_url)
    if not headers:
        print("Failed to retrieve crumb. Cannot create job.")
        return

    headers["Content-Type"] = "application/xml"

    try:
        create_job_url = f"{jenkins_url}/createItem?name={job_name}"
        response = session.post(
            create_job_url,
            auth=HTTPBasicAuth(ADMIN_USERNAME, admin_password),
            headers=headers,
            data=job_config_xml,
        )
        if response.status_code == 200:
            print("Jenkins job created successfully.")
        elif response.status_code == 400 and "already exists" in response.text:
            print("Jenkins job already exists. Updating...")
            update_job(session, jenkins_url, job_name, job_config_xml, headers, admin_password)
        else:
            print(f"Failed to create job: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating Jenkins job: {e}")
        return

    # Wait for SCM-triggered build
    # Monitor SHARED_REPO_PATH for new commit content
    print(f"Monitoring {shared_volume_dir} for new content...")
    initial_files = set(os.listdir(shared_volume_dir))
    while True:
        current_files = set(os.listdir(shared_volume_dir))
        if current_files != initial_files:
            print("New commit content detected in shared_volume_dir. Proceeding...")
            break
        time.sleep(60)  # Check for changes every 60 seconds

    # Proceed with further execution
    print("Executing remaining pipeline steps...")

def create_jenkins_job(session, jenkins_url, admin_password, SHARED_REPO_PATH):
    """Create or update Jenkins job with Poll SCM configuration and wait for new commit content locally."""
    job_name = "GitHub_PollSCM_Integration"
    GITHUB_REPO_URL = f"https://{GITHUB_PAT}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"

    job_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
    <project>
        <actions/>
        <description>CI/CD Pipeline for GitHub Integration using Poll SCM</description>
        <scm class="hudson.plugins.git.GitSCM" plugin="git@latest">
            <configVersion>2</configVersion>
            <userRemoteConfigs>
                <hudson.plugins.git.UserRemoteConfig>
                    <url>{GITHUB_REPO_URL}</url>
                </hudson.plugins.git.UserRemoteConfig>
            </userRemoteConfigs>
            <branches>
                <hudson.plugins.git.BranchSpec>
                    <name>*/main</name>
                </hudson.plugins.git.BranchSpec>
            </branches>
            <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
            <submoduleCfg class="list"/>
            <extensions/>
        </scm>
        <triggers>
            <hudson.triggers.SCMTrigger>
                <spec>H/5 * * * *</spec> <!-- Poll SCM every 5 minutes -->
            </hudson.triggers.SCMTrigger>
        </triggers>
        <builders>
            <hudson.tasks.Shell>
                <command>
                echo "Triggering SecOps pipeline..."
                # Use ShiningPanda to run the Python script
                python /scripts/master_script.py {GITHUB_REPO_URL} {SHARED_REPO_PATH}
                echo "SecOps pipeline executed. Proceeding to SecOps Stage locally."
                </command>
            </hudson.tasks.Shell>
        </builders>
        <publishers/>
        <buildWrappers>
            <!-- Wrapper for ShiningPanda Python environment -->
            <hudson.plugins.shiningpanda.python.PythonBuildWrapper>
                <pythonHome>/var/jenkins_home/plugins/shiningpanda</pythonHome> <!-- Specify the Python version from ShiningPanda -->
                <pythonName>Python 3</pythonName> <!-- Specify the environment name if needed -->
            </hudson.plugins.shiningpanda.python.PythonBuildWrapper>
        </buildWrappers>
    </project>"""

    headers = get_jenkins_crumb(session, jenkins_url)
    if not headers:
        print("Failed to retrieve crumb. Cannot create job.")
        return

    headers["Content-Type"] = "application/xml"

    try:
        create_job_url = f"{jenkins_url}/createItem?name={job_name}"
        response = session.post(
            create_job_url,
            auth=HTTPBasicAuth(ADMIN_USERNAME, admin_password),
            headers=headers,
            data=job_config_xml,
        )
        if response.status_code == 200:
            print("Jenkins job created successfully.")
        elif response.status_code == 400 and "already exists" in response.text:
            print("Jenkins job already exists. Updating...")
            update_job(session, jenkins_url, job_name, job_config_xml, headers, admin_password)
        else:
            print(f"Failed to create job: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating Jenkins job: {e}")
        return

    # Wait for SCM-triggered build
    # Monitor SHARED_REPO_PATH for new commit content
    print(f"Monitoring {shared_volume_dir} for new content...")
    initial_files = set(os.listdir(shared_volume_dir))
    while True:
        current_files = set(os.listdir(shared_volume_dir))
        if current_files != initial_files:
            print("New commit content detected in shared_volume_dir. Proceeding...")
            break
        time.sleep(60)  # Check for changes every 60 seconds

    # Proceed with further execution
    print("Executing remaining pipeline steps...")


def update_job(session, jenkins_url, job_name, job_config_xml, headers, admin_password):
    """Update existing Jenkins job."""
    try:
        update_job_url = f"{jenkins_url}/job/{job_name}/config.xml"
        response = session.post(
            update_job_url,
            auth=HTTPBasicAuth(ADMIN_USERNAME, admin_password),
            headers=headers,
            data=job_config_xml,
        )
        if response.status_code == 200:
            print("Jenkins job updated successfully.")
        else:
            print(f"Failed to update job: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error updating Jenkins job: {e}")

## SCA Script 
def run_additional_script(shared_volume_dir, github_repo ,CENTRAL_RESULTS_DIR):
    """Run the sca.py Python script located in the same directory with provided arguments."""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'sca.py')
        # Run sca.py with shared_volume_dir and github_repo as command-line arguments
        subprocess.run(['python', script_path, shared_volume_dir, github_repo, CENTRAL_RESULTS_DIR], check=True)
        print("Software Composition Analysis Completed.")
    except Exception as e:
        print(f"Error running the SCA script: {e}")

## SAST Script Trigger
def run_sast_script(shared_volume_dir, GITHUB_REPO , CENTRAL_RESULT_DIR):
    """
    Run the sast.py Python script located in the same directory with the provided arguments.
    
    Args:
        shared_volume_dir (str): The shared volume directory path.
        GITHUB_REPO (str): The name of the repository to scan.
    """
    try:
        # Construct the full path to sast.py
        script_path = os.path.join(os.path.dirname(__file__), 'sast.py')

        # Construct the target repository path
        target_repo_path = os.path.join(shared_volume_dir, GITHUB_REPO)

        # Verify if the target repository path exists
        if not os.path.exists(target_repo_path):
            raise FileNotFoundError(f"Target repository path does not exist: {target_repo_path}")

        # Run the sast.py script with the target repository path
        subprocess.run(['python', script_path, target_repo_path, CENTRAL_RESULT_DIR], check=True)

        print(f"Static Application Security Testing (SAST) completed successfully on {target_repo_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running the SAST script: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

## Pre-DAST Local Target Staging Project Deploy Locally
def run_deployment_script(shared_volume_dir, GITHUB_REPO):
    """
    Run the target-repo-deploy-auto.py script and return the list of converted deployment URLs.

    Args:
        shared_volume_dir (str): The shared volume directory path.
        GITHUB_REPO (str): The repository to deploy.

    Returns:
        list: A list of converted URLs from the deployment output.
    """
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'target-repo-deploy-auto.py')
        target_repo_path = os.path.join(shared_volume_dir, GITHUB_REPO)

        # Check if paths exist
        if not os.path.exists(target_repo_path):
            raise FileNotFoundError(f"Target repository path does not exist: {target_repo_path}")
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Deployment script not found: {script_path}")

        # Run the deployment script
        result = subprocess.run(
            ['python', script_path, '--project_path', target_repo_path],
            text=True,
            capture_output=True,
            check=True
        )
        print(result.stdout)

        # Extract and process URLs
        url_list = []
        if "Access your application at:" in result.stdout:
            urls_section = result.stdout.split("Access your application at:")[-1].strip()
            raw_urls = [
                line.strip("- ").strip() for line in urls_section.splitlines()
                if line.startswith("http://localhost") or "http://localhost" in line
            ]

            # Convert localhost URLs to the required format
            for url in raw_urls:
                if "http://localhost" in url:
                    try:
                        port = url.split(":")[-1].strip("/").split("/")[-1]
                        converted_url = f"http://host.docker.internal:{port}/"
                        url_list.append(converted_url)
                    except IndexError:
                        print(f"Invalid URL format: {url}")

            print(f"Captured and converted URLs: {url_list}")
        else:
            print("No URLs found in the deployment output.")

        return url_list

    except subprocess.CalledProcessError as e:
        print(f"Error while running deployment script: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


## All the DAST steps and results etc.
## Now an option to the user to continue to production deployment/commit or exit and return to remediate !

# DAST Scan

def trigger_dast_test(CENTRAL_RESULTS_DIR, url_list):
    """
    Trigger the dast-test.py script with the supplied URLs.

    Args:
        CENTRAL_RESULTS_DIR (str): Directory to store DAST results.
        url_list (list): List of converted URLs.
    """
    try:
        if not url_list:
            raise ValueError("No valid URLs found to trigger DAST testing.")

        for idx, url in enumerate(url_list):
            # Run the ZAP scan for each URL individually
            scan_dir = os.path.join(CENTRAL_RESULTS_DIR, f"zap_scan_{idx + 1}")
            os.makedirs(scan_dir, exist_ok=True)

            command = [
                "docker", "run", "--rm",
                "-v", f"{scan_dir}:/zap/wrk",
                "zaproxy/zap-stable", "zap-full-scan.py",
                "-t", url,
                "-r", f"/zap/wrk/zap_report_{idx + 1}.html",
                "-x", f"/zap/wrk/zap_report_{idx + 1}.xml"
            ]
            
            print(f"Running ZAP scan for URL {idx + 1}: {url}")
            try:
                subprocess.check_call(command)
                print(f"DAST scan completed successfully for URL {url}")
            except subprocess.CalledProcessError as e:
                print(f"Error running ZAP scan for {url}: {e}")

        print("All DAST scans completed.")

    except ValueError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


## if the user says return to remediate EXIT the program and tool. 
## if the user says continue commit to production/deployment.

## Function to take up this local latest commit and then commit that to the production branch of that repo.
def push_and_merge_to_production(shared_volume_dir, GITHUB_PAT, GITHUB_REPO_URL):
    """
    Push the contents of a target project directory to a GitHub repository,
    create a pull request to the "Production" branch, and merge it.

    Args:
        shared_volume_dir (str): The local directory containing the project to push.
        GITHUB_PAT (str): GitHub Personal Access Token with necessary repo permissions.
        GITHUB_REPO_URL (str): The full URL of the target GitHub repository (HTTPS format).

    Raises:
        Exception: If the repository or branch cannot be accessed or updated.
    """
    try:
        # Extract the repo name from the URL
        repo_name = GITHUB_REPO_URL.split('/')[-2] + '/' + GITHUB_REPO_URL.split('/')[-1].replace('.git', '')

        # Authenticate using PyGithub
        g = Github(GITHUB_PAT)
        repo = g.get_repo(repo_name)
        print(f"Connected to GitHub repository: {repo_name}")

        # Check if "Production" branch exists
        branches = [branch.name for branch in repo.get_branches()]
        if "Production" not in branches:
            print("Production branch does not exist. Creating it...")
            # Create the branch from the default branch
            default_branch = repo.default_branch
            default_ref = repo.get_git_ref(f"heads/{default_branch}")
            repo.create_git_ref(ref="refs/heads/Production", sha=default_ref.object.sha)
            print("Production branch created successfully.")
        else:
            print("Production branch already exists.")

        # Check if the directory is a Git repository
        if not os.path.exists(os.path.join(shared_volume_dir, ".git")):
            print(f"Initializing a new Git repository in {shared_volume_dir}...")
            local_repo = git.Repo.init(shared_volume_dir)
            print("Setting up remote repository...")
            local_repo.create_remote("origin", GITHUB_REPO_URL)
        else:
            # Initialize GitPython repo
            print("Using existing local repository.")
            local_repo = git.Repo(shared_volume_dir)

        # Ensure the local repo has the correct remote URL
        print("Configuring remote repository...")
        remote_url = local_repo.git.remote("get-url", "origin")
        if remote_url != GITHUB_REPO_URL:
            print("Updating remote URL to match target repository...")
            local_repo.git.remote("set-url", "origin", GITHUB_REPO_URL)

        # Fetch all branches to ensure "Production" exists locally
        print("Fetching remote branches...")
        local_repo.git.fetch()

        # Check out a new feature branch
        feature_branch = "update-feature"
        print(f"Creating and checking out feature branch '{feature_branch}'...")
        local_repo.git.checkout("-b", feature_branch)

        # Add, commit, and push changes
        print("Adding and committing changes...")
        local_repo.git.add(all=True)
        local_repo.index.commit(f"Update project files in branch '{feature_branch}'")

        print(f"Pushing feature branch '{feature_branch}' to remote...")
        local_repo.git.push("--set-upstream", "origin", feature_branch)

        # Create a pull request
        print(f"Creating a pull request from '{feature_branch}' to 'Production'...")
        pr = repo.create_pull(
            title=f"Merge updates from {feature_branch} into Production",
            body="Auto-generated pull request to merge feature updates.",
            head=feature_branch,
            base="Production",
        )
        print(f"Pull request created: {pr.html_url}")

        # Merge the pull request
        print("Merging the pull request...")
        pr.merge(merge_method="merge")
        print("Pull request merged successfully into 'Production' branch.")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def main():
    # Retrieve Jenkins admin password
    admin_password = get_jenkins_admin_password_from_file()
    if not admin_password:
        print("Could not retrieve Jenkins admin password.")
        return

    session = requests.Session()
    session.auth = HTTPBasicAuth(ADMIN_USERNAME, admin_password)
    
    # Create Jenkins job
    print("Creating Jenkins Job....")
    create_jenkins_job(session, JENKINS_URL, admin_password, SHARED_REPO_PATH)

    # Run additional scripts after Jenkins job creation
    print("Running SCA testing...")
    run_additional_script(shared_volume_dir, GITHUB_REPO, CENTRAL_RESULTS_DIR)

    print("Running SAST testing...")
    run_sast_script(shared_volume_dir, GITHUB_REPO, CENTRAL_RESULTS_DIR)

    ## Multiple Function calls left to trigerred and written 
    # Call the function to run the deployment script

    print("Running Local Deployment...")
    url_list = run_deployment_script(shared_volume_dir,GITHUB_REPO)

    ## Call the DAST-Test script 

    print("Running DAST testing...")
    trigger_dast_test(CENTRAL_RESULTS_DIR,url_list)

    ## Call the production commit script : 

    print("Commiting to the Production Branch...")
    push_and_merge_to_production(shared_volume_dir, GITHUB_PAT, GITHUB_REPO_URL)

    print("An DevSecOps powered CI-CD Cycle Ends.") 

if __name__ == "__main__":
    main()  # Calling the main function to execute when the script is run directly



