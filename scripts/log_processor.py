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
          logs: str
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
          "not found",
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
          "Killed",
          "kubectl error",
          "helm upgrade failed",
          "terraform error",
          "Error:",
          "BUILD FAILURE",
          "BUILD FAILED",
          "Compilation failed",
          "Tests failed",
     ]

     relevant_log_lines = []

     for i, line in enumerate(lines):
          if any(keyword in line for keyword in error_keywords):
               start = max(0, i - 10)
               end = min(len(lines), i + 10)
               relevant_log_lines.extend(lines[start:end])

     seen = set()
     unique_lines = []
     for line in relevant_log_lines:
          if line not in seen:
               seen.add(line)
               unique_lines.append(line)
               
     return "\n".join(unique_lines[:300])

def analyse_failure(
          job_name: str,
          logs: str,
          failed_steps: list[str]
) -> str:
     relevant_logs = extract_relevant_logs(logs)

     system_prompt = """
You are a senior DevOps engineer.

Analyze CI/CD pipeline failures and identify the root cause.

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