# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- CLAUDE.md development rules
- Basic directory structure
- SubAgents configuration (9 agents)
- Hooks configuration (4 hooks)
- Development phase documentation

## [0.2.0] - 2025-12-12

### Added
- 海外レシピ収集機能（Spoonacular API + DeepL翻訳）の完全統合
- データベース自動初期化機能（アプリ起動時）
- レシピ収集後の自動リスト更新機能

### Changed
- レシピ一覧の表示順を新しい順（ID降順）に変更
- ページあたり表示件数を20件から10件に変更
- Vite プロキシ設定をLAN IPアドレス対応に更新

### Fixed
- collector routerがapp.pyに未登録だった問題を修正
- rate_limiter headers_enabled互換性問題を修正
- WebUIボタンが機能しない問題を修正（APIレスポンス形式の不一致）
- データベーステーブル未作成エラーを修正

## [0.1.0] - 2024-12-11

### Added
- Project initialization
- Backend structure (FastAPI)
- Frontend structure (Svelte)
- Database schema design
- API endpoint definitions
- ClaudeCode integration settings
