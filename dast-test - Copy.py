
## Spin up the ZAP Docker Image run all the possible attacks on the target
## Providing 3 Scan Options : Full Scan + API Scan + Baseline Scan

## Only simple DAST testing and results storage locally running the container.
## this script will be provided with the target URL and the result storage dir as arguments
# python dast_scan.py /path/to/central_results "['http://example1.com', 'http://example2.com', 'http://example3.com']"

import os
import subprocess
import sys

# Function to check Docker status
def check_docker_status():
    try:
        subprocess.check_call(['docker', 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Docker is running.")
    except subprocess.CalledProcessError:
        print("Docker is not running. Please start Docker and try again.")
        sys.exit(1)

# Function to pull ZAP Docker image
def pull_zap_image():
    image_name = 'zaproxy/zap-stable'
    try:
        print(f"Pulling ZAP Docker image {image_name}...")
        subprocess.check_call(['docker', 'pull', image_name])
        print(f"ZAP Docker image {image_name} pulled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull ZAP Docker image. Error: {e}")
        sys.exit(1)

# Function to create a directory
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")
    else:
        print(f"Directory {directory} already exists.")

# Function to run ZAP scan
def run_zap_scan(target_url, report_directory):
    create_directory(report_directory)
    html_report = os.path.join(report_directory, 'zap_report.html')
    xml_report = os.path.join(report_directory, 'zap_report.xml')

    print(f"Running ZAP scan on the target URL: {target_url}...")
    try:
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f"{report_directory}:/zap/wrk",
            'zaproxy/zap-stable',
            'zap-full-scan.py', '-t', target_url,
            '-r', '/zap/wrk/zap_report.html',
            '-x', '/zap/wrk/zap_report.xml'
        ], check=True)
        print(f"ZAP scan completed for {target_url}. Reports saved in {report_directory}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running ZAP scan for {target_url}: {e}")
        sys.exit(1)

# Function to convert URLs from localhost to host.docker.internal
def convert_urls_to_docker_format(service_urls):
    converted_urls = []
    for url in service_urls:
        # Replace localhost with host.docker.internal in the URL
        converted_url = url.replace("http://localhost", "http://host.docker.internal")
        # Ensure the URL ends with a slash if it doesn't already have one
        if not converted_url.endswith('/'):
            converted_url += '/'
        converted_urls.append(converted_url)
    return converted_urls

# Main function
def main(central_results_dir, service_urls):
    """
    Main function to orchestrate DAST scans for all service URLs.

    Args:
        central_results_dir (str): Directory to store the scan results.
        service_urls (list): List of target URLs for DAST scanning.
    """
    # Check Docker status
    check_docker_status()

    # Pull the ZAP Docker image
    pull_zap_image()

    # Convert URLs to the desired format (host.docker.internal:8080)
    service_urls = convert_urls_to_docker_format(service_urls)

    # Run ZAP scans for each URL in the service_urls list
    for index, target_url in enumerate(service_urls, start=1):
        report_directory = os.path.join(central_results_dir, f"zap_scan_{index}")
        run_zap_scan(target_url, report_directory)

# Entry point
if __name__ == "__main__":
    # Ensure enough arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python script_name.py <CENTRAL_RESULTS_DIR> <SERVICE_URLS_LIST>")
        print("Example: python script_name.py /path/to/results \"['http://localhost:8080', 'http://localhost:8081']\"")
        sys.exit(1)

    # Parse the central results directory
    central_results_dir = os.path.abspath(sys.argv[1])

    # Parse the service URLs list (passed as a stringified Python list)
    try:
        service_urls = eval(sys.argv[2])
        if not isinstance(service_urls, list):
            raise ValueError("SERVICE_URLS_LIST must be a list.")
    except Exception as e:
        print(f"Invalid SERVICE_URLS_LIST provided: {e}")
        sys.exit(1)

    # Call the main function
    main(central_results_dir, service_urls)



 

