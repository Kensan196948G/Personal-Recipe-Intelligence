#!/bin/bash
#
# Personal Recipe Intelligence - バックアップユーティリティスクリプト
#
# 使用方法:
#   ./scripts/backup.sh create [backup_name]  - バックアップ作成
#   ./scripts/backup.sh list                  - バックアップ一覧表示
#   ./scripts/backup.sh restore <backup_id>   - バックアップからリストア
#   ./scripts/backup.sh delete <backup_id>    - バックアップ削除
#   ./scripts/backup.sh status                - バックアップ状態表示
#

set -e

# 設定
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
BACKUP_API="${API_BASE_URL}/api/v1/backup"

# 色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ヘルプ表示
show_help() {
  echo "Personal Recipe Intelligence - Backup Utility"
  echo ""
  echo "Usage:"
  echo "  $0 create [backup_name]    Create a new backup"
  echo "  $0 list                    List all backups"
  echo "  $0 restore <backup_id>     Restore from backup"
  echo "  $0 delete <backup_id>      Delete a backup"
  echo "  $0 status                  Show backup status"
  echo "  $0 help                    Show this help message"
  echo ""
  echo "Environment Variables:"
  echo "  API_BASE_URL               API base URL (default: http://localhost:8000)"
  echo ""
  exit 0
}

# バックアップ作成
create_backup() {
  local backup_name="${1:-}"

  echo -e "${GREEN}Creating backup...${NC}"

  if [ -z "$backup_name" ]; then
    response=$(curl -s -X POST "${BACKUP_API}/create" \
      -H "Content-Type: application/json" \
      -d '{}')
  else
    response=$(curl -s -X POST "${BACKUP_API}/create" \
      -H "Content-Type: application/json" \
      -d "{\"backup_name\": \"${backup_name}\"}")
  fi

  # レスポンス確認
  status=$(echo "$response" | jq -r '.status')
  if [ "$status" = "ok" ]; then
    backup_id=$(echo "$response" | jq -r '.data.backup_id')
    size_mb=$(echo "$response" | jq -r '.data.size_mb')
    echo -e "${GREEN}Backup created successfully!${NC}"
    echo "  Backup ID: $backup_id"
    echo "  Size: ${size_mb} MB"
  else
    error=$(echo "$response" | jq -r '.error // .detail')
    echo -e "${RED}Failed to create backup: ${error}${NC}"
    exit 1
  fi
}

# バックアップ一覧表示
list_backups() {
  echo -e "${GREEN}Listing backups...${NC}"

  response=$(curl -s -X GET "${BACKUP_API}/list")

  # レスポンス確認
  status=$(echo "$response" | jq -r '.status')
  if [ "$status" = "ok" ]; then
    count=$(echo "$response" | jq -r '.data | length')
    echo "Total backups: $count"
    echo ""
    echo "$response" | jq -r '.data[] | "ID: \(.backup_id)\n  Size: \(.size_mb) MB\n  Created: \(.created_at)\n  Compressed: \(.is_compressed)\n"'
  else
    error=$(echo "$response" | jq -r '.error // .detail')
    echo -e "${RED}Failed to list backups: ${error}${NC}"
    exit 1
  fi
}

# バックアップからリストア
restore_backup() {
  local backup_id="$1"

  if [ -z "$backup_id" ]; then
    echo -e "${RED}Error: backup_id is required${NC}"
    echo "Usage: $0 restore <backup_id>"
    exit 1
  fi

  echo -e "${YELLOW}WARNING: This will restore the database from backup.${NC}"
  echo -e "${YELLOW}Current database will be backed up as safety backup.${NC}"
  read -p "Are you sure? (yes/no): " confirm

  if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
  fi

  echo -e "${GREEN}Restoring from backup: ${backup_id}${NC}"

  response=$(curl -s -X POST "${BACKUP_API}/restore/${backup_id}")

  # レスポンス確認
  status=$(echo "$response" | jq -r '.status')
  if [ "$status" = "ok" ]; then
    message=$(echo "$response" | jq -r '.data.message')
    echo -e "${GREEN}${message}${NC}"
  else
    error=$(echo "$response" | jq -r '.error // .detail')
    echo -e "${RED}Failed to restore backup: ${error}${NC}"
    exit 1
  fi
}

# バックアップ削除
delete_backup() {
  local backup_id="$1"

  if [ -z "$backup_id" ]; then
    echo -e "${RED}Error: backup_id is required${NC}"
    echo "Usage: $0 delete <backup_id>"
    exit 1
  fi

  echo -e "${YELLOW}WARNING: This will permanently delete the backup.${NC}"
  read -p "Are you sure? (yes/no): " confirm

  if [ "$confirm" != "yes" ]; then
    echo "Delete cancelled."
    exit 0
  fi

  echo -e "${GREEN}Deleting backup: ${backup_id}${NC}"

  response=$(curl -s -X DELETE "${BACKUP_API}/${backup_id}")

  # レスポンス確認
  status=$(echo "$response" | jq -r '.status')
  if [ "$status" = "ok" ]; then
    message=$(echo "$response" | jq -r '.data.message')
    echo -e "${GREEN}${message}${NC}"
  else
    error=$(echo "$response" | jq -r '.error // .detail')
    echo -e "${RED}Failed to delete backup: ${error}${NC}"
    exit 1
  fi
}

# バックアップ状態表示
show_status() {
  echo -e "${GREEN}Backup status:${NC}"

  response=$(curl -s -X GET "${BACKUP_API}/status")

  # レスポンス確認
  status=$(echo "$response" | jq -r '.status')
  if [ "$status" = "ok" ]; then
    total_backups=$(echo "$response" | jq -r '.data.total_backups')
    total_size_mb=$(echo "$response" | jq -r '.data.total_size_mb')
    oldest=$(echo "$response" | jq -r '.data.oldest_backup // "N/A"')
    latest=$(echo "$response" | jq -r '.data.latest_backup // "N/A"')
    backup_dir=$(echo "$response" | jq -r '.data.backup_dir')

    echo "  Total backups: $total_backups"
    echo "  Total size: ${total_size_mb} MB"
    echo "  Oldest backup: $oldest"
    echo "  Latest backup: $latest"
    echo "  Backup directory: $backup_dir"
  else
    error=$(echo "$response" | jq -r '.error // .detail')
    echo -e "${RED}Failed to get status: ${error}${NC}"
    exit 1
  fi
}

# メイン処理
main() {
  # jq の存在確認
  if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install with: sudo apt-get install jq"
    exit 1
  fi

  # コマンド引数チェック
  if [ $# -eq 0 ]; then
    show_help
  fi

  command="$1"
  shift

  case "$command" in
    create)
      create_backup "$@"
      ;;
    list)
      list_backups
      ;;
    restore)
      restore_backup "$@"
      ;;
    delete)
      delete_backup "$@"
      ;;
    status)
      show_status
      ;;
    help|--help|-h)
      show_help
      ;;
    *)
      echo -e "${RED}Unknown command: $command${NC}"
      echo ""
      show_help
      ;;
  esac
}

main "$@"
