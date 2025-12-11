# 栄養士AI相談機能 ガイド

## 概要

栄養士AI相談機能は、ルールベースのチャットボットシステムで、ユーザーの栄養や食事に関する質問に回答し、パーソナライズされたアドバイスを提供します。

## 主な機能

### 1. インタラクティブチャット

- 自然言語での質問応答
- パターンマッチングによる応答生成
- コンテキストを考慮した回答
- チャット履歴の保存

### 2. 食事分析

- 栄養バランスの自動評価
- スコアリング（0〜100点）
- 改善アドバイスの提供
- 食事タイプ別の最適化

### 3. 食事プラン提案

- カロリー目標に基づいた献立提案
- 1日の食事配分（朝・昼・夜・間食）
- 目標に応じたカスタマイズ
- 水分補給アドバイス

### 4. パーソナライゼーション

- ユーザープロファイル管理
- 目標設定（減量、筋肉増強等）
- 制限事項対応（アレルギー、糖尿病等）
- 個別最適化されたアドバイス

### 5. 今日のワンポイント

- 日替わり栄養アドバイス
- カテゴリ別の知識提供
- 実践的なTips

## API エンドポイント

### チャット機能

#### POST /api/v1/advisor/chat

チャットメッセージを送信

**リクエスト:**
```json
{
  "user_id": "user-123",
  "message": "タンパク質について教えてください",
  "context": {}
}
```

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "message": {
      "id": "msg-456",
      "role": "assistant",
      "content": "タンパク質は体を作る重要な栄養素です...",
      "type": "protein",
      "tips": [
        "動物性と植物性のタンパク質をバランスよく摂取しましょう",
        "プロテインパウダーに頼りすぎず、食事から摂ることを優先しましょう"
      ],
      "timestamp": "2025-12-11T10:30:00Z"
    },
    "conversation_id": "user-123",
    "quick_actions": [...]
  }
}
```

#### GET /api/v1/advisor/history

チャット履歴を取得

**パラメータ:**
- `user_id`: ユーザーID（必須）
- `limit`: 取得件数（デフォルト: 50）
- `offset`: オフセット（デフォルト: 0）

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "history": [...],
    "total": 120,
    "limit": 50,
    "offset": 0
  }
}
```

#### DELETE /api/v1/advisor/history

チャット履歴をクリア

**パラメータ:**
- `user_id`: ユーザーID（必須）

### 食事分析

#### POST /api/v1/advisor/analyze

食事を分析してアドバイスを提供

**リクエスト:**
```json
{
  "user_id": "user-123",
  "meal_type": "lunch",
  "items": [
    {
      "recipe_id": "recipe-001",
      "servings": 1
    },
    {
      "recipe_id": "recipe-002",
      "servings": 0.5
    }
  ]
}
```

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "timestamp": "2025-12-11T12:00:00Z",
    "meal_type": "lunch",
    "items": [...],
    "nutrition": {
      "calories": 650,
      "protein": 35,
      "carbohydrates": 70,
      "fat": 20
    },
    "advice": [
      "バランスの良い食事です！この調子で続けましょう。"
    ],
    "score": 85
  }
}
```

### ワンポイントアドバイス

#### GET /api/v1/advisor/tips

今日のワンポイントアドバイスを取得

**パラメータ:**
- `user_id`: ユーザーID（オプション）

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "date": "2025-12-11",
    "category": "protein",
    "title": "タンパク質の重要性",
    "content": "タンパク質は体を作る重要な栄養素です...",
    "tips": [
      "動物性と植物性のタンパク質をバランスよく摂取しましょう",
      "プロテインパウダーに頼りすぎず、食事から摂ることを優先しましょう"
    ]
  }
}
```

### 食事プラン

#### POST /api/v1/advisor/meal-plan

食事プランを提案

**リクエスト:**
```json
{
  "user_id": "user-123",
  "target_calories": 2000,
  "goals": ["weight_loss"],
  "restrictions": []
}
```

**レスポンス:**
```json
{
  "status": "ok",
  "data": {
    "date": "2025-12-11",
    "target_calories": 2000,
    "target_protein": 75,
    "target_carbs": 275,
    "target_fat": 66.7,
    "meals": {
      "breakfast": {
        "target_calories": 500,
        "suggestions": [...],
        "tips": [...]
      },
      "lunch": {...},
      "dinner": {...},
      "snacks": {...}
    },
    "hydration": {
      "target_water": 2000,
      "tips": [...]
    },
    "general_advice": [...]
  }
}
```

### ユーザープロファイル

#### GET /api/v1/advisor/profile

ユーザープロファイルを取得

**パラメータ:**
- `user_id`: ユーザーID（必須）

#### PUT /api/v1/advisor/profile

ユーザープロファイルを更新

**パラメータ:**
- `user_id`: ユーザーID（必須）

**リクエスト:**
```json
{
  "preferences": {
    "favorite_foods": ["fish", "vegetables"]
  },
  "restrictions": ["allergy"],
  "goals": ["weight_loss", "muscle_gain"]
}
```

### クイックアクション

#### GET /api/v1/advisor/quick-actions

よくある質問のクイックアクション一覧を取得

