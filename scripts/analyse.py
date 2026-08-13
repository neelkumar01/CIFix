import os

from github_client import get_logs, post_pr_comment
from log_processor import analyse_failure
from comment_formatter import format_pr_comment

repo_name = os.getenv("REPO_NAME")
run_id = int(os.getenv("RUN_ID"))
pr_number = int(os.getenv("PR_NUMBER"))

def main():
     failed_jobs = get_logs(repo_name, run_id)

     analyses = []

     for job in failed_jobs:
          diagnosis = analyse_failure(
               job["job_name"],
               job["logs"],
               job["failed_steps"]
          )

          analyses.append({
               "job_name": job["job_name"],
               "diagnosis": diagnosis
          })
     comment = format_pr_comment(analyses)
     post_pr_comment(
          repo_name,
          pr_number,
          comment
     )

if __name__ == "__main__":
     main()