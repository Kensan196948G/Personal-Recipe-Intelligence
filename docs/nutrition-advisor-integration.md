# 栄養士AI相談機能 統合ガイド

## FastAPI への統合

### 1. メインアプリケーションへのルーター追加

`backend/main.py` に以下を追加：

```python
from fastapi import FastAPI
from backend.api.routers import nutrition_advisor

app = FastAPI(title="Personal Recipe Intelligence API")

# 栄養士AIルーターを追加
app.include_router(nutrition_advisor.router)

@app.get("/")
async def root():
  return {"message": "Personal Recipe Intelligence API"}
```

### 2. 依存関係のインストール

```bash
# 必要なパッケージがインストールされていることを確認
pip install fastapi uvicorn pydantic
```

### 3. サーバーの起動

```bash
# 開発サーバー起動
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API ドキュメントの確認

ブラウザで以下のURLにアクセス：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## React フロントエンドへの統合

### 1. コンポーネントのインポート

```jsx
// App.jsx
import React from 'react';
import NutritionAdvisor from './components/NutritionAdvisor';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Personal Recipe Intelligence</h1>
      </header>

      <main className="app-main">
        <NutritionAdvisor />
      </main>
    </div>
  );
}

export default App;
```

### 2. ルーティング設定（React Router使用時）

```jsx
// App.jsx with routing
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NutritionAdvisor from './components/NutritionAdvisor';
import RecipeList from './components/RecipeList';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/recipes" element={<RecipeList />} />
        <Route path="/advisor" element={<NutritionAdvisor />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### 3. 環境変数の設定

`.env` ファイル:
```
REACT_APP_API_URL=http://localhost:8000
```

API呼び出しの更新:
```jsx
// NutritionAdvisor.jsx
const API_URL = process.env.REACT_APP_API_URL || '';

const sendMessage = async (message) => {
  const response = await fetch(`${API_URL}/api/v1/advisor/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message }),
  });
  // ...
};
```

## 認証システムとの統合

### 1. JWT トークン認証

```python
# backend/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
  credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
  """JWTトークンから現在のユーザーIDを取得"""
  token = credentials.credentials
  # トークンを検証してユーザーIDを取得
  user_id = verify_token(token)
  if not user_id:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid authentication credentials"
    )
  return user_id
```

```python
# backend/api/routers/nutrition_advisor.py
from backend.api.dependencies import get_current_user

@router.post("/chat", response_model=ChatMessageResponse)
async def chat_message(
  request: ChatMessageRequest,
  user_id: str = Depends(get_current_user)
):
  """認証付きチャット"""
  result = advisor_service.chat(
    user_id=user_id,
    message=request.message,
    context=request.context
  )
  return ChatMessageResponse(status="ok", data=result)
