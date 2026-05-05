# 1. ローカルファイルを扱うための「プロバイダー」設定
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# 2. 実際に作成するファイルの内容定義
resource "local_file" "hello" {
  filename = "${path.module}/hello_terraform.txt"
  content  = "こんにちは！Windowsのローカル環境でTerraformが動いています。"
}

# フォルダ構成を定義する
locals {
  folders = ["src", "docs", "tests", "scripts"]
}

# 各フォルダの中に「.gitkeep」というファイルを作る
# これにより、副次的にフォルダも作成されます
resource "local_file" "project_structure" {
  for_each = toset(local.folders)
  
  filename = "${path.module}/${each.value}/.gitkeep"
  content  = "Directory initialized by Terraform"
}

# 実行レポートの作成（前回の例）
resource "local_file" "report" {
  filename = "${path.module}/report.txt"
  content  = <<EOT
Terraform実行レポート
--------------------
管理対象：Windows 11 Local Environment
実行時刻: ${timestamp()}
作成フォルダ: ${join(", ", local.folders)}
EOT
}