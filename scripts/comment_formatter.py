def format_pr_comment(
          analyses: list[dict]
) -> str:
     """
     Format analyses into a PR comment
     """
     comment = "## CI Failure Analysis 👀\n\n"

     comment += "> Automatically analysed by the CI Failure Analyser\n\n"

     for analysis in analyses:
        comment += f"### ❌ {analysis['job_name']}\n\n"
        comment += f"Diagnosis\n{analysis['diagnosis']}"
        comment += "\n\n - - - - - - - - - - - - - - -\n\n"

     comment += "*Analysis powered by Groq AI. Always verify before applying fixes*"

     return comment