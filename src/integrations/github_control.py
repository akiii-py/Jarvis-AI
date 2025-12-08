"""
GitHub Integration
Manage GitHub repos and git operations via voice/text commands
"""

import subprocess
import os
from typing import Tuple, List, Optional
from github import Github, GithubException
from pathlib import Path


class GitHubController:
    """Controls GitHub operations and local git commands."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub controller.
        
        Args:
            github_token: GitHub personal access token (optional)
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.gh = None
        
        if self.github_token:
            try:
                self.gh = Github(self.github_token)
                self.user = self.gh.get_user()
            except Exception as e:
                print(f"GitHub authentication failed: {e}")
                self.gh = None
    
    def is_authenticated(self) -> bool:
        """Check if GitHub is authenticated."""
        return self.gh is not None
    
    # ============================================================================
    # GitHub API Operations
    # ============================================================================
    
    def list_repos(self, limit: int = 10) -> Tuple[bool, str]:
        """
        List user's repositories.
        
        Returns:
            (success: bool, message: str)
        """
        if not self.is_authenticated():
            return (False, "GitHub authentication required, sir. Please set GITHUB_TOKEN.")
        
        try:
            repos = list(self.user.get_repos()[:limit])
            
            if not repos:
                return (True, "You have no repositories, sir.")
            
            repo_list = "Your repositories, sir:\n"
            for repo in repos:
                stars = f"⭐{repo.stargazers_count}" if repo.stargazers_count > 0 else ""
                repo_list += f"- {repo.name} {stars}\n"
            
            return (True, repo_list)
        
        except Exception as e:
            return (False, f"Could not fetch repositories: {e}")
    
    def create_repo(self, repo_name: str, description: str = "", private: bool = False) -> Tuple[bool, str]:
        """
        Create a new GitHub repository.
        
        Returns:
            (success: bool, message: str)
        """
        if not self.is_authenticated():
            return (False, "GitHub authentication required, sir.")
        
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=True
            )
            
            return (True, f"Created repository '{repo_name}', sir. URL: {repo.html_url}")
        
        except GithubException as e:
            if e.status == 422:
                return (False, f"Repository '{repo_name}' already exists, sir.")
            return (False, f"Could not create repository: {e}")
    
    def get_latest_commit(self, repo_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Get latest commit info.
        
        Args:
            repo_name: Repository name (uses current dir if None)
        
        Returns:
            (success: bool, message: str)
        """
        if repo_name and self.is_authenticated():
            try:
                repo = self.user.get_repo(repo_name)
                commits = list(repo.get_commits()[:1])
                if commits:
                    commit = commits[0]
                    return (True, f"Latest commit: {commit.commit.message} by {commit.commit.author.name}")
            except Exception as e:
                return (False, f"Could not fetch commit: {e}")
        
        # Fallback to local git
        return self._run_git_command(["git", "log", "-1", "--oneline"])
    
    # ============================================================================
    # Local Git Operations
    # ============================================================================
    
    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a git command locally."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip() or "Done, sir."
                return (True, output)
            else:
                error = result.stderr.strip() or "Command failed, sir."
                return (False, error)
        
        except subprocess.TimeoutExpired:
            return (False, "Command timed out, sir.")
        except Exception as e:
            return (False, f"Error: {e}")
    
    def git_status(self) -> Tuple[bool, str]:
        """Get git status."""
        return self._run_git_command(["git", "status", "--short"])
    
    def git_add_all(self) -> Tuple[bool, str]:
        """Stage all changes."""
        return self._run_git_command(["git", "add", "-A"])
    
    def git_commit(self, message: str) -> Tuple[bool, str]:
        """Commit staged changes."""
        return self._run_git_command(["git", "commit", "-m", message])
    
    def git_push(self) -> Tuple[bool, str]:
        """Push to remote."""
        return self._run_git_command(["git", "push"])
    
    def git_pull(self) -> Tuple[bool, str]:
        """Pull from remote."""
        return self._run_git_command(["git", "pull"])
    
    def git_branch(self) -> Tuple[bool, str]:
        """List branches."""
        return self._run_git_command(["git", "branch"])
    
    def quick_commit_push(self, message: str) -> Tuple[bool, str]:
        """
        Quick workflow: add all, commit, push.
        
        Returns:
            (success: bool, message: str)
        """
        # Add all
        success, msg = self.git_add_all()
        if not success:
            return (False, f"Could not stage changes: {msg}")
        
        # Commit
        success, msg = self.git_commit(message)
        if not success:
            return (False, f"Could not commit: {msg}")
        
        # Push
        success, msg = self.git_push()
        if not success:
            return (False, f"Could not push: {msg}")
        
        return (True, f"Changes committed and pushed, sir. Message: '{message}'")
