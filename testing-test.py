import os
import subprocess
import sys


def get_user_inputs():
    """
    Collect all user inputs.

    Returns:
        dict: A dictionary containing user input values.
    """
    inputs = {
        "shared_volume_dir": input("Enter the local directory path for the shared volume for latest repo copies: ").strip(),
        "CENTRAL_RESULTS_DIR": input("Enter the local directory path for storing all the Central Security Scan Results: ").strip(),
        "GITHUB_REPO_URL": input("Repo URL: ").strip(),
        "GITHUB_REPO": input("Enter the target GitHub repository (format: repo): ").strip(),
    }
    return inputs


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


def main():
    """
    Main function to orchestrate the deployment and DAST testing.
    """
    # Get user inputs
    inputs = get_user_inputs()

    # Run deployment script and get URLs
    print("Running Local Deployment...")
    url_list = run_deployment_script(inputs["shared_volume_dir"], inputs["GITHUB_REPO"])

    # Trigger DAST testing
    print("Running DAST testing...")
    trigger_dast_test(inputs["CENTRAL_RESULTS_DIR"], url_list)


if __name__ == "__main__":
    main()




