import os
import sys
import asyncio
from github import Github, Auth
from google import genai

def get_env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if value else default

def create_issue_comment(issue, body: str) -> None:
    issue.create_comment(body)

def add_label(issue, label_name: str) -> None:
    labels = [label.name for label in issue.labels]
    if label_name not in labels:
        issue.add_to_labels(label_name)

async def generate_analysis(client, model_id: str, title: str, body: str, comment: str) -> str:
    prompt = (
        "You are an expert software engineer. Analyze the following GitHub issue and provide a concise technical analysis. "
        "Return the response in markdown with sections: Summary, Likely Cause, Suggested Fixes, and Next Steps.\n\n"
        f"Issue Title:\n{title}\n\n"
        f"Issue Body:\n{body}\n\n"
    )
    if comment:
        prompt += f"Trigger Comment:\n{comment}\n\n"

    try:
        # 最初のコードと同じ aio (非同期) クライアントを使用
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=prompt,
            config={'temperature': 0.2, 'max_output_tokens': 800}
        )
        return response.text
    except Exception as e:
        return f"Error during AI analysis: {e}"

async def main_async() -> int:
    # 必要な情報の取得
    github_token = get_env("GITHUB_TOKEN")
    api_key = get_env("GEMINI_API_KEY")
    model_id = get_env("GEMINI_MODEL", "gemini-2.0-flash") # 2.5が未リリースの場合は2.0を指定
    
    issue_number = get_env("ISSUE_NUMBER")
    event_name = get_env("EVENT_NAME")
    comment_body = get_env("COMMENT_BODY")
    repo_name = get_env("GITHUB_REPOSITORY")

    # 必須チェック
    if not github_token or not api_key or not repo_name or not issue_number:
        print("Missing required environment variables (GITHUB_TOKEN, GEMINI_API_KEY, GITHUB_REPOSITORY, ISSUE_NUMBER)", file=sys.stderr)
        return 1

    try:
        issue_number_int = int(issue_number)
        
        # クライアントの初期化
        client = genai.Client(api_key=api_key)
        github = Github(auth=Auth.Token(github_token))
        repo = github.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number_int)

        # トリガー条件のチェック
        trigger_label = "needs-ai-review"
        trigger_comment = "/ai review"

        if event_name == "issues":
            labels = [label.name for label in issue.labels]
            if trigger_label not in labels:
                print(f"Skipping: Label '{trigger_label}' not found.")
                return 0
        elif event_name == "issue_comment":
            if trigger_comment not in comment_body.lower():
                print(f"Skipping: Comment does not contain '{trigger_comment}'.")
                return 0

        # AI分析の実行
        print(f"Analyzing issue #{issue_number_int}...")
        analysis = await generate_analysis(client, model_id, issue.title, issue.body or "", comment_body)

        comment_text = (
            "### 🤖 AI Issue Analysis\n"
            "Thank you for filing this issue. I analyzed the content and here is a suggested diagnosis:\n\n"
            f"{analysis}\n\n"
            "*このコメントは自動生成されています。*"
        )

        # 結果の反映
        create_issue_comment(issue, comment_text)
        add_label(issue, "ai-reviewed")

        print("Analysis comment posted successfully.")
        return 0

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    # 非同期関数の実行
    exit_code = asyncio.run(main_async())
    sys.exit(exit_code)