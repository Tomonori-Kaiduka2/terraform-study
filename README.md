# Terraform Study Project

このプロジェクトは、Terraformを使ってインフラを管理し、StreamlitアプリケーションをDockerコンテナでデプロイ・テストするサンプルです。

## プロジェクト構造

```
terraform-study/
├── main.tf                    # Terraform設定ファイル
├── terraform.tfvars           # Terraform変数ファイル
├── app/                       # Streamlitアプリケーション
│   ├── app.py                 # Streamlitアプリ本体
│   ├── Dockerfile             # Dockerイメージ定義
│   ├── requirements.txt       # Python依存関係
│   └── tests/                 # テストコード
│       └── test_app.py        # Playwrightテスト
├── .github/workflows/         # GitHub Actions CI/CD
│   └── docker-build.yaml      # Dockerビルド・テストワークフロー
└── README.md                  # このファイル
```

## セットアップ

### 1. Terraformの初期化

```bash
terraform init
```

### 2. 計画の確認

```bash
terraform plan
```

### 3. インフラのデプロイ

```bash
terraform apply
```

## アプリケーションの実行

### Dockerイメージのビルド

```bash
cd app
docker build -t streamlit-app .
```

### コンテナの実行

```bash
docker run -p 8501:8501 streamlit-app
```

ブラウザで `http://localhost:8501` にアクセスしてアプリを確認できます。

## テスト

### ローカルテスト実行

```bash
# 依存関係インストール
pip install -r requirements-test.txt
playwright install chromium --with-deps

# アプリ起動
docker run -d -p 8501:8501 streamlit-app

# テスト実行
pytest app/tests/test_app.py
```

## CI/CD

GitHub Actionsで以下の自動化が設定されています：

- **Dockerビルド**: アプリのDockerイメージをビルド
- **自動テスト**: Playwrightを使ってUIテストを実行
- **スクリーンショット保存**: テスト結果のスクリーンショットをArtifactとして保存
- **失敗時Issue作成**: テスト失敗時に自動でGitHub Issueを作成

### ワークフロー実行条件

- `push` または `pull_request` イベント
- 手動実行 (`workflow_dispatch`)

## 技術スタック

- **Infrastructure as Code**: Terraform
- **Application**: Streamlit (Python)
- **Containerization**: Docker
- **Testing**: Playwright (Python)
- **CI/CD**: GitHub Actions

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。