/**
 * Speech Recognition Service
 * Web Speech API を使用した音声認識サービス
 */

class SpeechService {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.onResultCallback = null;
    this.onErrorCallback = null;
    this.onStartCallback = null;
    this.onEndCallback = null;
    this.language = 'ja-JP';

    this.initRecognition();
  }

  /**
   * Web Speech API の初期化
   */
  initRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Web Speech API is not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();

    // 認識設定
    this.recognition.lang = this.language;
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 3;

    // イベントリスナー設定
    this.recognition.onstart = () => {
      this.isListening = true;
      if (this.onStartCallback) {
        this.onStartCallback();
      }
    };

    this.recognition.onresult = (event) => {
      const results = [];

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        const confidence = result[0].confidence;
        const isFinal = result.isFinal;

        results.push({
          transcript: transcript.trim(),
          confidence: confidence,
          isFinal: isFinal
        });
      }

      if (this.onResultCallback) {
        this.onResultCallback(results);
      }
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      this.isListening = false;

      if (this.onErrorCallback) {
        this.onErrorCallback({
          error: event.error,
          message: this.getErrorMessage(event.error)
        });
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (this.onEndCallback) {
        this.onEndCallback();
      }
    };
  }

  /**
   * エラーメッセージの取得
   */
  getErrorMessage(error) {
    const errorMessages = {
      'no-speech': '音声が検出されませんでした',
      'audio-capture': 'マイクにアクセスできません',
      'not-allowed': 'マイクの使用が許可されていません',
      'network': 'ネットワークエラーが発生しました',
      'aborted': '音声認識が中断されました'
    };

    return errorMessages[error] || '音声認識エラーが発生しました';
  }

  /**
   * 音声認識開始
   */
  start() {
    if (!this.recognition) {
      console.error('Speech recognition is not supported');
      return false;
    }

    if (this.isListening) {
      console.warn('Speech recognition is already running');
      return false;
    }

    try {
      this.recognition.start();
      return true;
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      return false;
    }
  }

  /**
   * 音声認識停止
   */
  stop() {
    if (!this.recognition || !this.isListening) {
      return;
    }

    try {
      this.recognition.stop();
    } catch (error) {
      console.error('Failed to stop speech recognition:', error);
    }
  }

  /**
   * 音声認識中断
   */
  abort() {
    if (!this.recognition) {
      return;
    }

    try {
      this.recognition.abort();
      this.isListening = false;
    } catch (error) {
      console.error('Failed to abort speech recognition:', error);
    }
  }

  /**
   * 言語設定
   */
  setLanguage(lang) {
    this.language = lang;
    if (this.recognition) {
      this.recognition.lang = lang;
    }
  }

  /**
   * コールバック設定
   */
  onResult(callback) {
    this.onResultCallback = callback;
  }

  onError(callback) {
    this.onErrorCallback = callback;
  }

  onStart(callback) {
    this.onStartCallback = callback;
  }

  onEnd(callback) {
    this.onEndCallback = callback;
  }

  /**
   * サポート確認
   */
  isSupported() {
    return this.recognition !== null;
  }

  /**
   * リスニング状態確認
   */
  getListeningStatus() {
    return this.isListening;
  }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SpeechService;
} else {
  window.SpeechService = SpeechService;
}
