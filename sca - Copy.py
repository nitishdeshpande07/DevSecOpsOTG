## This module's script would be responsible for 2 fucntionality provisioing 
# 1. The OWASP Dependency Check Docker Image needs to be spined up and then further
# - This project directory and path is to be dynamically supplied to it so as to 
# Perform the Software Dependency Check. And then through a logical combination of the 
# following commands :  
# now we would be performing the entire scan and then compiling the 
# entire report and then storing it in the project's source directory as SCA Results/
# and also provide an on screen option to the user to choose to view the results or move
# to the further deployment stage. 
# Change 1 : Make sure that this clones the Github Repo and then supplies that directory
# as a path or something locally to the OWASP Dependency Check Container.

# {{{{{ python script_name.py /path/to/shared_repo repository_name }}}}

import os
import subprocess
import sys

def get_project_path(shared_repo_path, repo_name):
    """Construct the full path to the target project directory."""
    repo_path = os.path.join(shared_repo_path, repo_name)
    if not os.path.exists(repo_path):
        print(f"Error: The specified repository path does not exist: {repo_path}")
        sys.exit(1)
    return os.path.abspath(repo_path)

def run_dependency_check(project_directory, report_directory, nvd_api_key):
    """Run OWASP Dependency Check Docker container for the project."""
    
    # Ensure the report directory exists
    if not os.path.exists(report_directory):
        os.makedirs(report_directory)

    print(f"Running OWASP Dependency Check on the project in {project_directory}...")

    try:
        # Run the OWASP Dependency Check Docker container with the provided NVD API key
        subprocess.check_call([
            'docker', 'run', '--rm',
            '-v', f"{project_directory}:/src", 
            '-v', f"{report_directory}:/report",
            'owasp/dependency-check', 
            '--scan', '/src', 
            '--format', 'ALL', 
            '--out', '/report',
            '--project', 'NodeJS Project Dependency Check',
            '--nvdApiKey', nvd_api_key,  # Use the provided API key
           # '--cveValidForHours', '72'  # Use cache if valid for the last 72 hours
        ])
        print(f"Dependency check completed. Reports are stored in {report_directory}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run OWASP Dependency Check. Error: {e}")
        return False
    return True

def view_report(report_directory):
    """Provide an option to view the generated HTML report."""
    html_report_path = os.path.join(report_directory, 'dependency-check-report.html')
    
    if os.path.isfile(html_report_path):
        print(f"HTML Report found: {html_report_path}")
        view_choice = input("Do you want to view the Dependency Check report? (yes/no): ").lower()
        
        if view_choice == 'yes':
            if sys.platform == 'win32':
                os.startfile(html_report_path)  # For Windows
            elif sys.platform == 'darwin':
                subprocess.call(['open', html_report_path])  # For macOS
            else:
                subprocess.call(['xdg-open', html_report_path])  # For Linux
        else:
            print("Skipping report view.")
    else:
        print("HTML report not found.") 

def main():
    """Main function to run OWASP Dependency Check and provide user options."""
    
    # Ensure the correct number of arguments are provided
    if len(sys.argv) != 4:
        print("Usage: python script_name.py <shared_repo_path> <repo_name> <CENTRAL_RESULTS_DIR>")
        sys.exit(1)

    # Get command-line arguments for shared_repo_path, repo_name, and report directory
    shared_repo_path = sys.argv[1]
    repo_name = sys.argv[2]
    report_directory = os.path.abspath(sys.argv[3])
    
    # Get the full project path
    project_directory = get_project_path(shared_repo_path, repo_name)
    
    # Prompt for the NVD API key
    nvd_api_key = input("Please enter your NVD API key: ").strip()
    if not nvd_api_key:
        print("Error: NVD API key is required.")
        sys.exit(1)

    # Run the OWASP Dependency Check scan
    if not run_dependency_check(project_directory, report_directory, nvd_api_key):
        return

    # Provide the option to view the generated report
    view_report(report_directory)

    # Further step for deployment or additional actions
    next_step = input("Do you want to move to the SAST Stage? (yes/no): ").lower()
    if next_step == 'yes':
        print("Proceeding to the SAST Testing stage locally...")
        # Add deployment logic here
    else:
        print("Exiting the process.")

if __name__ == "__main__":
    main()