```

### 2. フロントエンドでのトークン管理

```jsx
// utils/api.js
export const apiClient = {
  async post(url, data) {
    const token = localStorage.getItem('authToken');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
};

// NutritionAdvisor.jsx
import { apiClient } from '../utils/api';

const sendMessage = async (message) => {
  const result = await apiClient.post('/api/v1/advisor/chat', {
    message: message
  });
  // user_idはバックエンドで自動取得
};
```

## データベースとの統合

### 1. SQLite への永続化

現在はJSONファイルベースですが、SQLiteに移行する場合：

```python
# backend/models/advisor_models.py
from sqlalchemy import Column, String, JSON, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatMessage(Base):
  __tablename__ = "chat_messages"

  id = Column(String, primary_key=True)
  user_id = Column(String, index=True)
  role = Column(String)
  content = Column(String)
  message_type = Column(String)
  tips = Column(JSON)
  context = Column(JSON)
  timestamp = Column(DateTime)

class UserProfile(Base):
  __tablename__ = "user_profiles"

  user_id = Column(String, primary_key=True)
  preferences = Column(JSON)
  restrictions = Column(JSON)
  goals = Column(JSON)
  created_at = Column(DateTime)
  updated_at = Column(DateTime)
```

### 2. サービスの更新

```python
# backend/services/nutrition_advisor_service.py
from sqlalchemy.orm import Session
from backend.models.advisor_models import ChatMessage, UserProfile

class NutritionAdvisorService:
  def __init__(self, db: Session):
    self.db = db

  def chat(self, user_id: str, message: str, context: dict = None):
    # データベースに保存
    chat_msg = ChatMessage(
      id=str(uuid4()),
      user_id=user_id,
      role="user",
      content=message,
      context=context,
      timestamp=datetime.now()
    )
    self.db.add(chat_msg)
    self.db.commit()

    # ... 応答生成 ...
```

## レシピ管理機能との統合

### 1. レシピデータからの栄養情報取得

```python
# backend/services/nutrition_advisor_service.py
from backend.services.recipe_service import RecipeService

class NutritionAdvisorService:
  def __init__(self, recipe_service: RecipeService):
    self.recipe_service = recipe_service

  def analyze_meal_from_recipes(self, user_id: str, recipe_ids: List[str]):
    """レシピIDから食事を分析"""
    meal_items = []

    for recipe_id in recipe_ids:
      recipe = self.recipe_service.get_recipe(recipe_id)
      if recipe:
        # レシピの栄養情報を取得
        nutrition = recipe.get("nutrition", {})
        meal_items.append({
          "recipe_id": recipe_id,
          "name": recipe.get("title"),
          "nutrition": nutrition
        })

    # 分析実行
    return self._analyze_nutrition(meal_items)
```

### 2. レシピ推薦との連携

```python
def recommend_recipes_for_goal(self, user_id: str, goal: str) -> List[Dict]:
  """目標に応じたレシピ推薦"""
  profile = self.get_user_profile(user_id)

  if goal == "weight_loss":
    # 低カロリーレシピを推薦
    filters = {
      "max_calories": 500,
      "high_protein": True,
      "low_fat": True
    }
  elif goal == "muscle_gain":
    # 高タンパク質レシピを推薦
    filters = {
      "high_protein": True,
      "min_protein": 30
    }

  return self.recipe_service.search_recipes(filters)
```

## WebSocket による リアルタイム通信

### 1. バックエンド実装

```python
# backend/api/websockets/advisor_ws.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class AdvisorConnectionManager:
  def __init__(self):
    self.active_connections: Dict[str, WebSocket] = {}

  async def connect(self, user_id: str, websocket: WebSocket):
    await websocket.accept()
    self.active_connections[user_id] = websocket

  def disconnect(self, user_id: str):
    if user_id in self.active_connections:
      del self.active_connections[user_id]

  async def send_message(self, user_id: str, message: dict):
    if user_id in self.active_connections:
      await self.active_connections[user_id].send_json(message)

manager = AdvisorConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
  await manager.connect(user_id, websocket)
  try:
    while True:
      data = await websocket.receive_json()
      # メッセージ処理
      result = advisor_service.chat(
        user_id=user_id,
        message=data["message"]
      )
      await manager.send_message(user_id, result)
  except WebSocketDisconnect:
    manager.disconnect(user_id)
```

### 2. フロントエンド実装

```jsx
// hooks/useWebSocketAdvisor.js
import { useEffect, useState } from 'react';

export const useWebSocketAdvisor = (userId) => {
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket(
      `ws://localhost:8000/api/v1/advisor/ws/${userId}`
    );

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data.message]);
    };

    setWs(websocket);

    return () => websocket.close();
  }, [userId]);

  const sendMessage = (message) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ message }));
    }
  };

  return { messages, sendMessage };
};
```

## モバイルアプリへの統合

### React Native での使用

```jsx
// NutritionAdvisorScreen.js
import React from 'react';
import { View, ScrollView, TextInput, Button, Text } from 'react-native';

const NutritionAdvisorScreen = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    const response = await fetch('http://api.example.com/api/v1/advisor/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: 'mobile-user',
        message: message
      })
    });
    const result = await response.json();
    setMessages([...messages, result.data.message]);
    setMessage('');
  };

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        {messages.map((msg, index) => (
          <Text key={index}>{msg.content}</Text>
        ))}
      </ScrollView>
      <TextInput
        value={message}
        onChangeText={setMessage}
        placeholder="メッセージを入力..."
      />
      <Button title="送信" onPress={sendMessage} />
    </View>
  );
};
```

## テスト環境のセットアップ

### 1. バックエンドテスト

```bash
# テスト実行
pytest backend/tests/test_nutrition_advisor_service.py -v

# カバレッジ測定
pytest backend/tests/test_nutrition_advisor_service.py --cov=backend/services/nutrition_advisor_service
```

### 2. フロントエンドテスト

```bash
# Reactコンポーネントテスト
npm test -- NutritionAdvisor.test.jsx

# E2Eテスト（Cypress使用）
npx cypress run --spec "cypress/e2e/nutrition_advisor.cy.js"
```

### 3. 統合テスト

```python
# tests/integration/test_advisor_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_chat_endpoint():
  response = client.post(
    "/api/v1/advisor/chat",
    json={
      "user_id": "test-user",
      "message": "こんにちは"
    }
  )
  assert response.status_code == 200
  assert response.json()["status"] == "ok"
```

## パフォーマンス最適化

### 1. キャッシング

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_daily_tip_cached(date: str):
  """日付ベースでキャッシュされたワンポイント"""
  return advisor_service.get_daily_tip()
```

### 2. 非同期処理

```python
import asyncio

async def analyze_meal_async(user_id: str, meal_data: dict):
  """非同期食事分析"""
  loop = asyncio.get_event_loop()
  return await loop.run_in_executor(
    None,
    advisor_service.analyze_meal,
    user_id,
    meal_data
  )
```

## デプロイメント

### Docker コンテナ化

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/pri.db
```

## トラブルシューティング

### よくある問題と解決策

1. **CORS エラー**
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
     CORSMiddleware,
     allow_origins=["http://localhost:3000"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
   )
   ```

2. **パフォーマンス問題**
   - チャット履歴を定期的にクリア
   - データベースインデックスの追加
   - レスポンスキャッシング

3. **データ整合性**
   - トランザクション管理の実装
   - バックアップの自動化

## まとめ

この統合ガイドに従うことで、栄養士AI相談機能を既存のアプリケーションにスムーズに統合できます。必要に応じてカスタマイズし、プロジェクトの要件に合わせて拡張してください。
