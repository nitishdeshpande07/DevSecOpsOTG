import subprocess
import sys

def run_script(script_name):
    """Runs a Python script in the same directory and handles errors."""
    try:
        # Using `Popen` for better control while preserving full interactivity
        process = subprocess.Popen(
            [sys.executable, script_name],
        )
        process.communicate()  # Wait for the script to complete while preserving interactivity
        
        if process.returncode != 0:
            print(f"Error running {script_name}. Return code: {process.returncode}")
            sys.exit(1)  # Exit if a script fails

        print(f"\n{script_name} executed successfully.")
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(1)

def main():
    """Main function to execute the scripts in order."""
    
    # List of scripts to execute in order
    scripts = [
        "cli-opening.py",
        "setup.py",
        "jenkins-setup.py",
        "ci-cd-test-setup.py"
    ]
    
    # Run each script in the order specified
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main()
