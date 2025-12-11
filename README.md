# Personal-Recipe-Intelligence

国内外の料理レシピを定期的収集するシステム

## 🔧 メンテナンス / Maintenance

このリポジトリは定期的なメンテナンスを自動化しています。

### 自動化されているメンテナンスタスク

#### 📅 定期実行
- **毎週月曜日 10:00 (UTC)**: 依存関係チェック、セキュリティスキャン
- **毎週日曜日 00:00 (UTC)**: CodeQL セキュリティ分析
- **毎日 00:00 (UTC)**: 古いissueとPRの管理

#### 🔄 PR/プッシュ時の自動チェック
- コード品質チェック
- セキュリティ脆弱性スキャン
- Markdownファイルのバリデーション
- 自動ラベリング

#### 🤖 自動化ツール
- **Dependabot**: 依存関係の自動更新（毎週月曜日）
- **Stale Bot**: 60日間活動のないissueに対して通知、90日後に自動クローズ
- **Auto-labeler**: PRとissueの自動分類
- **CodeQL**: 継続的なセキュリティ分析

### ワークフロー

1. **scheduled-maintenance.yml**: 定期メンテナンスタスクの実行
2. **pr-validation.yml**: PRの検証とコード品質チェック
3. **codeql-analysis.yml**: セキュリティ脆弱性の自動検出
4. **stale.yml**: 古いissueとPRの管理
5. **auto-label.yml**: 自動ラベリング

### Issue テンプレート

以下のテンプレートを利用できます：
- 🐛 Bug Report: バグ報告
- ✨ Feature Request: 新機能のリクエスト
- 🔧 Maintenance Task: メンテナンスタスクの追跡

## 📝 コントリビューション

PRを作成する際は、自動的にPRテンプレートが適用されます。適切に記入してください。

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。
