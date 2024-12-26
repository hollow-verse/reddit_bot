import os
from github import Github

def main():
    token = os.getenv("PAT_GITHUB_TOKEN")
    if not token:
        raise ValueError("PAT_GITHUB_TOKEN environment variable is required")
    g = Github(token)
    repo_name = "laraib-sidd/reddit_bot"
    repo = g.get_repo(repo_name)
    for wf in repo.get_workflows():
        for run in wf.get_runs():
            run.delete()

if __name__ == "__main__":
    main()
