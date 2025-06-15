#!/usr/bin/env python
"""
Script to delete GitHub repositories that are forks and have no commits from the authenticated user.
Usage: python delete_empty_forks.py
"""

import sys
import time
from getpass import getpass

try:
    from github import Github, GithubException
except ImportError:
    print("Required package not found. Installing PyGithub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub"])
    from github import Github, GithubException

def main():
    # Get GitHub token
    token = getpass("Enter your GitHub personal access token: ")

    # Authenticate with GitHub
    g = Github(token)

    try:
        # Get the authenticated user
        user = g.get_user()
        username = user.login
        print(f"Authenticated as: {username}")

        # Get all repositories
        repos = user.get_repos()

        # Filter for forks
        forks_to_delete = []

        for repo in repos:
            if repo.fork:
                # Check if user has made any commits
                try:
                    commits = list(repo.get_commits(author=username))
                    if not commits:
                        forks_to_delete.append(repo)
                        print(f"Found fork with no commits: {repo.full_name}")
                except GithubException as e:
                    # This can happen if the repository is empty
                    print(f"Error checking commits for {repo.full_name}: {e}")
                    forks_to_delete.append(repo)

                # Add a small delay to avoid hitting rate limits
                time.sleep(0.5)

        # Confirm deletion
        if forks_to_delete:
            print(f"\nFound {len(forks_to_delete)} forks with no commits:")
            for repo in forks_to_delete:
                print(f"- {repo.full_name}")

            confirm = input("\nDo you want to delete these repositories? (yes/no): ").lower()
            if confirm == "yes":
                for repo in forks_to_delete:
                    print(f"Deleting {repo.full_name}...")
                    repo.delete()
                print("Deletion complete!")
            else:
                print("Operation cancelled.")
        else:
            print("No forks without commits were found.")

    except GithubException as e:
        print(f"GitHub API error: {e}")

if __name__ == "__main__":
    main()
