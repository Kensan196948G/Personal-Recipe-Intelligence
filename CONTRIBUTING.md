# コントリビューションガイド / Contributing Guide

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます！

## 🤝 貢献方法

### Issue の作成

バグや機能リクエストを見つけた場合：

1. 既存のissueを確認して、重複していないか確認してください
2. 適切なissueテンプレートを使用してください：
   - 🐛 Bug Report
   - ✨ Feature Request
   - 🔧 Maintenance Task

### Pull Request の作成

1. **フォークとクローン**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Personal-Recipe-Intelligence.git
   cd Personal-Recipe-Intelligence
   ```

2. **ブランチの作成**
   ```bash
   git checkout -b feature/your-feature-name
   # または
   git checkout -b fix/your-bug-fix
   ```

3. **変更の実施**
   - コードを変更する
   - 必要に応じてテストを追加する
   - ドキュメントを更新する

4. **コミット**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   コミットメッセージの形式：
   - `feat:` 新機能
   - `fix:` バグ修正
   - `docs:` ドキュメントのみの変更
   - `style:` コードの意味に影響しない変更（空白、フォーマットなど）
   - `refactor:` リファクタリング
   - `test:` テストの追加または修正
   - `chore:` ビルドプロセスやツールの変更

5. **プッシュとPR作成**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   GitHubでPull Requestを作成してください。PRテンプレートに従って記入してください。

## 🔍 コードレビュープロセス

1. **自動チェック**: PRを作成すると、以下が自動的に実行されます：
   - コード品質チェック
   - セキュリティスキャン
   - Markdownバリデーション
   - 自動ラベリング

2. **レビュー**: メンテナーがコードをレビューします

3. **フィードバック対応**: 必要に応じて変更を加えてください

4. **マージ**: 承認されたらマージされます

## 📋 ガイドライン

### コーディング規約

- **Python**: PEP 8に従う
- **JavaScript/TypeScript**: StandardまたはESLintの推奨設定に従う
- コードは読みやすく、保守しやすいものにする
- 適切なコメントを追加する

### コミット規約

- 意味のある、説明的なコミットメッセージを書く
- 1つのコミットで1つの変更を行う
- 英語または日本語でコミットメッセージを書く

### テスト

- 新機能には必ずテストを追加する
- バグ修正には再現テストを追加する
- すべてのテストが通ることを確認する

## 🔒 セキュリティ

セキュリティ上の問題を発見した場合は、公開のissueではなく、メンテナーに直接連絡してください。

## 🎯 優先事項

以下のようなコントリビューションを歓迎します：

- バグ修正
- ドキュメントの改善
- テストカバレッジの向上
- パフォーマンスの改善
- 新機能（事前にissueで議論してください）

## 📞 サポート

質問がある場合は、issueを作成してください。

## 🙏 謝辞

すべてのコントリビューターに感謝します！
