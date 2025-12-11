/**
 * Voice Command Handler
 * 音声コマンドの解析と実行を担当
 */

class VoiceCommandHandler {
  constructor(speechService, ttsService) {
    this.speechService = speechService;
    this.ttsService = ttsService;
    this.currentRecipe = null;
    this.currentStepIndex = 0;
    this.commands = this.initCommands();
    this.timerIds = [];
  }

  /**
   * コマンド定義の初期化
   */
  initCommands() {
    return [
      // レシピナビゲーション
      {
        patterns: ['次の手順', '次', 'つぎ', 'ネクスト'],
        action: () => this.nextStep(),
        description: '次の手順へ進む'
      },
      {
        patterns: ['前の手順', '前', 'まえ', 'ひとつ前'],
        action: () => this.previousStep(),
        description: '前の手順に戻る'
      },
      {
        patterns: ['最初から', '初めから', 'はじめから', 'スタート'],
        action: () => this.firstStep(),
        description: '最初の手順から開始'
      },
      {
        patterns: ['もう一度', 'もう一回', 'リピート', '繰り返し'],
        action: () => this.repeatStep(),
        description: '現在の手順を繰り返す'
      },

      // 材料・情報
      {
        patterns: ['材料', '材料を教えて', '材料は', '材料読んで'],
        action: () => this.readIngredients(),
        description: '材料リストを読み上げる'
      },
      {
        patterns: ['レシピ名', 'タイトル', '料理名'],
        action: () => this.readTitle(),
        description: 'レシピ名を読み上げる'
      },
      {
        patterns: ['全部読んで', '全て読んで', '全部教えて'],
        action: () => this.readAll(),
        description: 'レシピ全体を読み上げる'
      },

      // タイマー
      {
        patterns: ['タイマー', 'タイマー設定', 'タイマーセット'],
        action: (transcript) => this.setTimer(transcript),
        description: 'タイマーを設定'
      },
      {
        patterns: ['タイマー停止', 'タイマーキャンセル'],
        action: () => this.cancelTimers(),
        description: 'タイマーをキャンセル'
      },

      // 制御
      {
        patterns: ['一時停止', 'ポーズ', '止めて'],
        action: () => this.pause(),
        description: '読み上げを一時停止'
      },
      {
        patterns: ['再開', '続き', '続けて'],
        action: () => this.resume(),
        description: '読み上げを再開'
      },
      {
        patterns: ['停止', 'ストップ', '黙れ', '静かに'],
        action: () => this.stop(),
        description: '読み上げを停止'
      },

      // 検索
      {
        patterns: ['検索', 'レシピ検索', '探して'],
        action: (transcript) => this.searchRecipe(transcript),
        description: 'レシピを検索'
      },

      // ヘルプ
      {
        patterns: ['ヘルプ', '使い方', 'コマンド一覧'],
        action: () => this.showHelp(),
        description: '使い方を表示'
      }
    ];
  }

  /**
   * 音声コマンドの解析
   */
  parseCommand(transcript) {
    const text = transcript.toLowerCase().trim();

    for (const command of this.commands) {
      for (const pattern of command.patterns) {
        if (text.includes(pattern.toLowerCase())) {
          return {
            command: command,
            transcript: transcript,
            matched: pattern
          };
        }
      }
    }

    return null;
  }

  /**
   * コマンド実行
   */
  executeCommand(transcript) {
    const parsedCommand = this.parseCommand(transcript);

    if (parsedCommand) {
      console.log(`Executing command: ${parsedCommand.matched}`);
      try {
        parsedCommand.command.action(transcript);
        return true;
      } catch (error) {
        console.error('Command execution error:', error);
        this.ttsService.speak('コマンドの実行中にエラーが発生しました');
        return false;
      }
    } else {
      console.log('No matching command found');
      this.ttsService.speak('コマンドが認識できませんでした');
      return false;
    }
  }

  /**
   * レシピ設定
   */
  setRecipe(recipe) {
    this.currentRecipe = recipe;
    this.currentStepIndex = 0;
  }

  /**
   * 次の手順
   */
  nextStep() {
    if (!this.currentRecipe || !this.currentRecipe.steps) {
      this.ttsService.speak('レシピが設定されていません');
      return;
    }

    if (this.currentStepIndex < this.currentRecipe.steps.length - 1) {
      this.currentStepIndex++;
      const step = this.currentRecipe.steps[this.currentStepIndex];
      this.ttsService.speakStep(this.currentStepIndex + 1, step);
      this.dispatchStepChange();
    } else {
      this.ttsService.speak('最後の手順です');
    }
  }

  /**
   * 前の手順
   */
  previousStep() {
    if (!this.currentRecipe || !this.currentRecipe.steps) {
      this.ttsService.speak('レシピが設定されていません');
      return;
    }

    if (this.currentStepIndex > 0) {
      this.currentStepIndex--;
      const step = this.currentRecipe.steps[this.currentStepIndex];
      this.ttsService.speakStep(this.currentStepIndex + 1, step);
      this.dispatchStepChange();
    } else {
      this.ttsService.speak('最初の手順です');
    }
  }

