import os
import sys
from github import Github, Auth
from openai import OpenAI


def get_env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    if value is None:
        return default
    return value.strip()


def create_issue_comment(issue, body: str) -> None:
    issue.create_comment(body)


def add_label(issue, label_name: str) -> None:
    labels = [label.name for label in issue.labels]
    if label_name not in labels:
        issue.add_to_labels(label_name)


def generate_analysis(title: str, body: str, comment: str, model: str) -> str:
    prompt = (
        "You are an expert software engineer. Analyze the following GitHub issue and provide a concise technical analysis. "
        "Return the response in markdown with sections: Summary, Likely Cause, Suggested Fixes, and Next Steps.\n\n"
        f"Issue Title:\n{title}\n\n"
        f"Issue Body:\n{body}\n\n"
    )
    if comment:
        prompt += f"Trigger Comment:\n{comment}\n\n"

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "You are a professional AI assistant for GitHub issue triage and analysis."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=600,
        temperature=0.2,
    )
    if hasattr(response, 'output_text') and response.output_text:
        return response.output_text.strip()
    if response.output and len(response.output) > 0:
        first_item = response.output[0]
        if isinstance(first_item, dict) and 'content' in first_item:
            for chunk in first_item['content']:
                if 'text' in chunk:
                    return chunk['text'].strip()
    return str(response)


def main() -> int:
    github_token = get_env("GITHUB_TOKEN")
    ai_api_key = get_env("AI_API_KEY")
    ai_model = get_env("AI_MODEL", "gemini-1.5-mini")
    issue_number = get_env("ISSUE_NUMBER")
    event_name = get_env("EVENT_NAME")
    comment_body = get_env("COMMENT_BODY")

    if not github_token:
        print("GITHUB_TOKEN is required.", file=sys.stderr)
        return 1

    if not ai_api_key:
        print("AI_API_KEY is required. Set GEMINI_API_KEY in GitHub Secrets.", file=sys.stderr)
        return 1

    if not issue_number:
        print("ISSUE_NUMBER is required.", file=sys.stderr)
        return 1

    try:
        issue_number_int = int(issue_number)
    except ValueError:
        print("ISSUE_NUMBER must be an integer.", file=sys.stderr)
        return 1

    client = OpenAI(api_key=ai_api_key)
    github = Github(auth=Auth.Token(github_token))
    repo = github.get_repo(os.getenv("GITHUB_REPOSITORY"))
    issue = repo.get_issue(number=issue_number_int)

    trigger_label = "needs-ai-review"
    trigger_comment = "/ai review"

    if event_name == "issues":
        labels = [label.name for label in issue.labels]
        if trigger_label not in labels:
            print(f"Skipping analysis because label '{trigger_label}' is not present.")
            return 0
    elif event_name == "issue_comment":
        if trigger_comment not in comment_body.lower():
            print(f"Skipping analysis because comment does not contain '{trigger_comment}'.")
            return 0
    else:
        print(f"Unsupported event: {event_name}")
        return 0

    analysis = generate_analysis(issue.title, issue.body or "", comment_body, ai_model)

    comment = (
        "### 🤖 AI Issue Analysis\n"
        "Thank you for filing this issue. I analyzed the content and here is a suggested diagnosis:\n\n"
        f"{analysis}\n\n"
        "*このコメントは自動生成されています。必要に応じて内容を確認し、ラベルや対応を追加してください。*"
    )

    create_issue_comment(issue, comment)
    add_label(issue, "ai-reviewed")

    print("Analysis comment posted and label added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
