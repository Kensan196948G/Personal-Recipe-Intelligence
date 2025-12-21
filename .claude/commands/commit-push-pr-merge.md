# Git コミット → プッシュ → PR作成 → マージ 自動化コマンド

このコマンドは以下の一連の操作を自動実行します：
1. 変更をステージング
2. コミット作成
3. リモートへプッシュ
4. Pull Request 作成
5. PR をマージ

## 実行手順

### Step 1: 現在の状態を確認
```bash
git status
git diff --stat
```

### Step 2: 変更をステージング
未追跡ファイルと変更ファイルをすべてステージングしてください。
```bash
git add -A
```

### Step 3: コミットメッセージを作成
変更内容を分析し、Conventional Commits 形式でコミットメッセージを作成してください。

形式:
- `feat(scope): 新機能の説明`
- `fix(scope): バグ修正の説明`
- `chore(scope): 雑務の説明`
- `refactor(scope): リファクタリングの説明`
- `docs(scope): ドキュメント更新の説明`

コミット例:
```bash
git commit -m "$(cat <<'EOF'
feat(api): レシピ検索機能を追加

- 全文検索エンドポイントを実装
- 材料による絞り込み機能を追加
- ページネーション対応

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 4: ブランチ戦略を決定
- 直接 `main` にプッシュする場合: Step 5a へ
- 新しいブランチで PR を作成する場合: Step 5b へ

### Step 5a: main に直接プッシュ
```bash
git push origin main
```
→ 完了

### Step 5b: 新しいブランチを作成してプッシュ
```bash
# ブランチ名は変更内容に応じて適切に命名
git checkout -b feature/適切な名前
git push -u origin feature/適切な名前
```

### Step 6: Pull Request を作成
```bash
gh pr create --title "PRタイトル" --body "$(cat <<'EOF'
## Summary
- 変更点1
- 変更点2

## Test plan
- [ ] テスト項目1
- [ ] テスト項目2

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 7: PR をマージ
```bash
# マージ前にCIが通っているか確認
gh pr checks

# マージ実行
gh pr merge --merge --delete-branch
```

### Step 8: main に戻る
```bash
git checkout main
git pull origin main
```

## 注意事項
- マージ前に必ず CI/CD のステータスを確認すること
- 破壊的変更がある場合は慎重にレビューすること
- コンフリクトが発生した場合は手動で解決すること

## 引数（オプション）
- `$ARGUMENTS`: コミットメッセージまたは操作の説明を指定可能
