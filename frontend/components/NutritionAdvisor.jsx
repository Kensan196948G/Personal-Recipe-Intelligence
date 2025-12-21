import React, { useState, useEffect, useRef } from 'react';
import './NutritionAdvisor.css';

const NutritionAdvisor = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [quickActions, setQuickActions] = useState([]);
  const [dailyTip, setDailyTip] = useState(null);
  const [showTip, setShowTip] = useState(true);
  const messagesEndRef = useRef(null);

  const userId = 'default-user'; // 実装時は認証システムから取得

  useEffect(() => {
    loadChatHistory();
    loadQuickActions();
    loadDailyTip();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`/api/v1/advisor/history?user_id=${userId}&limit=20`);
      const result = await response.json();

      if (result.status === 'ok' && result.data.history) {
        setMessages(result.data.history);
      }
    } catch (error) {
      console.error('チャット履歴の読み込みエラー:', error);
    }
  };

  const loadQuickActions = async () => {
    try {
      const response = await fetch('/api/v1/advisor/quick-actions');
      const result = await response.json();

      if (result.status === 'ok') {
        setQuickActions(result.data);
      }
    } catch (error) {
      console.error('クイックアクションの読み込みエラー:', error);
    }
  };

  const loadDailyTip = async () => {
    try {
      const response = await fetch(`/api/v1/advisor/tips?user_id=${userId}`);
      const result = await response.json();

      if (result.status === 'ok') {
        setDailyTip(result.data);
      }
    } catch (error) {
      console.error('今日のワンポイントの読み込みエラー:', error);
    }
  };

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    setLoading(true);

    try {
      const response = await fetch('/api/v1/advisor/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: message,
        }),
      });

      const result = await response.json();

      if (result.status === 'ok') {
        // ユーザーメッセージを追加
        const userMessage = {
          id: Date.now().toString(),
          role: 'user',
          content: message,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage, result.data.message]);
        setInputMessage('');
      } else {
        alert('メッセージの送信に失敗しました');
      }
    } catch (error) {
      console.error('メッセージ送信エラー:', error);
      alert('エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleQuickAction = (action) => {
    sendMessage(action.message);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  const clearHistory = async () => {
    if (!confirm('チャット履歴を削除しますか？')) return;

    try {
      const response = await fetch(`/api/v1/advisor/history?user_id=${userId}`, {
        method: 'DELETE',
      });

      const result = await response.json();

      if (result.status === 'ok') {
        setMessages([]);
        alert('チャット履歴を削除しました');
      }
    } catch (error) {
      console.error('履歴削除エラー:', error);
      alert('エラーが発生しました');
    }
  };

  return (
    <div className="nutrition-advisor">
      <div className="advisor-header">
        <h2>栄養士AI相談</h2>
        <button onClick={clearHistory} className="btn-clear" title="履歴をクリア">
          🗑️ 履歴削除
        </button>
      </div>

      {/* 今日のワンポイント */}
      {dailyTip && showTip && (
        <div className="daily-tip">
          <div className="tip-header">
            <h3>💡 今日のワンポイント</h3>
            <button onClick={() => setShowTip(false)} className="btn-close">
              ✕
            </button>
          </div>
          <div className="tip-content">
            <h4>{dailyTip.title}</h4>
            <p>{dailyTip.content}</p>
            {dailyTip.tips && dailyTip.tips.length > 0 && (
              <ul className="tip-list">
                {dailyTip.tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* チャットエリア */}
      <div className="chat-area">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="welcome-icon">🥗</div>
            <h3>栄養士AIアドバイザーへようこそ！</h3>
            <p>栄養や食事に関するご質問をお気軽にどうぞ</p>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  {msg.tips && msg.tips.length > 0 && (
                    <div className="message-tips">
                      <strong>ポイント:</strong>
                      <ul>
                        {msg.tips.map((tip, index) => (
                          <li key={index}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                <div className="message-timestamp">{formatTimestamp(msg.timestamp)}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* クイックアクション */}
      {quickActions.length > 0 && messages.length === 0 && (
        <div className="quick-actions">
          <h4>よくある質問</h4>
          <div className="quick-action-buttons">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action)}
                className="quick-action-btn"
                disabled={loading}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 入力エリア */}
      <form onSubmit={handleSubmit} className="input-area">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="栄養や食事について質問してください..."
          disabled={loading}
          className="message-input"
          maxLength={1000}
        />
        <button type="submit" disabled={loading || !inputMessage.trim()} className="send-btn">
          {loading ? '送信中...' : '送信'}
        </button>
      </form>
    </div>
  );
};

export default NutritionAdvisor;
