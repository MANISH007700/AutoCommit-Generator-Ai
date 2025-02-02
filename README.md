# AutoCommit-Generator-Ai

Create Github Commit Message Automatically based on your code changes

## Steps to Reproduce

1 - Clone the repo `git clone <repo_id.git>`
2 - Make the code executable `chmod +x < .py filename>` : example `chmod +x commit-generator.py`
3 - Make the bash file executable `chmod +x <bashfile>` : example `chmod +x com_ai`
4 - Move both of them to local usr folder
`sudo mv commit_generator.py /usr/local/bin/`
`sudo mv com_ai /usr/local/bin/`

5 - You can run it now just by calling the bashfile from anywhere in the terminal now like this
`com_ai` : and this will automatically create the github commit message for you based on `git diff`
