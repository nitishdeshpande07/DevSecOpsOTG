## Oneclick DevSecOps : Hassle Free DevSecOps Provisioning 
## Shift Left At Fingertips
import subprocess
import sys

def run_script(script_name):
    """Runs a Python script in the same directory and handles errors."""
    try:
        # print(f"Running {script_name}...")
        subprocess.check_call([sys.executable, script_name])
        print(f"\n {script_name} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(1)  # Exit if a script fails

def main():  
    """Main function to execute the scripts in order."""
    
    # List of scripts to execute in order
    scripts = [
        "cli-opening.py",
        "setup.py",
        "jenkins-setup-test-f.py",
        "ci-cd-test-setup.py"
    ]
    
    # Run each script in the order specified
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main() 

