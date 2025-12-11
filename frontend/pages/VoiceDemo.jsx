/**
 * VoiceDemo Page - 音声アシスタントデモページ
 */

import React from 'react';
import VoiceControl from '../components/VoiceControl';
import './VoiceDemo.css';

const VoiceDemo = () => {
  return (
    <div className="voice-demo">
      <div className="voice-demo__container">
        <header className="voice-demo__header">
          <h1 className="voice-demo__title">音声アシスタント</h1>
          <p className="voice-demo__subtitle">
            声でレシピを検索・操作できます
          </p>
        </header>

        <main className="voice-demo__main">
          <VoiceControl />

          <section className="voice-demo__info">
            <h2 className="voice-demo__info-title">対応デバイス</h2>
            <div className="voice-demo__devices">
              <div className="voice-demo__device-card">
                <div className="voice-demo__device-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="5" y="2" width="14" height="20" rx="2" />
                    <path d="M12 18h.01" />
                  </svg>
                </div>
                <h3>Webブラウザ</h3>
                <p>Chrome, Edge, Safari で音声認識に対応</p>
              </div>

              <div className="voice-demo__device-card">
                <div className="voice-demo__device-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                </div>
                <h3>Amazon Alexa</h3>
                <p>Alexa スキルとして利用可能</p>
              </div>

              <div className="voice-demo__device-card">
                <div className="voice-demo__device-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <h3>Google Assistant</h3>
                <p>Google Action として利用可能</p>
              </div>
            </div>
          </section>

          <section className="voice-demo__features">
            <h2 className="voice-demo__features-title">主な機能</h2>
            <div className="voice-demo__features-grid">
              <div className="voice-demo__feature">
                <div className="voice-demo__feature-icon">🔍</div>
                <h3>レシピ検索</h3>
                <p>「カレーのレシピ」と言うだけで検索できます</p>
              </div>

              <div className="voice-demo__feature">
                <div className="voice-demo__feature-icon">📖</div>
                <h3>手順読み上げ</h3>
                <p>「次」「前」で手順を進めたり戻したりできます</p>
              </div>

              <div className="voice-demo__feature">
                <div className="voice-demo__feature-icon">📝</div>
                <h3>材料リスト</h3>
                <p>「材料」と言えば必要な材料を読み上げます</p>
              </div>

              <div className="voice-demo__feature">
                <div className="voice-demo__feature-icon">⏱️</div>
                <h3>タイマー設定</h3>
                <p>「タイマー5分」で調理タイマーをセットできます</p>
              </div>

              <div className="voice-demo__feature">
                <div className="voice-demo__feature-icon">🔁</div>
                <h3>繰り返し再生</h3>
                <p>「もう一度」で同じ手順を繰り返せます</p>
              </div>

              <div className="voice-demo__feature">
                <div className="voice-demo__feature-icon">❓</div>
                <h3>ヘルプ機能</h3>
                <p>「ヘルプ」で使い方を確認できます</p>
              </div>
            </div>
          </section>

          <section className="voice-demo__tips">
            <h2 className="voice-demo__tips-title">使い方のコツ</h2>
            <ul className="voice-demo__tips-list">
              <li>
                <strong>静かな環境で:</strong>
                周囲の騒音が少ない場所で使うと認識精度が上がります
              </li>
              <li>
                <strong>はっきりと発音:</strong>
                ゆっくりはっきり話すと正確に認識されます
              </li>
              <li>
                <strong>短い文章で:</strong>
                長い文章より短いコマンドの方が認識されやすいです
              </li>
              <li>
                <strong>マイクの許可:</strong>
                初回使用時はブラウザのマイク許可が必要です
              </li>
              <li>
                <strong>HTTPS環境:</strong>
                音声認識は HTTPS 環境でのみ動作します
              </li>
            </ul>
          </section>

          <section className="voice-demo__examples">
            <h2 className="voice-demo__examples-title">コマンド例</h2>
            <div className="voice-demo__examples-grid">
              <div className="voice-demo__example-category">
                <h3>検索</h3>
                <ul>
                  <li>カレーのレシピ</li>
                  <li>パスタの作り方</li>
                  <li>簡単なデザート</li>
                </ul>
              </div>

              <div className="voice-demo__example-category">
                <h3>操作</h3>
                <ul>
                  <li>次</li>
                  <li>前</li>
                  <li>もう一度</li>
                  <li>キャンセル</li>
                </ul>
              </div>

              <div className="voice-demo__example-category">
                <h3>情報</h3>
                <ul>
                  <li>材料は？</li>
                  <li>何が必要？</li>
                  <li>作り方を教えて</li>
                </ul>
              </div>

              <div className="voice-demo__example-category">
                <h3>タイマー</h3>
                <ul>
                  <li>タイマー5分</li>
                  <li>10分タイマー</li>
                  <li>タイマーセット</li>
                </ul>
              </div>
            </div>
          </section>
        </main>

        <footer className="voice-demo__footer">
          <p className="voice-demo__footer-note">
            ※ 音声認識機能はブラウザとデバイスによってサポート状況が異なります
          </p>
        </footer>
      </div>
    </div>
  );
};

export default VoiceDemo;
