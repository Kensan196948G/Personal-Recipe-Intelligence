/**
 * VoiceAssistant Component
 * 音声アシスタントUIコンポーネント
 */

import React, { useState, useEffect, useRef } from 'react';

const VoiceAssistant = ({ recipe, onStepChange, onSearch }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);
  const [volume, setVolume] = useState(1.0);
  const [rate, setRate] = useState(1.0);
  const [showCommands, setShowCommands] = useState(false);

  const speechServiceRef = useRef(null);
  const ttsServiceRef = useRef(null);
  const commandHandlerRef = useRef(null);

  useEffect(() => {
    // サービス初期化
    if (typeof window !== 'undefined') {
      const SpeechService = window.SpeechService;
      const TTSService = window.TTSService;
      const VoiceCommandHandler = window.VoiceCommandHandler;

      if (!SpeechService || !TTSService || !VoiceCommandHandler) {
        setIsSupported(false);
        return;
      }

      speechServiceRef.current = new SpeechService();
      ttsServiceRef.current = new TTSService();
      commandHandlerRef.current = new VoiceCommandHandler(
        speechServiceRef.current,
        ttsServiceRef.current
      );

      // サポートチェック
      if (!speechServiceRef.current.isSupported() || !ttsServiceRef.current.isSupported()) {
        setIsSupported(false);
        return;
      }

      // コールバック設定
      speechServiceRef.current.onStart(() => {
        setIsListening(true);
        setError(null);
      });

      speechServiceRef.current.onEnd(() => {
        setIsListening(false);
      });

      speechServiceRef.current.onError((errorData) => {
        setError(errorData.message);
        setIsListening(false);
      });

      speechServiceRef.current.onResult((results) => {
        const finalResults = results.filter(r => r.isFinal);
        const interimResults = results.filter(r => !r.isFinal);

        if (finalResults.length > 0) {
          const finalText = finalResults[0].transcript;
          setTranscript(finalText);
          setInterimTranscript('');

          // コマンド実行
          commandHandlerRef.current.executeCommand(finalText);
        }

        if (interimResults.length > 0) {
          setInterimTranscript(interimResults[0].transcript);
        }
      });

      ttsServiceRef.current.onStart(() => {
        setIsSpeaking(true);
      });

      ttsServiceRef.current.onEnd(() => {
        setIsSpeaking(false);
      });

      // カスタムイベントリスナー
      window.addEventListener('voiceStepChange', handleStepChange);
      window.addEventListener('voiceSearch', handleSearch);
      window.addEventListener('voiceHelp', handleHelp);

      return () => {
        window.removeEventListener('voiceStepChange', handleStepChange);
        window.removeEventListener('voiceSearch', handleSearch);
        window.removeEventListener('voiceHelp', handleHelp);

        if (speechServiceRef.current) {
          speechServiceRef.current.abort();
        }
        if (ttsServiceRef.current) {
          ttsServiceRef.current.cancel();
        }
      };
    }
  }, []);

  useEffect(() => {
    // レシピ変更時
    if (recipe && commandHandlerRef.current) {
      commandHandlerRef.current.setRecipe(recipe);
    }
  }, [recipe]);

  useEffect(() => {
    // 音量変更
    if (ttsServiceRef.current) {
      ttsServiceRef.current.setVolume(volume);
    }
  }, [volume]);

  useEffect(() => {
    // 速度変更
    if (ttsServiceRef.current) {
      ttsServiceRef.current.setRate(rate);
    }
  }, [rate]);

  const handleStepChange = (event) => {
    if (onStepChange) {
      onStepChange(event.detail.stepIndex);
    }
  };

  const handleSearch = (event) => {
    if (onSearch) {
      onSearch(event.detail.keyword);
    }
  };

  const handleHelp = () => {
    setShowCommands(true);
  };

  const toggleListening = () => {
    if (isListening) {
      speechServiceRef.current.stop();
    } else {
      const started = speechServiceRef.current.start();
      if (!started) {
        setError('音声認識を開始できませんでした');
      }
    }
  };

  const stopSpeaking = () => {
    if (ttsServiceRef.current) {
      ttsServiceRef.current.cancel();
    }
  };

  const pauseSpeaking = () => {
    if (ttsServiceRef.current) {
      ttsServiceRef.current.pause();
    }
  };

  const resumeSpeaking = () => {
    if (ttsServiceRef.current) {
      ttsServiceRef.current.resume();
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-assistant-unsupported">
        <p>お使いのブラウザは音声機能に対応していません</p>
        <p>Chrome、Edge、Safariの最新版をご利用ください</p>
      </div>
    );
  }

  const availableCommands = commandHandlerRef.current
    ? commandHandlerRef.current.getAvailableCommands()
    : [];

  return (
    <div className="voice-assistant">
      <div className="voice-assistant-header">
        <h3>音声アシスタント</h3>
        <button
          className="help-button"
          onClick={() => setShowCommands(!showCommands)}
          title="コマンド一覧"
        >
          ?
        </button>
      </div>

      <div className="voice-controls">
        <button
          className={`voice-button ${isListening ? 'listening' : ''}`}
          onClick={toggleListening}
          disabled={isSpeaking}
        >
          <span className="mic-icon">{isListening ? '🔴' : '🎤'}</span>
          {isListening ? '音声認識中...' : '音声入力'}
        </button>

        <div className="tts-controls">
          <button
            onClick={pauseSpeaking}
            disabled={!isSpeaking}
            title="一時停止"
          >
            ⏸
          </button>
          <button
            onClick={resumeSpeaking}
            disabled={!isSpeaking}
            title="再開"
          >
            ▶
          </button>
          <button
            onClick={stopSpeaking}
            disabled={!isSpeaking}
            title="停止"
          >
            ⏹
          </button>
        </div>
      </div>

      {(transcript || interimTranscript) && (
        <div className="transcript-display">
          <div className="transcript-label">認識結果:</div>
          <div className="transcript-text">
            {transcript}
            {interimTranscript && (
              <span className="interim-text">{interimTranscript}</span>
            )}
          </div>
        </div>
      )}

      {isSpeaking && (
        <div className="speaking-indicator">
          <span className="speaker-icon">🔊</span>
          読み上げ中...
        </div>
      )}

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠</span>
          {error}
        </div>
      )}

      <div className="voice-settings">
        <div className="setting-row">
          <label>音量:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
          />
          <span>{Math.round(volume * 100)}%</span>
        </div>

        <div className="setting-row">
          <label>速度:</label>
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            value={rate}
            onChange={(e) => setRate(parseFloat(e.target.value))}
          />
          <span>{rate.toFixed(1)}x</span>
        </div>
      </div>

      {showCommands && (
        <div className="commands-list">
          <h4>利用可能なコマンド</h4>
          <ul>
            {availableCommands.map((cmd, index) => (
              <li key={index}>
                <strong>{cmd.patterns.join(', ')}</strong>
                <p>{cmd.description}</p>
              </li>
            ))}
          </ul>
          <button onClick={() => setShowCommands(false)}>閉じる</button>
        </div>
      )}

      <style jsx>{`
        .voice-assistant {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 16px;
          margin: 16px 0;
        }

        .voice-assistant-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .voice-assistant-header h3 {
          margin: 0;
          font-size: 18px;
        }

        .help-button {
          background: #007bff;
          color: white;
          border: none;
          border-radius: 50%;
          width: 28px;
          height: 28px;
          cursor: pointer;
          font-weight: bold;
        }

        .voice-assistant-unsupported {
          background: #fff3cd;
          border: 1px solid #ffc107;
          border-radius: 8px;
          padding: 16px;
          text-align: center;
        }

        .voice-controls {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .voice-button {
          flex: 1;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 12px 24px;
          font-size: 16px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: background 0.3s;
        }

        .voice-button:hover:not(:disabled) {
          background: #218838;
        }

        .voice-button:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .voice-button.listening {
          background: #dc3545;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }

        .mic-icon {
          font-size: 20px;
        }

        .tts-controls {
          display: flex;
          gap: 8px;
        }

        .tts-controls button {
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 12px 16px;
          cursor: pointer;
          font-size: 16px;
        }

        .tts-controls button:hover:not(:disabled) {
          background: #5a6268;
        }

        .tts-controls button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .transcript-display {
          background: white;
          border: 1px solid #ced4da;
          border-radius: 6px;
          padding: 12px;
          margin-bottom: 12px;
        }

        .transcript-label {
          font-weight: bold;
          margin-bottom: 4px;
          color: #495057;
        }

        .transcript-text {
          color: #212529;
        }

        .interim-text {
          color: #6c757d;
          font-style: italic;
        }

        .speaking-indicator {
          background: #d1ecf1;
          border: 1px solid #bee5eb;
          border-radius: 6px;
          padding: 8px 12px;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .speaker-icon {
          font-size: 18px;
        }

        .error-message {
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 6px;
          padding: 8px 12px;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
          color: #721c24;
        }

        .error-icon {
          font-size: 18px;
        }

        .voice-settings {
          background: white;
          border: 1px solid #ced4da;
          border-radius: 6px;
          padding: 12px;
        }

        .setting-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 8px;
        }

        .setting-row:last-child {
          margin-bottom: 0;
        }

        .setting-row label {
          min-width: 50px;
          font-weight: 500;
        }

        .setting-row input[type="range"] {
          flex: 1;
        }

        .setting-row span {
          min-width: 50px;
          text-align: right;
        }

        .commands-list {
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 24px;
          max-width: 500px;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          z-index: 1000;
        }

        .commands-list h4 {
          margin-top: 0;
          margin-bottom: 16px;
        }

        .commands-list ul {
          list-style: none;
          padding: 0;
          margin: 0 0 16px 0;
        }

        .commands-list li {
          border-bottom: 1px solid #e9ecef;
          padding: 12px 0;
        }

        .commands-list li:last-child {
          border-bottom: none;
        }

        .commands-list strong {
          color: #007bff;
        }

        .commands-list p {
          margin: 4px 0 0 0;
          color: #6c757d;
          font-size: 14px;
        }

        .commands-list button {
          width: 100%;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 10px;
          cursor: pointer;
        }

        .commands-list button:hover {
          background: #5a6268;
        }
      `}</style>
    </div>
  );
};

export default VoiceAssistant;
