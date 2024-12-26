## The Principal Script that is responsible for 
## Calling the Entire Security Scanning Functionalties from this point. 
## This would the calling point for the SCA SAST DAST 
## 1. Currently provides the local project repo path for further usage.
## 2. Now basically we are able to succesfully clone the latest commit based github
## target repo so now we would be downloading this cloned project repo into a directory of our
## choice locally.. 
## Fully working JENKINS-JOB based Master script working perfect and sucesfully.
## Remember and make sure that this is the part of the mount_scripts dir.
import os
import sys
import subprocess

def clone_repo_to_shared_repo(github_url, shared_repo_path):
    """
    Clone the GitHub repository directly into the shared_repo directory.
    """
    try:
        if not github_url:
            raise ValueError("GitHub URL not provided.")
        
        # Normalize the shared_repo_path
        normalized_shared_repo_path = os.path.normpath(shared_repo_path)
        
        # Ensure the shared_repo directory exists
        if not os.path.exists(normalized_shared_repo_path):
            print(f"Shared repository path '{normalized_shared_repo_path}' does not exist. Creating it...")
            os.makedirs(normalized_shared_repo_path)
        
        print(f"Cloning the repository: {github_url}")
        
        # Define the target path inside the shared repository
        target_path = os.path.join(normalized_shared_repo_path, os.path.basename(github_url).replace(".git", ""))
        
        # Run the git clone command directly into the shared_repo directory
        subprocess.run(["git", "clone", github_url, target_path], check=True)
         
        # Verify the repository was cloned
        if not os.path.isdir(target_path):
            raise Exception("Failed to clone the repository.")
        
        print(f"Repository cloned successfully to: {target_path}")
        return target_path
    
    except subprocess.CalledProcessError as e:
        print(f"Error during git clone: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    # Ensure the GitHub URL and shared_repo_path are passed as arguments
    if len(sys.argv) < 3:
        print("Usage: python master_script.py <GitHub URL> <Shared Repository Path>")
        sys.exit(1)
    
    # Get the GitHub URL and shared_repo path from the command-line arguments
    github_url = sys.argv[1]
    shared_repo_path = sys.argv[2]
    
    # Debug: Print initial arguments
    print(f"Debug - GitHub URL: {github_url}")
    print(f"Debug - Shared repository path: {shared_repo_path}")
    
    # Clone the repository into the shared repository
    cloned_path = clone_repo_to_shared_repo(github_url, shared_repo_path)
    
    # Print the final cloned path for verification
    print(f"Repository successfully set up at: {cloned_path}")

if __name__ == "__main__":
    main()







