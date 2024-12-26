import os
from github import Github
from datetime import datetime

def main():
    token = os.getenv("PAT_GITHUB_TOKEN")
    if not token:
        raise ValueError("PAT_GITHUB_TOKEN environment variable is required")
    g = Github(token)
    repo_name = "laraib-sidd/reddit_bot"
    repo = g.get_repo(repo_name)
    try:
        workflows = list(repo.get_workflows())
        print(f"Found {len(workflows)} workflows")
        
        for wf in workflows:
            print(f"Processing workflow: {wf.name}")
            runs = wf.get_runs()
            total_runs = runs.totalCount
            print(f"Total runs for {wf.name}: {total_runs}")
            
            page = 0
            while True:
                try:
                    current_page = runs.get_page(page)
                    if not current_page:
                        break
                    for run in current_page:
                        print(f"Deleting run {run.id} from {run.created_at}")
                        run.delete()
                    page += 1
                except Exception as e:
                    print(f"Error processing page {page}: {str(e)}")
                    break
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
