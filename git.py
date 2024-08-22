import subprocess

class Git:
    """
    A class that encapsulates Git-related operations.
    """

    @staticmethod
    def fetch(repo_path: str) -> None:
        """
        Fetch the latest changes from the remote repository.

        :param repo_path: The path to the Git repository.
        """
        subprocess.run(["git", "fetch"], cwd=repo_path, check=True)

    @staticmethod
    def has_new_commits(repo_path: str) -> bool:
        """
        Check if there are new commits in the remote repository.

        :param repo_path: The path to the Git repository.
        :return: True if there are new commits, otherwise False.
        """
        local_head = subprocess.check_output(
            ["git", "rev-parse", "@{0}"],
            cwd=repo_path
        ).strip()

        remote_head = subprocess.check_output(
            ["git", "rev-parse", "@{u}"],
            cwd=repo_path
        ).strip()

        return local_head != remote_head

    @staticmethod
    def pull(repo_path: str) -> None:
        """
        Pull the latest changes from the remote repository.

        :param repo_path: The path to the Git repository.
        """
        subprocess.run(["git", "pull"], cwd=repo_path, check=True)
