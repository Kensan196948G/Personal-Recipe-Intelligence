# レポート機能セットアップガイド

## 概要

Personal Recipe Intelligence のレポート機能は、週次・月次・カスタム期間のレポート生成、PDF/HTML/Markdown出力、レポート履歴管理を提供します。

## 依存関係のインストール

### 1. Python パッケージ

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend
pip install reportlab==4.0.9
```

### 2. 日本語フォント（PDF生成に必要）

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install fonts-noto-cjk

# フォントキャッシュの更新
fc-cache -fv
```

## ディレクトリ構成

```
backend/
  services/
    report_service.py          # レポート生成サービス
  api/
    routers/
      report.py                # レポートAPIルーター
  tests/
    test_report_service.py     # レポートサービステスト

frontend/
  components/
    ReportViewer.jsx           # レポートビューアコンポーネント

data/
  reports/                     # レポート保存ディレクトリ
    history.json               # レポート履歴ファイル
```

## API エンドポイント

### 週次レポート取得

```bash
GET /api/v1/report/weekly?user_id=user_001&week_offset=0
```

パラメータ:
- `user_id`: ユーザーID（必須）
- `week_offset`: 週オフセット（0=今週、-1=先週）

### 月次レポート取得

```bash
GET /api/v1/report/monthly?user_id=user_001&month_offset=0
```

パラメータ:
- `user_id`: ユーザーID（必須）
- `month_offset`: 月オフセット（0=今月、-1=先月）

### カスタム期間レポート生成

```bash
POST /api/v1/report/custom
Content-Type: application/json

{
  "user_id": "user_001",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### PDF生成とダウンロード

```bash
GET /api/v1/report/generate/pdf?user_id=user_001&report_type=weekly&week_offset=0
```

パラメータ:
- `user_id`: ユーザーID（必須）
- `report_type`: レポートタイプ（weekly/monthly/custom）
- `week_offset`: 週オフセット（weeklyの場合）
- `month_offset`: 月オフセット（monthlyの場合）
- `start_date`: 開始日（customの場合必須）
- `end_date`: 終了日（customの場合必須）

### HTML レポート生成

```bash
GET /api/v1/report/generate/html?user_id=user_001&report_type=weekly&week_offset=0
```

### Markdown レポート生成

```bash
GET /api/v1/report/generate/markdown?user_id=user_001&report_type=weekly&week_offset=0
```

### レポート履歴取得

```bash
GET /api/v1/report/history?user_id=user_001&limit=20
```

パラメータ:
- `user_id`: ユーザーID（必須）
- `limit`: 取得件数（デフォルト: 20）

### レポートID検索

```bash
GET /api/v1/report/{report_id}
```

## 使用例

### Python（サービス直接利用）

```python
from backend.services.report_service import ReportService
from backend.services.nutrition_service import NutritionService
from backend.services.goal_service import GoalService

# サービス初期化
nutrition_service = NutritionService()
goal_service = GoalService()
report_service = ReportService(
    nutrition_service=nutrition_service,
    goal_service=goal_service
)

# 週次レポート生成
report_data = report_service.generate_weekly_report(
    user_id="user_001",
    week_offset=0
)

# PDF生成
pdf_bytes = report_service.generate_pdf(report_data)

# ファイルに保存
with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)

# HTML生成
html_content = report_service.generate_html_report(report_data)

# Markdown生成
markdown_content = report_service.generate_markdown_report(report_data)
```

### cURLでのAPI利用

```bash
# 週次レポート取得
curl -X GET "http://localhost:8001/api/v1/report/weekly?user_id=user_001&week_offset=0"

# PDF ダウンロード
curl -X GET "http://localhost:8001/api/v1/report/generate/pdf?user_id=user_001&report_type=weekly&week_offset=0" \
  -o report.pdf

# カスタムレポート生成
curl -X POST "http://localhost:8001/api/v1/report/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  }'

# レポート履歴取得
curl -X GET "http://localhost:8001/api/v1/report/history?user_id=user_001&limit=10"
```

### React コンポーネント利用

```jsx
import ReportViewer from './components/ReportViewer';

function App() {
  return (
    <div>
      <ReportViewer userId="user_001" />
    </div>
  );
}
```

## レポート内容

各レポートには以下の情報が含まれます：

### 栄養サマリー
- 総カロリー / 1日平均カロリー
- 総タンパク質 / 1日平均タンパク質
- 総脂質 / 1日平均脂質
- 総炭水化物 / 1日平均炭水化物

### 支出サマリー
- 総支出
- 1日平均支出
- 食事回数
- 1食平均支出

### 目標サマリー
- 総目標数
- 完了数
- 進行中数
- 達成率
- 目標詳細（上位5件）

### アドバイス
- 栄養バランスに基づくアドバイス
- 支出に関するアドバイス
- 目標達成に関するアドバイス

## テスト

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend

# レポートサービステスト実行
pytest tests/test_report_service.py -v

# カバレッジ付きテスト
pytest tests/test_report_service.py --cov=services.report_service --cov-report=html
```

## トラブルシューティング

### 日本語フォントが表示されない

PDFに日本語が正しく表示されない場合：

1. フォントがインストールされているか確認
```bash
fc-list | grep -i noto
```

2. フォントパスを確認
```bash
ls -la /usr/share/fonts/opentype/noto/
ls -la /usr/share/fonts/truetype/noto/
```

3. 必要に応じて手動でフォントを配置
```bash
# フォントディレクトリ作成
sudo mkdir -p /usr/share/fonts/truetype/noto

# フォントダウンロード（例）
wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansCJKjp-hinted.zip
unzip NotoSansCJKjp-hinted.zip -d /usr/share/fonts/truetype/noto/

# キャッシュ更新
fc-cache -fv
```

### reportlab インストールエラー

```bash
# 依存関係インストール
sudo apt-get install python3-dev libfreetype6-dev

# 再インストール
pip install --upgrade --force-reinstall reportlab
```

### レポート履歴が保存されない

データディレクトリのパーミッションを確認：

```bash
chmod -R 755 data/reports/
```

## パフォーマンス

- レポート生成: 1秒以内
- PDF生成: 2-3秒（フォントロード含む）
- HTML生成: 1秒以内
- Markdown生成: 1秒以内

大量のデータがある場合、期間を適切に設定することで高速化できます。

## セキュリティ

- レポートデータはユーザーIDで分離
- 履歴は最新100件のみ保持
- 機密情報（パスワード、トークン）はマスキング
- ファイル出力先は data/ ディレクトリに限定

## ライセンス

reportlab: BSD License

## 参考リンク

- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
