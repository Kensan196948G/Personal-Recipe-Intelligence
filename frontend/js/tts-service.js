/**
 * Text-to-Speech Service
 * Web Speech API を使用した音声合成サービス
 */

class TTSService {
  constructor() {
    this.synth = window.speechSynthesis;
    this.voice = null;
    this.volume = 1.0;
    this.rate = 1.0;
    this.pitch = 1.0;
    this.language = 'ja-JP';
    this.isSpeaking = false;

    this.onStartCallback = null;
    this.onEndCallback = null;
    this.onPauseCallback = null;
    this.onResumeCallback = null;

    this.loadVoices();
  }

  /**
   * 音声リストの読み込み
   */
  loadVoices() {
    const voices = this.synth.getVoices();
    if (voices.length > 0) {
      this.selectJapaneseVoice(voices);
    } else {
      // Chrome では voices が遅延読み込みされる
      this.synth.onvoiceschanged = () => {
        const loadedVoices = this.synth.getVoices();
        this.selectJapaneseVoice(loadedVoices);
      };
    }
  }

  /**
   * 日本語音声の選択
   */
  selectJapaneseVoice(voices) {
    // 日本語音声を優先的に選択
    const japaneseVoice = voices.find(voice =>
      voice.lang.startsWith('ja') || voice.lang === this.language
    );

    if (japaneseVoice) {
      this.voice = japaneseVoice;
    } else {
      // デフォルト音声を使用
      this.voice = voices[0];
    }
  }

  /**
   * テキスト読み上げ
   */
  speak(text, options = {}) {
    if (!text || text.trim() === '') {
      console.warn('Empty text provided for TTS');
      return false;
    }

    // 既存の読み上げを停止
    if (this.isSpeaking) {
      this.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);

    // パラメータ設定
    utterance.voice = this.voice;
    utterance.volume = options.volume !== undefined ? options.volume : this.volume;
    utterance.rate = options.rate !== undefined ? options.rate : this.rate;
    utterance.pitch = options.pitch !== undefined ? options.pitch : this.pitch;
    utterance.lang = options.lang || this.language;

    // イベントリスナー設定
    utterance.onstart = () => {
      this.isSpeaking = true;
      if (this.onStartCallback) {
        this.onStartCallback();
      }
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      if (this.onEndCallback) {
        this.onEndCallback();
      }
    };

    utterance.onerror = (event) => {
      console.error('TTS error:', event.error);
      this.isSpeaking = false;
    };

    utterance.onpause = () => {
      if (this.onPauseCallback) {
        this.onPauseCallback();
      }
    };

    utterance.onresume = () => {
      if (this.onResumeCallback) {
        this.onResumeCallback();
      }
    };

    // 読み上げ開始
    try {
      this.synth.speak(utterance);
      return true;
    } catch (error) {
      console.error('Failed to start TTS:', error);
      return false;
    }
  }

  /**
   * レシピ全体の読み上げ
   */
  speakRecipe(recipe) {
    if (!recipe) {
      return false;
    }

    let text = `レシピ名: ${recipe.title}。`;

    if (recipe.ingredients && recipe.ingredients.length > 0) {
      text += '材料は、';
      recipe.ingredients.forEach((ingredient, index) => {
        text += `${ingredient.name} ${ingredient.amount}`;
        if (index < recipe.ingredients.length - 1) {
          text += '、';
        }
      });
      text += '。';
    }

    if (recipe.steps && recipe.steps.length > 0) {
      text += '手順は、';
      recipe.steps.forEach((step, index) => {
        text += `${index + 1}、${step}。`;
      });
    }

    return this.speak(text);
  }

  /**
   * レシピ手順の読み上げ
   */
  speakStep(stepNumber, stepText) {
    const text = `手順${stepNumber}、${stepText}`;
    return this.speak(text);
  }

  /**
   * 材料リストの読み上げ
   */
  speakIngredients(ingredients) {
    if (!ingredients || ingredients.length === 0) {
      return false;
    }

    let text = '材料は、';
    ingredients.forEach((ingredient, index) => {
      text += `${ingredient.name} ${ingredient.amount}`;
      if (index < ingredients.length - 1) {
        text += '、';
      }
    });
    text += '、以上です。';

    return this.speak(text);
  }

  /**
   * 一時停止
   */
  pause() {
    if (this.synth.speaking && !this.synth.paused) {
      this.synth.pause();
    }
  }

  /**
   * 再開
   */
  resume() {
    if (this.synth.paused) {
      this.synth.resume();
    }
  }

  /**
   * キャンセル（停止）
   */
  cancel() {
    this.synth.cancel();
    this.isSpeaking = false;
  }

  /**
   * 音量設定
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
  }

  /**
   * 速度設定
   */
  setRate(rate) {
    this.rate = Math.max(0.1, Math.min(10, rate));
  }

  /**
   * ピッチ設定
   */
  setPitch(pitch) {
    this.pitch = Math.max(0, Math.min(2, pitch));
  }

  /**
   * 言語設定
   */
  setLanguage(lang) {
    this.language = lang;
    this.loadVoices();
  }

  /**
   * 音声設定
   */
  setVoice(voiceName) {
    const voices = this.synth.getVoices();
    const selectedVoice = voices.find(voice => voice.name === voiceName);
    if (selectedVoice) {
      this.voice = selectedVoice;
    }
  }

  /**
   * 利用可能な音声リストを取得
   */
  getVoices() {
    return this.synth.getVoices();
  }

  /**
   * コールバック設定
   */
  onStart(callback) {
    this.onStartCallback = callback;
  }

  onEnd(callback) {
    this.onEndCallback = callback;
  }

  onPause(callback) {
    this.onPauseCallback = callback;
  }

  onResume(callback) {
    this.onResumeCallback = callback;
  }

  /**
   * サポート確認
   */
  isSupported() {
    return 'speechSynthesis' in window;
  }

  /**
   * 読み上げ状態確認
   */
  getSpeakingStatus() {
    return this.isSpeaking;
  }

  /**
   * 一時停止状態確認
   */
  isPaused() {
    return this.synth.paused;
  }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TTSService;
} else {
  window.TTSService = TTSService;
}