  /**
   * 最初の手順
   */
  firstStep() {
    if (!this.currentRecipe || !this.currentRecipe.steps) {
      this.ttsService.speak('レシピが設定されていません');
      return;
    }

    this.currentStepIndex = 0;
    const step = this.currentRecipe.steps[this.currentStepIndex];
    this.ttsService.speakStep(this.currentStepIndex + 1, step);
    this.dispatchStepChange();
  }

  /**
   * 手順繰り返し
   */
  repeatStep() {
    if (!this.currentRecipe || !this.currentRecipe.steps) {
      this.ttsService.speak('レシピが設定されていません');
      return;
    }

    const step = this.currentRecipe.steps[this.currentStepIndex];
    this.ttsService.speakStep(this.currentStepIndex + 1, step);
  }

  /**
   * 材料読み上げ
   */
  readIngredients() {
    if (!this.currentRecipe || !this.currentRecipe.ingredients) {
      this.ttsService.speak('材料情報がありません');
      return;
    }

    this.ttsService.speakIngredients(this.currentRecipe.ingredients);
  }

  /**
   * タイトル読み上げ
   */
  readTitle() {
    if (!this.currentRecipe || !this.currentRecipe.title) {
      this.ttsService.speak('レシピが設定されていません');
      return;
    }

    this.ttsService.speak(`レシピ名は、${this.currentRecipe.title}です`);
  }

  /**
   * レシピ全体読み上げ
   */
  readAll() {
    if (!this.currentRecipe) {
      this.ttsService.speak('レシピが設定されていません');
      return;
    }

    this.ttsService.speakRecipe(this.currentRecipe);
  }

  /**
   * タイマー設定
   */
  setTimer(transcript) {
    // 数値と単位を抽出
    const minuteMatch = transcript.match(/(\d+)\s*分/);
    const secondMatch = transcript.match(/(\d+)\s*秒/);

    let totalSeconds = 0;

    if (minuteMatch) {
      totalSeconds += parseInt(minuteMatch[1]) * 60;
    }

    if (secondMatch) {
      totalSeconds += parseInt(secondMatch[1]);
    }

    if (totalSeconds === 0) {
      this.ttsService.speak('タイマーの時間を認識できませんでした。例えば、3分タイマー、と言ってください');
      return;
    }

    this.ttsService.speak(`${totalSeconds}秒のタイマーを設定しました`);

    const timerId = setTimeout(() => {
      this.ttsService.speak('タイマーが終了しました');
      this.dispatchTimerEnd();
    }, totalSeconds * 1000);

    this.timerIds.push(timerId);
  }

  /**
   * タイマーキャンセル
   */
  cancelTimers() {
    this.timerIds.forEach(id => clearTimeout(id));
    this.timerIds = [];
    this.ttsService.speak('タイマーをキャンセルしました');
  }

  /**
   * 一時停止
   */
  pause() {
    this.ttsService.pause();
  }

  /**
   * 再開
   */
  resume() {
    this.ttsService.resume();
  }

  /**
   * 停止
   */
  stop() {
    this.ttsService.cancel();
  }

  /**
   * レシピ検索
   */
  searchRecipe(transcript) {
    // 「検索」以降のテキストを検索キーワードとして抽出
    const searchMatch = transcript.match(/検索\s*(.+)/i) ||
                        transcript.match(/探して\s*(.+)/i);

    if (searchMatch && searchMatch[1]) {
      const keyword = searchMatch[1].trim();
      this.ttsService.speak(`${keyword}を検索します`);
      this.dispatchSearch(keyword);
    } else {
      this.ttsService.speak('検索するキーワードを言ってください');
    }
  }

  /**
   * ヘルプ表示
   */
  showHelp() {
    const helpText = '音声コマンドは、次の手順、前の手順、材料を読んで、タイマー設定、などがあります';
    this.ttsService.speak(helpText);
    this.dispatchHelp();
  }

  /**
   * イベント発行
   */
  dispatchStepChange() {
    window.dispatchEvent(new CustomEvent('voiceStepChange', {
      detail: { stepIndex: this.currentStepIndex }
    }));
  }

  dispatchTimerEnd() {
    window.dispatchEvent(new CustomEvent('voiceTimerEnd'));
  }

  dispatchSearch(keyword) {
    window.dispatchEvent(new CustomEvent('voiceSearch', {
      detail: { keyword: keyword }
    }));
  }

  dispatchHelp() {
    window.dispatchEvent(new CustomEvent('voiceHelp'));
  }

  /**
   * 利用可能なコマンド一覧取得
   */
  getAvailableCommands() {
    return this.commands.map(cmd => ({
      patterns: cmd.patterns,
      description: cmd.description
    }));
  }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = VoiceCommandHandler;
} else {
  window.VoiceCommandHandler = VoiceCommandHandler;
}
