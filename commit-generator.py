import json
import subprocess
import sys
import requests


class CommitMessageGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def get_git_diff(self):
        """Get the git diff of staged changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print("Error: Failed to get git diff")
                sys.exit(1)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing git diff: {e}")
            sys.exit(1)

    def generate_commit_message(self, diff):
        """Generate commit message using Ollama"""
        prompt = f"""Given the following git diff, craft a concise commit message that:
            - Starts with a verb
            - Is specific
            - Remains under 72 characters

            Diff:
            {diff}

            Commit message:"""

        try:
            response = requests.post(
                self.ollama_url,
                json={"model": "mistral", "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            message = response.json()["response"].strip()
            # Take only the first line
            return message.split("\n")[0]
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama: {e}")
            print("Make sure Ollama is installed and running (ollama serve)")
            sys.exit(1)

    def commit_changes(self, message):
        """Commit changes with the given message"""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message], capture_output=True, text=True
            )
            if result.returncode == 0:
                print("Successfully committed changes!")
                return True
            else:
                print(f"Error committing changes: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error executing git commit: {e}")
            return False


def main():
    generator = CommitMessageGenerator()

    # Get git diff
    diff = generator.get_git_diff()
    if not diff:
        print("No staged changes found. Run 'git add' first.")
        sys.exit(1)

    # Generate commit message
    suggested_message = generator.generate_commit_message(diff)

    # Ask user to accept or modify
    print(f"\nSuggested commit message: {suggested_message}")
    user_input = input("\nPress Enter to accept, or type a new message: ").strip()

    # Use user's message if provided, otherwise use generated message
    final_message = user_input if user_input else suggested_message

    # Commit changes
    if generator.commit_changes(final_message):
        print("\nReady to push! Use 'git push origin' to push your changes.")


if __name__ == "__main__":
    main()
