import json
import subprocess
import sys

import requests
from loguru import logger  # Added loguru for logging


class CommitMessageGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        logger.info("CommitMessageGenerator initialized.")

    def get_git_diff(self):
        """Get the git diff of staged changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"], capture_output=True, text=True
            )
            result.check_returncode()  # Simplified error handling
            logger.debug("Successfully retrieved git diff.")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing git diff: {e}")
            sys.exit(1)

    def generate_commit_message(self, diff):
        """Generate commit message using Ollama"""
        prompt = (
            "Given the following git diff, craft a concise commit message that:\n"
            " - Starts with a verb\n"
            " - Is specific\n"
            " - Remains under 72 characters\n\n"
            f"Diff:\n{diff}\n\nCommit message:"
        )

        try:
            response = requests.post(
                self.ollama_url,
                json={"model": "mistral", "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            message = (
                response.json()["response"].strip().split("\n")[0]
            )  # Take only the first line
            logger.debug("Generated commit message.")
            return message
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama: {e}")
            logger.error("Make sure Ollama is installed and running (ollama serve)")
            sys.exit(1)

    def commit_changes(self, message):
        """Commit changes with the given message"""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message], capture_output=True, text=True
            )
            result.check_returncode()  # Simplified error handling
            logger.info("Successfully committed changes!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing git commit: {e}")
            return False


def main():
    logger.info("Starting commit message generation process.")
    generator = CommitMessageGenerator()

    # Get git diff
    diff = generator.get_git_diff()
    if not diff:
        logger.warning("No staged changes found. Run 'git add' first.")
        sys.exit(1)

    # Generate commit message
    suggested_message = generator.generate_commit_message(diff)

    # Ask user to accept or modify
    logger.info(f"Suggested commit message: {suggested_message}")
    user_input = input("\nPress Enter to accept, or type a new message: ").strip()

    # Use user's message if provided, otherwise use generated message
    final_message = user_input if user_input else suggested_message

    # Commit changes
    if generator.commit_changes(final_message):
        logger.info("Ready to push! Use 'git push origin' to push your changes.")


if __name__ == "__main__":
    main()
