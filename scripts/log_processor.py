import os

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=2000,
    max_retries=2,
)


def extract_relevant_logs(
    logs: str,
    failed_steps: list[str]
) -> str:
    """
    Extract most relevant log sections around failures from complete log
    """

    lines = logs.split("\n")

    error_keywords = [
        "ERROR",
        "error",
        "FAILED",
        "Failed",
        "FAIL",
        "fatal:",
        "Exception",
        "Traceback",
        "panic:",
        "segmentation fault",
        "permission denied",
        "access denied",
        "unauthorized",
        "forbidden",
        "connection refused",
        "connection reset",
        "timeout",
        "timed out",
        "No such file",
        "command not found",
        "ModuleNotFoundError",
        "ImportError",
        "SyntaxError",
        "TypeError",
        "ValueError",
        "AssertionError",
        "npm ERR!",
        "ERR_PNPM",
        "yarn error",
        "ELIFECYCLE",
        "ERESOLVE",
        "ENOENT",
        "Docker daemon",
        "docker: Error",
        "manifest unknown",
        "pull access denied",
        "ImagePullBackOff",
        "CrashLoopBackOff",
        "OOMKilled",
        "OutOfMemory",
        "kubectl error",
        "helm upgrade failed",
        "terraform error",
        "BUILD FAILURE",
        "BUILD FAILED",
        "Compilation failed",
        "Tests failed",

        # GitHub Actions specific
        "Process completed with exit code",
        "exit code",
        "##[error]",
    ]

    relevant_indices = set()

    for i, line in enumerate(lines):

        if any(step in line for step in failed_steps):
            start = max(0, i - 15)
            end = min(len(lines), i + 30)

            for j in range(start, end):
                relevant_indices.add(j)

        if any(keyword in line for keyword in error_keywords):
            start = max(0, i - 10)
            end = min(len(lines), i + 10)

            for j in range(start, end):
                relevant_indices.add(j)

    return "\n".join(
        lines[i]
        for i in sorted(relevant_indices)
    )


def analyse_failure(
    job_name: str,
    logs: str,
    failed_steps: list[str]
) -> str:

    relevant_logs = extract_relevant_logs(
        logs,
        failed_steps
    )

    system_prompt = """
You are a senior DevOps engineer.

Analyze CI/CD pipeline failures and identify the actual root cause.

Important rules:

- Give highest priority to the explicitly failed step.
- Look at the command executed in the failed step.
- Look for the exit code of the failed command.
- Prefer the direct cause of the failed step over unrelated errors or warnings.
- Do not assume technologies, cloud providers, services, or dependencies unless they are clearly shown in the logs.
- Do not treat unrelated authentication, warning, or API messages as the root cause.
- If a command intentionally exits with a non-zero exit code, identify that command as the root cause.
- Only make conclusions supported by the provided logs.
- If the root cause cannot be determined, clearly say that the logs are insufficient.

Provide:

1. Root Cause
2. Evidence from logs
3. Recommended Fix
4. Prevention

Be concise and actionable.
"""

    prompt = f"""
Job Name:
{job_name}

Failed Steps:
{failed_steps}

Logs:
{relevant_logs}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]

    response = llm.invoke(messages)

    return response.content