**レスポンス:**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "weight_loss",
      "label": "ダイエットのコツは？",
      "message": "ダイエットについて教えてください"
    },
    ...
  ]
}
```

## 知識ベースカテゴリ

システムは以下のカテゴリの質問に対応しています：

1. **挨拶** (`greetings`)
2. **タンパク質** (`protein`)
3. **炭水化物** (`carbohydrates`)
4. **脂質** (`fat`)
5. **ビタミン** (`vitamins`)
6. **ミネラル** (`minerals`)
7. **減量** (`weight_loss`)
8. **増量** (`weight_gain`)
9. **アレルギー** (`allergies`)
10. **糖尿病** (`diabetes`)
11. **水分補給** (`hydration`)
12. **食事時間** (`meal_timing`)
13. **運動** (`exercise`)
14. **睡眠** (`sleep`)
15. **ストレス** (`stress`)
16. **妊娠・授乳** (`pregnancy`)
17. **高齢者** (`elderly`)

## パーソナライゼーション

### 目標設定

ユーザーは以下の目標を設定できます：

- `weight_loss`: 減量
- `muscle_gain`: 筋肉増強
- `health_maintenance`: 健康維持

### 制限事項

以下の制限事項に対応：

- `allergy`: 食物アレルギー
- `diabetes`: 糖尿病
- `hypertension`: 高血圧
- `pregnancy`: 妊娠中
- `lactose_intolerant`: 乳糖不耐症

## 食事分析スコアリング

食事は以下の基準でスコアリングされます（0〜100点）：

### 基本スコア: 70点

### 加点要素
- カロリーが適切範囲内: +10点
- タンパク質が20g以上: +10点
- 炭水化物比率が適切（50〜65%）: +5点
- 脂質比率が適切（20〜30%）: +5点

### 減点要素
- カロリーが推奨範囲外: -5点
- タンパク質不足（15g未満）: -10点
- 炭水化物比率が高すぎる（70%以上）: -5点
- 脂質比率が高すぎる（35%以上）: -5点

## フロントエンド統合例

### React コンポーネント使用例

```jsx
import NutritionAdvisor from './components/NutritionAdvisor';

function App() {
  return (
    <div className="app">
      <NutritionAdvisor />
    </div>
  );
}
```

### カスタムフック例

```javascript
// useNutritionAdvisor.js
import { useState, useEffect } from 'react';

export const useNutritionAdvisor = (userId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (message) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/advisor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message }),
      });
      const result = await response.json();
      if (result.status === 'ok') {
        setMessages(prev => [...prev, result.data.message]);
      }
    } finally {
      setLoading(false);
    }
  };

  return { messages, sendMessage, loading };
};
```

## ベストプラクティス

### 1. ユーザープロファイルの活用

```python
# プロファイルを設定
advisor_service.update_user_profile(
  user_id="user-123",
  profile_updates={
    "goals": ["weight_loss"],
    "restrictions": ["diabetes"],
  }
)

# パーソナライズされた応答を取得
result = advisor_service.chat(
  user_id="user-123",
  message="炭水化物について教えてください"
)
# → 糖尿病に関する注意事項が含まれる
```

### 2. 食事分析の活用

```python
# 食事データを準備
meal_data = {
  "meal_type": "lunch",
  "items": [
    {"recipe_id": "recipe-001", "servings": 1},
  ]
}

# 分析実行
analysis = advisor_service.analyze_meal(
  user_id="user-123",
  meal_data=meal_data
)

print(f"スコア: {analysis['score']}点")
print(f"アドバイス: {', '.join(analysis['advice'])}")
```

### 3. チャット履歴の管理

```python
# 履歴取得（最新20件）
history = advisor_service.get_chat_history(
  user_id="user-123",
  limit=20
)

# 古い履歴をクリア
if history["total"] > 100:
  advisor_service.clear_chat_history(user_id="user-123")
```

## トラブルシューティング

### 応答が期待通りでない場合

1. 知識ベースのパターンを確認
2. ユーザープロファイルが正しく設定されているか確認
3. チャット履歴が適切に保存されているか確認

### パフォーマンスの問題

1. チャット履歴を定期的にクリア（最新100件まで自動保持）
2. 食事分析履歴も定期的にクリア（最新30件まで自動保持）

### データの永続化

- チャット履歴: `data/advisor_chat_history.json`
- ユーザープロファイル: `data/advisor_user_profiles.json`

バックアップを定期的に取得することを推奨します。

## 今後の拡張予定

1. **機械学習モデルの統合**
   - より高度な質問応答
   - 感情分析
   - 意図理解の向上

2. **多言語対応**
   - 英語、中国語などへの対応

3. **音声入力対応**
   - 音声認識との連携

4. **画像認識との連携**
   - 食事画像から自動分析

5. **外部APIとの連携**
   - 栄養データベースとの統合
   - レシピ検索APIとの連携

## セキュリティとプライバシー

- ユーザーデータは暗号化して保存することを推奨
- 個人の健康情報は慎重に取り扱う
- GDPRなどの規制に準拠
- アクセスログを適切に管理

## ライセンス

MIT License
