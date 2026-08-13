from github import Github
import os
import requests

g = Github(os.getenv("GITHUB_TOKEN"))

def get_logs(
          repo_name: str,
          run_id: int
) -> list[dict]:
     """This function gets failure job logs of a specific workflow run"""

     repo = g.get_repo(repo_name)
     run = repo.get_workflow_run(run_id)

     failed_jobs = []

     for job in run.jobs():
          if job.conclusion == "failure":
               # get log url
               url = job.logs_url()

               # retrieve logs
               headers = {
                    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
                    "Accept": "application/vnd.github+json",
               }
               response = requests.get(
                    url, 
                    headers=headers,
                    allow_redirects=False
               )
               response.raise_for_status()

               log_url = response.headers["Location"]

               log_response = requests.get(log_url)
               log_response.raise_for_status()

               failed_jobs.append({
                    "job_name": job.name,
                    "logs": log_response.text,
                    "failed_steps": [
                         step.name for step in job.steps
                         if step.conclusion == "failure"
                    ]
               })
     return failed_jobs

def post_pr_comment(
          repo_name: str,
          pr_number: int,
          comment: str
):
     repo = g.get_repo(repo_name)
     pr = repo.get_pull(pr_number)
     pr.create_issue_comment(comment)