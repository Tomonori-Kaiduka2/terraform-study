# 1. プロバイダー設定
# ローカルファイルを操作するための標準的な設定です
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# 2. 変数の定義
# ここで「単一の名前」ではなく「リスト（名前の集合）」を受け取るように定義します
variable "agent_list" {
  description = "量産したいAIエージェント名のリスト"
  type        = list(string)
  # デフォルト値を設定しておくと、tfvarsが空でもエラーになりません
  default     = ["default-agent-01"]
}

# 3. リソースの量産（for_each）
# 変数 agent_list に含まれる名前の数だけ、以下の処理を繰り返します
resource "local_file" "agent_reports" {
  # listをset（重複なし集合）に変換して、繰り返し処理のキーにします
  for_each = toset(var.agent_list)

  # パスを動的に生成（例: ./Agent-Alpha/doc/report.txt）
  # each.value にはリスト内の個別の名前（Agent-Alphaなど）が入ります
  filename = "${path.module}/${each.value}/doc/report.txt"
  
  content  = <<EOT
=========================================
AI Agent Infrastructure Report
=========================================
Agent Identifier : ${each.value}
Provisioning Time: ${timestamp()}
System Status    : Operational

Description:
This environment has been automatically 
provisioned as a base for AI Agent logic.
=========================================
EOT
}

# 4. （オプション）各エージェント専用のスクリプトフォルダも同時に作成
resource "local_file" "agent_init" {
  for_each = toset(var.agent_list)
  
  filename = "${path.module}/${each.value}/scripts/initialize.ps1"
  content  = "# Initialization script for ${each.value}"
}