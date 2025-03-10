"""Utility for syncing secrets between GitHub repository and local .env file."""
from github import Github
import os
import base64
import logging
from nacl import encoding, public
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using LibSodium."""
    public_key_bytes = base64.b64decode(public_key)
    public_key = public.PublicKey(public_key_bytes)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def create_or_update_secret(
    repo, secret_name: str = None, secret_value: str = None, secret_type: str = "actions"
):
    """Create or update a repository secret."""
    try:
        repo.create_secret(secret_name, secret_value, secret_type)
        logger.info(f"Created/updated secret: {secret_name}")
    except Exception as e:
        logger.error(f"Failed to create/update secret {secret_name}: {e}")


def delete_all_secrets(repo):
    """Delete all repository secrets."""
    try:
        for secret in repo.get_secrets():
            repo.delete_secret(secret.name)
            logger.info(f"Deleted secret: {secret.name}")
    except Exception as e:
        logger.error(f"Failed to delete secrets: {e}")


def sync_github_secrets():
    """Sync secrets from GitHub repository to local environment."""
    # Initialize GitHub client
    github_token = os.getenv('PAT_GITHUB_TOKEN')
    if not github_token:
        logger.error("PAT_GITHUB_TOKEN environment variable is required")
        return

    try:
        g = Github(github_token)
        
        # Get repository (default to current repo if not in GitHub Actions)
        repo_name = os.environ.get('GITHUB_REPOSITORY', "laraib_sidd/reddit_bot")
        repo = g.get_repo(repo_name)
        logger.info(f"Connected to GitHub repository: {repo.full_name}")
        
        # Display available secrets
        secrets = repo.get_secrets()
        secret_names = [secret.name for secret in secrets]
        logger.info(f"Found {len(secret_names)} secrets in the repository")
        
        # Display available variables
        variables = repo.get_variables()
        logger.info(f"Found {variables.totalCount} variables in the repository")
        
        # Convert variables to secrets if needed
        for variable in variables:
            logger.info(f"Found variable: {variable.name}")
            # Uncomment the following line to convert variables to secrets
            # create_or_update_secret(repo, variable.name, variable.value, "actions")
            
        logger.info("GitHub secrets sync completed")
        
    except Exception as e:
        logger.error(f"Error in GitHub secrets sync: {e}")
        raise 