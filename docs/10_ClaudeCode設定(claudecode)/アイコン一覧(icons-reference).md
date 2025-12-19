# アイコン一覧 (Icons Reference)

Personal Recipe Intelligence プロジェクトで使用するアイコン一覧です。

## SubAgent アイコン（9種類）

| アイコン | Agent名 | 役割 |
|:------:|---------|------|
| 🎯 | PlannerAgent | タスク分解・優先度割当の司令塔 |
| 🔧 | DevAPIAgent | FastAPI/Python コード自動生成 |
| 🎨 | DevUIAgent | Svelte WebUI 自動生成 |
| 🌐 | ScraperAgent | Webレシピ抽出（DOM解析） |
| 📷 | OcrAgent | 画像からテキスト抽出 |
| 🌍 | TranslationAgent | DeepL APIで海外レシピ日本語化 |
| 🧹 | CleanerAgent | 材料・手順の正規化・単位変換 |
| 🧪 | QaAgent | pytest/bun test 自動生成 |
| 📝 | WriterAgent | ドキュメント自動生成 |

## Hooks アイコン（5種類）

| アイコン | Hook名 | 役割 |
|:------:|--------|------|
| 🔌 | mcp-manager.js | MCP同時起動制御、待機キュー管理 |
| 📬 | on-task-created.js | タスク生成時にSubAgentへ自動振り分け |
| 👁 | on-file-changed.js | ファイル変更時に関連Agentへ通知 |
| ⛓ | on-agent-result.js | Agent完了時の連鎖実行 |
| 📡 | on-mcp-event.js | MCPイベント処理 |

## MCP アイコン（3種類）

| アイコン | MCP名 | 役割 |
|:------:|-------|------|
| 📚 | context7 | ライブラリドキュメント取得 |
| 🧠 | memory | セッション間の情報永続化 |
| 🖥 | chrome-devtools | ブラウザ操作・DOM検査 |

## 使用方法

### 設定ファイルでの参照

SubAgent設定ファイル（`.claude/agents/*.json`）では `icon` フィールドで参照:

```json
{
  "name": "PlannerAgent",
  "icon": "🎯",
  ...
}
```

Hooks設定ファイル（`.claude/hooks/*.js`）ではJSDocコメントで参照:

```javascript
/**
 * 🔌 MCP Manager
 * @icon 🔌
 */
```

---

更新日: 2025-12-19
