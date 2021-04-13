import requests
import os
import json
import sys

from typing import Union

SUCCESS = "success"
FAILURE = "failure"
WARNING = "warning"


def action_color(status: str):
    """
    Get a action color based on the workflow status.
    """

    if status == SUCCESS:
        return "good"
    elif status == FAILURE:
        return "danger"

    return WARNING


def action_status(status: str):
    """
    Get a transformed status based on the workflow status.
    """

    if status == SUCCESS:
        return "passed"
    elif status == FAILURE:
        return "failed"

    return "passed with warnings"


def action_emoji(status: str):
    """
    Get an emoji based on the workflow status.
    """

    if status == SUCCESS:
        return ":thumbsup:"
    elif status == FAILURE:
        return ":middle_finger:"

    return ":warning:"


def notify_slack(job_status: str, notify_when: Union[str, None]):
    url = os.getenv("SLACK_WEBHOOK_URL")
    workflow = os.getenv("GITHUB_WORKFLOW")
    repo = os.getenv("GITHUB_REPOSITORY")
    branch = os.getenv("GITHUB_REF")
    commit = os.getenv("GITHUB_SHA")
    stage = os.getenv("STAGE")

    commit_url = f"https://github.com/{repo}/commit/{commit}"
    repo_url = f"https://github.com/{repo}/actions"

    color = action_color(job_status)
    status_message = action_status(job_status)
    emoji = action_emoji(job_status)

    message = f"{emoji} {stage} {workflow} {status_message} in <{repo_url}|{repo}> on <{commit_url}|{commit[:7]}>."

    payload = {
        "attachments": [
            {
                "text": message,
                "color": color,
                "mrkdwn_in": ["text"],
                "footer": "Forked by <https://kicksaw.com|Kicksaw>",
            }
        ]
    }

    payload = json.dumps(payload)

    headers = {"Content-Type": "application/json"}

    if notify_when is None:
        notify_when = "success,failure,warnings"

    if job_status in notify_when and not testing:
        requests.post(url, data=payload, headers=headers)


def main():
    job_status = os.getenv("INPUT_STATUS")
    notify_when = os.getenv("INPUT_NOTIFY_WHEN")
    notify_slack(job_status, notify_when)


if __name__ == "__main__":
    try:
        testing = True if sys.argv[1] == "--test" else False
    except IndexError as e:
        testing = False

    main()
