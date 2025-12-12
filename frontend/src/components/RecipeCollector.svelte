<script>
  import { onMount, onDestroy } from 'svelte';
  import { fetchRecipes } from '../stores/recipes.js';

  let status = null;
  let collecting = false;
  let collectResult = null;
  let error = null;
  let collectCount = 5;
  let tags = '';
  let refreshInterval;

  const API_BASE = '';

  async function fetchStatus() {
    try {
      const res = await fetch(`${API_BASE}/collector/status`);
      if (res.ok) {
        status = await res.json();
        error = null;
      } else {
        error = 'ステータス取得に失敗しました';
      }
    } catch (e) {
      error = `接続エラー: ${e.message}`;
    }
  }

  async function collectNow() {
    collecting = true;
    collectResult = null;
    error = null;

    try {
      const res = await fetch(`${API_BASE}/collector/collect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          count: collectCount,
          tags: tags || null,
        }),
      });

      if (res.ok) {
        collectResult = await res.json();
        await fetchStatus();
        // 収集後にレシピ一覧を更新
        await fetchRecipes();
      } else {
        const errData = await res.json().catch(() => ({}));
        error = errData.detail || '収集に失敗しました';
      }
    } catch (e) {
      error = `収集エラー: ${e.message}`;
    } finally {
      collecting = false;
    }
  }

  async function startScheduler() {
    try {
      const res = await fetch(`${API_BASE}/collector/start`, { method: 'POST' });
      if (res.ok) {
        await fetchStatus();
      }
    } catch (e) {
      error = `スケジューラー開始エラー: ${e.message}`;
    }
  }

  async function stopScheduler() {
    try {
      const res = await fetch(`${API_BASE}/collector/stop`, { method: 'POST' });
      if (res.ok) {
        await fetchStatus();
      }
    } catch (e) {
      error = `スケジューラー停止エラー: ${e.message}`;
    }
  }

  function formatDateTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  onMount(() => {
    fetchStatus();
    refreshInterval = setInterval(fetchStatus, 30000); // 30秒ごとに更新
  });

  onDestroy(() => {
    if (refreshInterval) clearInterval(refreshInterval);
  });
</script>

<div class="collector-container">
  <h2>
    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
    </svg>
    海外レシピ自動収集
  </h2>

  {#if error}
    <div class="error-message">
      <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {error}
    </div>
  {/if}

  {#if status}
    <div class="status-card">
      <h3>
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
        スケジューラー状態
      </h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="label">状態:</span>
          <span class={status.running ? 'value running' : 'value stopped'}>
            {status.running ? '実行中' : '停止中'}
          </span>
        </div>
        <div class="status-item">
          <span class="label">1日の収集数:</span>
          <span class="value">{status.daily_count}件</span>
        </div>
        <div class="status-item">
          <span class="label">収集時刻:</span>
          <span class="value">{status.collection_hour}:00</span>
        </div>
        <div class="status-item">
          <span class="label">前回収集:</span>
          <span class="value">{formatDateTime(status.last_collection)}</span>
        </div>
        <div class="status-item">
          <span class="label">次回収集:</span>
          <span class="value">{formatDateTime(status.next_collection)}</span>
        </div>
        <div class="status-item">
          <span class="label">APIキー:</span>
          <span class="value">
            Spoonacular: {status.api_keys_configured?.spoonacular ? '✓' : '✗'}
            / DeepL: {status.api_keys_configured?.deepl ? '✓' : '✗'}
          </span>
        </div>
      </div>

      <div class="scheduler-controls">
        {#if status.running}
          <button class="btn btn-danger" on:click={stopScheduler}>
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="6" y="4" width="4" height="16"/>
              <rect x="14" y="4" width="4" height="16"/>
            </svg>
            スケジューラー停止
          </button>
        {:else}
          <button class="btn btn-success" on:click={startScheduler}>
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            スケジューラー開始
          </button>
        {/if}
      </div>
    </div>
  {/if}

  <div class="manual-collect">
    <h3>
      <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      手動収集
    </h3>

    <div class="form-group">
      <label for="collectCount">収集件数:</label>
      <input
        type="number"
        id="collectCount"
        bind:value={collectCount}
        min="1"
        max="10"
      />
    </div>

    <div class="form-group">
      <label for="tags">カテゴリ (オプション):</label>
      <input
        type="text"
        id="tags"
        bind:value={tags}
        placeholder="例: デザート、肉料理、vegetarian"
      />
      <small>日本語・英語どちらでも入力可能。カンマ区切りで複数指定可。空欄でランダム取得。</small>
    </div>

    <button
      class="btn btn-primary"
      on:click={collectNow}
      disabled={collecting || !status?.api_keys_configured?.spoonacular || !status?.api_keys_configured?.deepl}
    >
      {#if collecting}
        <svg class="icon-sm spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="2" x2="12" y2="6"/>
          <line x1="12" y1="18" x2="12" y2="22"/>
          <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
          <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
          <line x1="2" y1="12" x2="6" y2="12"/>
          <line x1="18" y1="12" x2="22" y2="12"/>
          <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
          <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
        </svg>
        収集中...
      {:else}
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="16"/>
          <line x1="8" y1="12" x2="16" y2="12"/>
        </svg>
        今すぐ収集
      {/if}
    </button>

    {#if !status?.api_keys_configured?.spoonacular || !status?.api_keys_configured?.deepl}
      <p class="warning">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        APIキーが設定されていません。.envファイルを確認してください。
      </p>
    {/if}
  </div>

  {#if collectResult}
    <div class="result-card" class:success={collectResult.success} class:failure={!collectResult.success}>
      <h3>
        {#if collectResult.success}
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          収集完了
        {:else}
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          収集失敗
        {/if}
      </h3>

      {#if collectResult.success}
        <p>{collectResult.collected}件のレシピを収集しました。</p>
        {#if collectResult.recipes && collectResult.recipes.length > 0}
          <ul class="recipe-list">
            {#each collectResult.recipes as recipe}
              <li>
                <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                {recipe.title} (ID: {recipe.id})
              </li>
            {/each}
          </ul>
        {/if}
      {:else}
        <p class="error-text">{collectResult.error}</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .collector-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 1rem;
  }

  h2 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #333;
    margin-bottom: 1.5rem;
  }

  h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #444;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }

  .icon {
    width: 24px;
    height: 24px;
  }

  .icon-sm {
    width: 18px;
    height: 18px;
  }

  .icon-xs {
    width: 14px;
    height: 14px;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #fee;
    border: 1px solid #fcc;
    color: #c00;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .status-card,
  .manual-collect,
  .result-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .status-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .label {
    font-size: 0.85rem;
    color: #666;
  }

  .value {
    font-weight: 500;
    color: #333;
  }

  .value.running {
    color: #28a745;
  }

  .value.stopped {
    color: #dc3545;
  }

  .scheduler-controls {
    padding-top: 1rem;
    border-top: 1px solid #eee;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
    color: #444;
  }

  .form-group input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .form-group input:focus {
    outline: none;
    border-color: #0077aa;
    box-shadow: 0 0 0 2px rgba(0, 119, 170, 0.1);
  }

  .form-group small {
    display: block;
    margin-top: 0.25rem;
    color: #888;
    font-size: 0.85rem;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 6px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-primary {
    background: #0077aa;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #005580;
  }

  .btn-success {
    background: #28a745;
    color: white;
  }

  .btn-success:hover:not(:disabled) {
    background: #218838;
  }

  .btn-danger {
    background: #dc3545;
    color: white;
  }

  .btn-danger:hover:not(:disabled) {
    background: #c82333;
  }

  .warning {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 0.75rem;
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 6px;
    color: #856404;
    font-size: 0.9rem;
  }

  .result-card.success {
    background: #d4edda;
    border: 1px solid #c3e6cb;
  }

  .result-card.failure {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
  }

  .result-card h3 {
    color: inherit;
  }

  .result-card.success h3 {
    color: #155724;
  }

  .result-card.failure h3 {
    color: #721c24;
  }

  .recipe-list {
    list-style: none;
    padding: 0;
    margin: 1rem 0 0;
  }

  .recipe-list li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .error-text {
    color: #721c24;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
