<script>
  import { createEventDispatcher } from 'svelte';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorAlert from './ErrorAlert.svelte';

  const dispatch = createEventDispatcher();

  let file = null;
  let loading = false;
  let error = null;
  let preview = null;
  let result = null;
  let skipDuplicates = true;
  let dragOver = false;

  async function handleFileSelect(event) {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      file = selectedFile;
      error = null;
      result = null;
      await loadPreview();
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    dragOver = false;
    const droppedFile = event.dataTransfer?.files?.[0];
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      file = droppedFile;
      error = null;
      result = null;
      loadPreview();
    } else {
      error = 'CSVファイルのみ対応しています';
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    dragOver = true;
  }

  function handleDragLeave() {
    dragOver = false;
  }

  async function loadPreview() {
    if (!file) return;

    loading = true;
    error = null;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/v1/import/csv/preview', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'プレビューの読み込みに失敗しました');
      }

      preview = data.data;
    } catch (e) {
      error = e.message;
      preview = null;
    } finally {
      loading = false;
    }
  }

  async function handleImport() {
    if (!file) return;

    loading = true;
    error = null;
    result = null;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `/api/v1/import/csv?skip_duplicates=${skipDuplicates}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'インポートに失敗しました');
      }

      result = data.data;

      if (result.summary.imported > 0) {
        dispatch('imported', result);
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function downloadTemplate() {
    try {
      const response = await fetch('/api/v1/import/csv/template');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'recipe_template.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (e) {
      error = 'テンプレートのダウンロードに失敗しました';
    }
  }

  function reset() {
    file = null;
    preview = null;
    result = null;
    error = null;
  }

  function handleBack() {
    dispatch('back');
  }
</script>

<div class="csv-import">
  <div class="header">
    <button class="btn-back" on:click={handleBack}>
      &larr; 戻る
    </button>
    <h2>CSVインポート</h2>
  </div>

  {#if error}
    <ErrorAlert message={error} on:close={() => (error = null)} />
  {/if}

  {#if !result}
    <div class="upload-section">
      <div
        class="drop-zone"
        class:drag-over={dragOver}
        on:drop={handleDrop}
        on:dragover={handleDragOver}
        on:dragleave={handleDragLeave}
      >
        <div class="drop-content">
          <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round"/>
            <polyline points="17 8 12 3 7 8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <p>CSVファイルをドラッグ&ドロップ</p>
          <p class="or">または</p>
          <label class="file-input-label">
            ファイルを選択
            <input
              type="file"
              accept=".csv"
              on:change={handleFileSelect}
              class="file-input"
            />
          </label>
        </div>
      </div>

      <div class="template-section">
        <button class="btn-template-download" on:click={downloadTemplate}>
          <svg class="download-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round"/>
            <polyline points="7 10 12 15 17 10" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3" stroke-width="2" stroke-linecap="round"/>
          </svg>
          サンプルCSVをダウンロード（10件のレシピ例）
        </button>
        <p class="template-hint">
          カレーライス、肉じゃが、親子丼など10種類のサンプルレシピが含まれています
        </p>
      </div>

      {#if file}
        <div class="file-info">
          <span class="file-name">{file.name}</span>
          <span class="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
          <button class="btn-clear" on:click={reset}>取り消し</button>
        </div>
      {/if}
    </div>

    {#if loading}
      <div class="loading-container">
        <LoadingSpinner />
        <p>読み込み中...</p>
      </div>
    {:else if preview}
      <div class="preview-section">
        <h3>プレビュー ({preview.total}件)</h3>

        {#if preview.errors && preview.errors.length > 0}
          <div class="preview-errors">
            <h4>エラー ({preview.errors.length}件)</h4>
            <ul>
              {#each preview.errors.slice(0, 5) as err}
                <li>行 {err.row}: {err.error}</li>
              {/each}
              {#if preview.errors.length > 5}
                <li>... 他 {preview.errors.length - 5} 件</li>
              {/if}
            </ul>
          </div>
        {/if}

        <div class="preview-table-wrapper">
          <table class="preview-table">
            <thead>
              <tr>
                <th>タイトル</th>
                <th>説明</th>
                <th>人数</th>
                <th>材料数</th>
                <th>手順数</th>
                <th>タグ</th>
              </tr>
            </thead>
            <tbody>
              {#each preview.recipes as recipe}
                <tr>
                  <td>{recipe.title}</td>
                  <td class="truncate">{recipe.description || '-'}</td>
                  <td>{recipe.servings || '-'}</td>
                  <td>{recipe.ingredients?.length || 0}</td>
                  <td>{recipe.steps?.length || 0}</td>
                  <td>{recipe.tags?.join(', ') || '-'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        {#if preview.total > 10}
          <p class="preview-note">* プレビューは最初の10件のみ表示</p>
        {/if}

        <div class="import-options">
          <label class="checkbox-label">
            <input type="checkbox" bind:checked={skipDuplicates} />
            重複するレシピをスキップ
          </label>
        </div>

        <div class="import-actions">
          <button class="btn-cancel" on:click={reset}>キャンセル</button>
          <button class="btn-import" on:click={handleImport}>
            {preview.total}件をインポート
          </button>
        </div>
      </div>
    {/if}
  {:else}
    <div class="result-section">
      <h3>インポート結果</h3>

      <div class="result-summary">
        <div class="result-item success">
          <span class="result-label">インポート成功</span>
          <span class="result-value">{result.summary.imported}件</span>
        </div>
        <div class="result-item skip">
          <span class="result-label">スキップ</span>
          <span class="result-value">{result.summary.skipped}件</span>
        </div>
        <div class="result-item error">
          <span class="result-label">エラー</span>
          <span class="result-value">{result.summary.errors}件</span>
        </div>
      </div>

      {#if result.imported && result.imported.length > 0}
        <div class="result-detail">
          <h4>インポートしたレシピ</h4>
          <ul class="imported-list">
            {#each result.imported as item}
              <li>{item.title}</li>
            {/each}
          </ul>
        </div>
      {/if}

      {#if result.skipped && result.skipped.length > 0}
        <div class="result-detail">
          <h4>スキップしたレシピ</h4>
          <ul class="skipped-list">
            {#each result.skipped as item}
              <li>{item.title} ({item.reason === 'duplicate' ? '重複' : item.reason})</li>
            {/each}
          </ul>
        </div>
      {/if}

      {#if result.errors && result.errors.length > 0}
        <div class="result-detail">
          <h4>エラー</h4>
          <ul class="error-list">
            {#each result.errors as err}
              <li>{err.title || `行 ${err.row}`}: {err.error}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <div class="result-actions">
        <button class="btn-new-import" on:click={reset}>
          別のファイルをインポート
        </button>
        <button class="btn-done" on:click={handleBack}>
          完了
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .csv-import {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .header h2 {
    margin: 0;
    font-size: 1.25rem;
  }

  .btn-back {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 0.5rem;
    font-size: 1rem;
  }

  .btn-back:hover {
    color: #333;
  }

  .upload-section {
    margin-bottom: 1.5rem;
  }

  .drop-zone {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 3rem;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
  }

  .drop-zone.drag-over {
    border-color: #4a90a4;
    background: #f0f7fa;
  }

  .drop-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .upload-icon {
    width: 48px;
    height: 48px;
    color: #999;
    margin-bottom: 0.5rem;
  }

  .drop-zone p {
    margin: 0;
    color: #666;
  }

  .or {
    font-size: 0.85rem;
    color: #999 !important;
  }

  .file-input-label {
    background: #4a90a4;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    margin-top: 0.5rem;
    transition: background 0.2s;
  }

  .file-input-label:hover {
    background: #3d7a8a;
  }

  .file-input {
    display: none;
  }

  .template-section {
    margin-top: 1.5rem;
    padding: 1.5rem;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    text-align: center;
  }

  .btn-template-download {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    background: #0284c7;
    border: none;
    color: white;
    padding: 0.875rem 1.5rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(2, 132, 199, 0.3);
  }

  .btn-template-download:hover {
    background: #0369a1;
    box-shadow: 0 4px 8px rgba(2, 132, 199, 0.4);
    transform: translateY(-1px);
  }

  .download-icon {
    width: 20px;
    height: 20px;
  }

  .template-hint {
    font-size: 0.85rem;
    color: #0369a1;
    margin-top: 0.75rem;
    margin-bottom: 0;
  }

  .file-info {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: #f5f5f5;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .file-name {
    font-weight: 500;
  }

  .file-size {
    color: #666;
    font-size: 0.9rem;
  }

  .btn-clear {
    margin-left: auto;
    background: none;
    border: none;
    color: #e74c3c;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .loading-container {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .preview-section h3 {
    margin: 0 0 1rem;
    font-size: 1.1rem;
  }

  .preview-errors {
    background: #fef2f2;
    border: 1px solid #fee2e2;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .preview-errors h4 {
    color: #dc2626;
    margin: 0 0 0.5rem;
    font-size: 0.95rem;
  }

  .preview-errors ul {
    margin: 0;
    padding-left: 1.5rem;
    color: #b91c1c;
    font-size: 0.9rem;
  }

  .preview-table-wrapper {
    overflow-x: auto;
    margin-bottom: 1rem;
  }

  .preview-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  .preview-table th,
  .preview-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  .preview-table th {
    background: #f9f9f9;
    font-weight: 600;
    white-space: nowrap;
  }

  .truncate {
    max-width: 200px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .preview-note {
    font-size: 0.8rem;
    color: #999;
    margin: 0.5rem 0 1rem;
  }

  .import-options {
    margin-bottom: 1rem;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .import-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
  }

  .btn-cancel {
    background: #f5f5f5;
    border: 1px solid #ccc;
    color: #333;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .btn-import {
    background: #4a90a4;
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .btn-import:hover {
    background: #3d7a8a;
  }

  .result-section h3 {
    margin: 0 0 1.5rem;
    font-size: 1.1rem;
  }

  .result-summary {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .result-item {
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
  }

  .result-item.success {
    background: #ecfdf5;
  }

  .result-item.skip {
    background: #fef3c7;
  }

  .result-item.error {
    background: #fef2f2;
  }

  .result-label {
    display: block;
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.25rem;
  }

  .result-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 600;
  }

  .result-item.success .result-value {
    color: #059669;
  }

  .result-item.skip .result-value {
    color: #d97706;
  }

  .result-item.error .result-value {
    color: #dc2626;
  }

  .result-detail {
    margin-bottom: 1rem;
  }

  .result-detail h4 {
    margin: 0 0 0.5rem;
    font-size: 0.95rem;
  }

  .result-detail ul {
    margin: 0;
    padding-left: 1.5rem;
    font-size: 0.9rem;
    max-height: 150px;
    overflow-y: auto;
  }

  .imported-list li {
    color: #059669;
  }

  .skipped-list li {
    color: #d97706;
  }

  .error-list li {
    color: #dc2626;
  }

  .result-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 1.5rem;
  }

  .btn-new-import {
    background: #f5f5f5;
    border: 1px solid #ccc;
    color: #333;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .btn-done {
    background: #4a90a4;
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .btn-done:hover {
    background: #3d7a8a;
  }
</style>
