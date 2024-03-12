import subprocess

def generate_issue(owner: str, repo: str, title: str, body: str):
    output = subprocess.check_output(
        [
            "gh", "api",
            "--method", "POST",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues",
            "-f", f"title='{title}'",
            "-f", f"body='{body}'"
        ]
    )

    return output


if __name__ == "__main__":
    generate_issue("start-out", "todo-or-not", "python did this", "and I for one am stoked about it")
