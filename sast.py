## From here the locally cloned latest project commit would be undergoing the SAST by
## tigerring the Docker Image of the Semgrep-OSS for Static AS Testing.
## python run_semgrep_sast.py <path_to_project_repo>
import os
import subprocess
import sys

def ensure_docker_image(image_name):
    """Check if the specified Docker image is available locally. Pull it if not."""
    try:
        print(f"Checking for the Docker image: {image_name}...")
        result = subprocess.run(['docker', 'images', '-q', image_name], stdout=subprocess.PIPE, text=True)
        if not result.stdout.strip():
            print(f"Docker image {image_name} not found. Pulling it...")
            subprocess.check_call(['docker', 'pull', image_name])
        else:
            print(f"Docker image {image_name} is already available.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to ensure Docker image. Error: {e}")
        sys.exit(1)

def get_project_path(project_path):
    """Validate the project path."""
    if not os.path.exists(project_path):
        print(f"Error: The specified project path does not exist: {project_path}")
        sys.exit(1)
    return os.path.abspath(project_path)

def get_report_directory(report_directory):
    """Validate or create the report directory."""
    if not os.path.exists(report_directory):
        os.makedirs(report_directory)
    return os.path.abspath(report_directory)

def run_semgrep_scan(project_directory, report_directory):
    """Run the Semgrep Docker container for SAST scans."""
    print(f"Running Semgrep SAST scans on the project in {project_directory}...")

    try:
        # Define the JSON output file path
        json_output_file = os.path.join(report_directory, 'semgrep-sast-results.json')

        # Run the Semgrep Docker container
        subprocess.check_call([
            'docker', 'run', '--rm',
            '-v', f"{project_directory}:/src",
            '-v', f"{report_directory}:/output",
            'returntocorp/semgrep',
            'semgrep',
            '--config=auto',                 # Use auto-detection for configurations
            '--json',                        # Generate results in JSON format
            '--no-git-ignore',               # Ignore .gitignore rules to include all files
            '--verbose',                     # Enable verbose output for debugging
            '--error',                       # Treat findings as errors
            '-o', '/output/semgrep-sast-results.json'  # JSON output file
        ])

        # Print results summary
        print(f"SAST scan completed successfully.")
        print(f"Results (JSON): {json_output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Failed to run Semgrep. Error: {e}")
        sys.exit(1)

def main():
    """Main function to run Semgrep SAST scans."""
    if len(sys.argv) != 3:
        print("Usage: python sast.py <project_repo_path> <results_directory>")
        sys.exit(1)

    # Get the project repository path and results directory from command-line arguments
    project_path = get_project_path(sys.argv[1])
    report_directory = get_report_directory(sys.argv[2])

    # Confirm Semgrep Docker image is available
    semgrep_image = 'returntocorp/semgrep'
    ensure_docker_image(semgrep_image)

    # Run the Semgrep SAST scan
    run_semgrep_scan(project_path, report_directory)

    # Inform the user about next steps
    print("SAST scan completed successfully. You can now review the results.")

if __name__ == "__main__":
    main()

