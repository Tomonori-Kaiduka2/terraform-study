import os
import sys
from github import Github, Auth
from google.cloud import aiplatform
from google.api_core.client_options import ClientOptions


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


def resolve_model_name(model: str, project: str, location: str) -> str:
    if model.startswith("projects/"):
        return model
    if not project:
        raise ValueError("GCP_PROJECT is required when VERTEX_MODEL is not a full resource path.")
    return f"projects/{project}/locations/{location}/publishers/google/models/{model}"


def parse_vertex_response(response) -> str:
    if hasattr(response, "predictions") and response.predictions:
        first = response.predictions[0]
        if isinstance(first, dict):
            if "content" in first:
                return first["content"]
            if "candidates" in first and first["candidates"]:
                candidate = first["candidates"][0]
                if isinstance(candidate, dict) and "content" in candidate:
                    return candidate["content"]
                return str(candidate)
        return str(first)
    return str(response)


def generate_analysis(client, model_name: str, title: str, body: str, comment: str) -> str:
    prompt = (
        "You are an expert software engineer. Analyze the following GitHub issue and provide a concise technical analysis. "
        "Return the response in markdown with sections: Summary, Likely Cause, Suggested Fixes, and Next Steps.\n\n"
        f"Issue Title:\n{title}\n\n"
        f"Issue Body:\n{body}\n\n"
    )
    if comment:
        prompt += f"Trigger Comment:\n{comment}\n\n"

    request = aiplatform.gapic.types.PredictRequest(
        endpoint=model_name,
        instances=[{"content": prompt}],
        parameters={"temperature": 0.2, "maxOutputTokens": 600},
    )
    response = client.predict(request=request)
    return parse_vertex_response(response)


def main() -> int:
    github_token = get_env("GITHUB_TOKEN")
    gcp_project = get_env("GCP_PROJECT")
    gcp_location = get_env("GCP_LOCATION", "us-central1")
    vertex_model = get_env("VERTEX_MODEL", "gemini-1.5-mini")
    issue_number = get_env("ISSUE_NUMBER")
    event_name = get_env("EVENT_NAME")
    comment_body = get_env("COMMENT_BODY")

    if not github_token:
        print("GITHUB_TOKEN is required.", file=sys.stderr)
        return 1

    if not issue_number:
        print("ISSUE_NUMBER is required.", file=sys.stderr)
        return 1

    if not gcp_project:
        print("GCP_PROJECT is required.", file=sys.stderr)
        return 1

    try:
        issue_number_int = int(issue_number)
    except ValueError:
        print("ISSUE_NUMBER must be an integer.", file=sys.stderr)
        return 1

    client = aiplatform.gapic.PredictionServiceClient(
        client_options=ClientOptions(api_endpoint=f"{gcp_location}-aiplatform.googleapis.com")
    )
    model_name = resolve_model_name(vertex_model, gcp_project, gcp_location)

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

    analysis = generate_analysis(issue.title, issue.body or "", comment_body, model_name)

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
