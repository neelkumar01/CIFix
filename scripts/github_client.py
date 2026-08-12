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
                    "Authorization": f"token {os.getenv("GITHUB_TOKEN")}"
               }
               response = requests.get(url, headers)

               failed_jobs.append({
                    "job_name": job.name,
                    "logs": response.text,
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