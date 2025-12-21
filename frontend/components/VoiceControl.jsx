/**
 * VoiceControl Component - 音声コントロールコンポーネント
 *
 * Web Speech API を使用した音声認識・コマンド実行
 */

import React, { useState, useEffect, useRef } from 'react';
import './VoiceControl.css';

const VoiceControl = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [sessionId, setSessionId] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);

  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);

  useEffect(() => {
    // Web Speech API サポートチェック
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false);
      setError('お使いのブラウザは音声認識に対応していません');
      return;
    }

    // セッションID生成
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);

    // Speech Recognition 初期化
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'ja-JP';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log('Voice recognition started');
      setIsListening(true);
      setError('');
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcriptPart;
        } else {
          interim += transcriptPart;
        }
      }

      setInterimTranscript(interim);

      if (final) {
        setTranscript(final);
        processCommand(final);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setError(`音声認識エラー: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      console.log('Voice recognition ended');
      setIsListening(false);
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  const processCommand = async (command) => {
    try {
      setError('');

      // コマンド履歴に追加
      const historyEntry = {
        timestamp: new Date().toISOString(),
        command,
        response: ''
      };

      // API にコマンド送信
      const response = await fetch('/api/v1/voice/generic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          command: command,
          language: 'ja-JP'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const speechText = data.speech || 'コマンドを実行しました';
      setResponse(speechText);

      historyEntry.response = speechText;
      setCommandHistory(prev => [historyEntry, ...prev].slice(0, 10));

      // 音声で応答
      speak(speechText);

    } catch (err) {
      console.error('Command processing error:', err);
      setError(`コマンド処理エラー: ${err.message}`);
    }
  };

  const speak = (text) => {
    if (!synthRef.current) return;

    // 既存の発話を停止
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // 日本語音声を選択
    const voices = synthRef.current.getVoices();
    const japaneseVoice = voices.find(voice => voice.lang === 'ja-JP');
    if (japaneseVoice) {
      utterance.voice = japaneseVoice;
    }

    utterance.onend = () => {
      console.log('Speech finished');
    };

    utterance.onerror = (event) => {
      console.error('Speech error:', event);
    };

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
    }
  };

  const clearHistory = () => {
    setCommandHistory([]);
    setTranscript('');
    setInterimTranscript('');
    setResponse('');
    setError('');
  };

  if (!isSupported) {
    return (
      <div className="voice-control voice-control--unsupported">
        <div className="voice-control__error">
          <p>お使いのブラウザは音声認識に対応していません</p>
          <p className="voice-control__error-hint">
            Chrome、Edge、Safari の最新版をお試しください
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-control">
      <div className="voice-control__header">
        <h2 className="voice-control__title">音声コントロール</h2>
        <button
          className="voice-control__clear-btn"
          onClick={clearHistory}
          title="履歴をクリア"
        >
          クリア
        </button>
      </div>

      <div className="voice-control__main">
        {/* マイクボタン */}
        <button
          className={`voice-control__mic-btn ${isListening ? 'voice-control__mic-btn--active' : ''}`}
          onClick={toggleListening}
          title={isListening ? '音声認識を停止' : '音声認識を開始'}
        >
          <svg
            className="voice-control__mic-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
          <span className="voice-control__mic-label">
            {isListening ? '認識中...' : 'タップして話す'}
          </span>
        </button>

        {/* 認識中テキスト */}
        {(transcript || interimTranscript) && (
          <div className="voice-control__transcript">
            <div className="voice-control__transcript-label">認識テキスト:</div>
            <div className="voice-control__transcript-text">
              {transcript && <span className="voice-control__transcript-final">{transcript}</span>}
              {interimTranscript && (
                <span className="voice-control__transcript-interim">{interimTranscript}</span>
              )}
            </div>
          </div>
        )}

        {/* 応答テキスト */}
        {response && (
          <div className="voice-control__response">
            <div className="voice-control__response-label">応答:</div>
            <div className="voice-control__response-text">{response}</div>
            <button
              className="voice-control__stop-btn"
              onClick={stopSpeaking}
              title="音声を停止"
            >
              停止
            </button>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="voice-control__error">
            {error}
          </div>
        )}

        {/* 使い方ヒント */}
        <div className="voice-control__hints">
          <h3 className="voice-control__hints-title">使い方</h3>
          <ul className="voice-control__hints-list">
            <li>「カレーのレシピ」- レシピを検索</li>
            <li>「次」- 次の手順へ</li>
            <li>「前」- 前の手順に戻る</li>
            <li>「もう一度」- 同じ手順を繰り返す</li>
            <li>「材料」- 材料リストを読み上げ</li>
            <li>「タイマー5分」- タイマーを設定</li>
            <li>「ヘルプ」- 使い方を表示</li>
          </ul>
        </div>
      </div>

      {/* コマンド履歴 */}
      {commandHistory.length > 0 && (
        <div className="voice-control__history">
          <h3 className="voice-control__history-title">履歴</h3>
          <div className="voice-control__history-list">
            {commandHistory.map((entry, index) => (
              <div key={index} className="voice-control__history-item">
                <div className="voice-control__history-time">
                  {new Date(entry.timestamp).toLocaleTimeString('ja-JP')}
                </div>
                <div className="voice-control__history-command">
                  <strong>コマンド:</strong> {entry.command}
                </div>
                <div className="voice-control__history-response">
                  <strong>応答:</strong> {entry.response}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceControl;
