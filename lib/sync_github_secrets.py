from github import Github
import os
import base64
from nacl import encoding, public


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using LibSodium"""
    public_key_bytes = base64.b64decode(public_key)
    public_key = public.PublicKey(public_key_bytes)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def create_or_update_secret(
    repo, secret_name: str, secret_value: str,secret_type: str = "actions"
):
    """Create or update a repository secret"""

    # Get repository's public key for secret encryption
    public_key = repo.get_public_key()
    encrypted_value = encrypt_secret(public_key.key, secret_value)

    repo.create_secret(secret_name, encrypted_value, secret_type)


def delete_all_secrets(repo):
    """Delete all repository secrets"""
    for secret in repo.get_secrets():
        repo.delete_secret(secret.name)


def main():
    # Initialize GitHub client
    github_token = os.getenv('PAT_GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    g = Github(github_token)

    # Get repository (replace with your repository details)
    repo_name = "hollow-verse/reddit_bot"
    repo = g.get_repo(repo_name)

    # delete_all_secrets(repo)
    # Convert each variable into a secret
    for variable in repo.get_variables():
        print(variable.name,variable.value)
        # create_or_update_secret(repo, variable.name, variable.value, "actions")


if __name__ == "__main__":
    main()
