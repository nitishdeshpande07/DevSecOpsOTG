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


def find_paused_container():
    """Check if there is a paused container for OWASP Dependency Check."""
    try:
        result = subprocess.check_output(
            ['docker', 'ps', '-a', '--filter', 'status=paused', '--filter', 'ancestor=owasp/dependency-check', '--format', '{{.ID}}'],
            text=True
        ).strip()
        return result if result else None
    except subprocess.CalledProcessError:
        return None


def pause_container(container_id):
    """Pause the given container."""
    try:
        subprocess.check_call(['docker', 'pause', container_id])
    except subprocess.CalledProcessError as e:
        print(f"Error pausing container {container_id}: {e}")


def run_dependency_check(project_directory, report_directory, nvd_api_key):
    """Run OWASP Dependency Check Docker container for the project."""
    # Ensure the report directory exists
    if not os.path.exists(report_directory):
        os.makedirs(report_directory)

    print(f"Running OWASP Dependency Check on the project in {project_directory}...")

    paused_container = find_paused_container()
    if paused_container:
        print(f"Found paused container {paused_container}. Resuming and using it.")
        subprocess.check_call(['docker', 'unpause', paused_container])

        try:
            # Execute the scan inside the paused container
            subprocess.check_call([
                'docker', 'start', '-ai', paused_container
            ])
        finally:
            print(f"Pausing the container {paused_container} again.")
            pause_container(paused_container)
    else:
        print("No paused container found. Creating a new one.")

        try:
            # Create and run a new container, but don't remove it after use
            container_id = subprocess.check_output([
                'docker', 'create',
                '-v', f"{project_directory}:/src",
                '-v', f"{report_directory}:/report",
                'owasp/dependency-check',
                '--scan', '/src',
                '--format', 'ALL',
                '--out', '/report',
                '--project', 'NodeJS Project Dependency Check',
                '--nvdApiKey', nvd_api_key
            ], text=True).strip()

            print(f"Starting container {container_id}...")
            subprocess.check_call(['docker', 'start', '-ai', container_id])
            print(f"Pausing the container {container_id} for future use.")
            pause_container(container_id)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run OWASP Dependency Check. Error: {e}")
            return False

    print(f"Dependency check completed. Reports are stored in {report_directory}.")
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
