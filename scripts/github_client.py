from github import Github
import os
import requests


g = Github(os.getenv("GITHUB_TOKEN"))


def get_logs(
    repo_name: str,
    run_id: int
) -> list[dict]:

    repo = g.get_repo(repo_name)
    run = repo.get_workflow_run(run_id)

    failed_jobs = []

    for job in run.jobs():

        if job.conclusion == "failure":

            url = (
                f"https://api.github.com/repos/"
                f"{repo_name}/actions/jobs/{job.id}/logs"
            )

            headers = {
                "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            failed_jobs.append({
                "job_name": job.name,
                "logs": response.text,
                "failed_steps": [
                    step.name
                    for step in job.steps
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