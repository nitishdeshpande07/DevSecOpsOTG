import os
import git
from github import Github

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

# Example usage
if __name__ == "__main__":
    # Replace these with actual values
    SHARED_VOLUME_DIR = input("Enter the path to the shared volume directory: ")
    GITHUB_PAT = input("Enter your GitHub Personal Access Token: ")
    GITHUB_REPO_URL = input("Enter the GitHub repository URL (HTTPS format): ")

    push_and_merge_to_production(SHARED_VOLUME_DIR, GITHUB_PAT, GITHUB_REPO_URL)



