<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { shoppingListApi, recipeApi } from '../services/api.js';

  const dispatch = createEventDispatcher();

  let lists = [];
  let selectedList = null;
  let loading = true;
  let error = null;

  // 新規リスト作成
  let showNewListForm = false;
  let newListName = '';

  // 新規アイテム追加
  let newItemName = '';
  let newItemAmount = '';
  let newItemUnit = '';

  // レシピ追加モーダル
  let showRecipeModal = false;
  let recipes = [];
  let selectedRecipeId = null;
  let recipeMultiplier = 1;

  onMount(async () => {
    await loadLists();
  });

  async function loadLists() {
    loading = true;
    error = null;
    try {
      const response = await shoppingListApi.list();
      if (response.status === 'ok') {
        lists = response.data.items || [];
        // 自動で最初のリストを選択、なければ作成
        if (lists.length > 0 && !selectedList) {
          await selectList(lists[0].id);
        }
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function selectList(listId) {
    try {
      const response = await shoppingListApi.get(listId);
      if (response.status === 'ok') {
        selectedList = response.data;
      }
    } catch (e) {
      error = e.message;
    }
  }

  async function createList() {
    if (!newListName.trim()) return;

    try {
      const response = await shoppingListApi.create({ name: newListName.trim() });
      if (response.status === 'ok') {
        newListName = '';
        showNewListForm = false;
        await loadLists();
        await selectList(response.data.id);
      }
    } catch (e) {
      error = e.message;
    }
  }

  async function deleteList(listId) {
    if (!confirm('この買い物リストを削除しますか？')) return;

    try {
      await shoppingListApi.delete(listId);
      selectedList = null;
      await loadLists();
    } catch (e) {
      error = e.message;
    }
  }

  async function addItem() {
    if (!newItemName.trim() || !selectedList) return;

    try {
      const item = {
        name: newItemName.trim(),
        amount: newItemAmount ? parseFloat(newItemAmount) : null,
        unit: newItemUnit.trim() || null,
      };
      await shoppingListApi.addItem(selectedList.id, item);
      newItemName = '';
      newItemAmount = '';
      newItemUnit = '';
      await selectList(selectedList.id);
    } catch (e) {
      error = e.message;
    }
  }

  async function toggleItem(itemId) {
    try {
      await shoppingListApi.toggleItem(selectedList.id, itemId);
      await selectList(selectedList.id);
    } catch (e) {
      error = e.message;
    }
  }

  async function deleteItem(itemId) {
    try {
      await shoppingListApi.deleteItem(selectedList.id, itemId);
      await selectList(selectedList.id);
    } catch (e) {
      error = e.message;
    }
  }

  async function clearChecked() {
    if (!confirm('チェック済みのアイテムを削除しますか？')) return;

    try {
      await shoppingListApi.clearChecked(selectedList.id);
      await selectList(selectedList.id);
    } catch (e) {
      error = e.message;
    }
  }

  async function openRecipeModal() {
    showRecipeModal = true;
    try {
      const response = await recipeApi.list({ per_page: 100 });
      if (response.status === 'ok') {
        recipes = response.data.items || [];
      }
    } catch (e) {
      error = e.message;
    }
  }

  async function addRecipeIngredients() {
    if (!selectedRecipeId || !selectedList) return;

    try {
      await shoppingListApi.addRecipe(selectedList.id, selectedRecipeId, recipeMultiplier);
      showRecipeModal = false;
      selectedRecipeId = null;
      recipeMultiplier = 1;
      await selectList(selectedList.id);
    } catch (e) {
      error = e.message;
    }
  }

  function getProgress() {
    if (!selectedList || !selectedList.items || selectedList.items.length === 0) return 0;
    const checked = selectedList.items.filter(item => item.is_checked).length;
    return Math.round((checked / selectedList.items.length) * 100);
  }

  // アイテムをレシピ名でグループ化
  $: groupedItems = (() => {
    if (!selectedList || !selectedList.items) return [];

    const groups = new Map();
    const noRecipeItems = [];

    for (const item of selectedList.items) {
      if (item.recipe_name) {
        if (!groups.has(item.recipe_name)) {
          groups.set(item.recipe_name, []);
        }
        groups.get(item.recipe_name).push(item);
      } else {
        noRecipeItems.push(item);
      }
    }

    const result = [];

    // レシピ名のあるグループを先に
    for (const [recipeName, items] of groups) {
      result.push({ recipeName, items });
    }

    // レシピ名のないアイテムは最後に「その他」として表示
    if (noRecipeItems.length > 0) {
      result.push({ recipeName: null, items: noRecipeItems });
    }

    return result;
  })();

  function handleBack() {
    dispatch('back');
  }
</script>

<div class="shopping-list-page">
  <header class="page-header">
    <button class="back-btn" on:click={handleBack}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      戻る
    </button>
    <h1>買い物リスト</h1>
  </header>

  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  <div class="shopping-layout">
    <!-- サイドパネル: リスト一覧 -->
    <aside class="lists-panel">
      <div class="panel-header">
        <h2>リスト</h2>
        <button class="add-btn" on:click={() => showNewListForm = true}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
      </div>

      {#if showNewListForm}
        <form class="new-list-form" on:submit|preventDefault={createList}>
          <input
            type="text"
            bind:value={newListName}
            placeholder="リスト名"
            autofocus
          />
          <div class="form-actions">
            <button type="submit" class="btn-primary">作成</button>
            <button type="button" class="btn-secondary" on:click={() => showNewListForm = false}>キャンセル</button>
          </div>
        </form>
      {/if}

      {#if loading}
        <div class="loading">読込中...</div>
      {:else if lists.length === 0}
        <div class="empty-state">
          <p>買い物リストがありません</p>
          <button class="btn-primary" on:click={() => showNewListForm = true}>
            新しいリストを作成
          </button>
        </div>
      {:else}
        <ul class="lists">
          {#each lists as list}
            <li
              class="list-item"
              class:active={selectedList?.id === list.id}
              on:click={() => selectList(list.id)}
              on:keypress={() => selectList(list.id)}
              role="button"
              tabindex="0"
            >
              <div class="list-info">
                <span class="list-name">{list.name}</span>
                <span class="list-count">{list.checked_count}/{list.item_count}</span>
              </div>
              <button
                class="delete-list-btn"
                on:click|stopPropagation={() => deleteList(list.id)}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </aside>

    <!-- メインコンテンツ: 選択されたリスト -->
    <main class="list-content">
      {#if selectedList}
        <div class="list-header">
          <h2>{selectedList.name}</h2>
          <div class="list-actions">
            <button class="action-btn" on:click={openRecipeModal}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              レシピから追加
            </button>
            {#if selectedList.items?.some(item => item.is_checked)}
              <button class="action-btn danger" on:click={clearChecked}>
                チェック済みをクリア
              </button>
            {/if}
          </div>
        </div>

        <!-- 進捗バー -->
        <div class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress()}%"></div>
          </div>
          <span class="progress-text">{getProgress()}% 完了</span>
        </div>

        <!-- アイテム追加フォーム -->
        <form class="add-item-form" on:submit|preventDefault={addItem}>
          <input
            type="text"
            bind:value={newItemName}
            placeholder="アイテム名"
            class="item-name-input"
          />
          <input
            type="number"
            bind:value={newItemAmount}
            placeholder="数量"
            class="item-amount-input"
            step="0.1"
          />
          <input
            type="text"
            bind:value={newItemUnit}
            placeholder="単位"
            class="item-unit-input"
          />
          <button type="submit" class="add-item-btn">追加</button>
        </form>

        <!-- アイテムリスト（レシピ別グループ表示） -->
        {#if selectedList.items?.length === 0}
          <div class="empty-items">
            <p>アイテムがありません</p>
            <p class="hint">上のフォームから追加するか、レシピから材料をインポートできます</p>
          </div>
        {:else}
          <div class="items-grouped">
            {#each groupedItems as group}
              <div class="recipe-group">
                {#if group.recipeName}
                  <div class="recipe-group-header">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                    <span>{group.recipeName}</span>
                    <span class="item-count">({group.items.length}品)</span>
                  </div>
                {:else}
                  <div class="recipe-group-header other">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="12" y1="8" x2="12" y2="16"/>
                      <line x1="8" y1="12" x2="16" y2="12"/>
                    </svg>
                    <span>その他</span>
                    <span class="item-count">({group.items.length}品)</span>
                  </div>
                {/if}
                <ul class="items-list">
                  {#each group.items as item}
                    <li class="item" class:checked={item.is_checked}>
                      <label class="item-checkbox">
                        <input
                          type="checkbox"
                          checked={item.is_checked}
                          on:change={() => toggleItem(item.id)}
                        />
                        <span class="checkmark"></span>
                      </label>
                      <div class="item-details">
                        <span class="item-name">{item.name}</span>
                        {#if item.amount || item.unit}
                          <span class="item-quantity">
                            {item.amount || ''}{item.unit || ''}
                          </span>
                        {/if}
                      </div>
                      <button class="delete-item-btn" on:click={() => deleteItem(item.id)}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                          <line x1="18" y1="6" x2="6" y2="18"/>
                          <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                      </button>
                    </li>
                  {/each}
                </ul>
              </div>
            {/each}
          </div>
        {/if}
      {:else}
        <div class="no-list-selected">
          <p>リストを選択してください</p>
        </div>
      {/if}
    </main>
  </div>
</div>

<!-- レシピ追加モーダル -->
{#if showRecipeModal}
  <div class="modal-overlay" on:click={() => showRecipeModal = false} on:keypress={() => showRecipeModal = false} role="button" tabindex="0">
    <div class="modal" on:click|stopPropagation on:keypress|stopPropagation role="dialog">
      <div class="modal-header">
        <h3>レシピから材料を追加</h3>
        <button class="close-btn" on:click={() => showRecipeModal = false}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="recipe-select">
          <label>レシピを選択</label>
          <select bind:value={selectedRecipeId}>
            <option value={null}>-- 選択してください --</option>
            {#each recipes as recipe}
              <option value={recipe.id}>{recipe.title}</option>
            {/each}
          </select>
        </div>
        <div class="multiplier-input">
          <label>人数</label>
          <input type="number" bind:value={recipeMultiplier} min="1" max="10" step="1" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={() => showRecipeModal = false}>キャンセル</button>
        <button class="btn-primary" on:click={addRecipeIngredients} disabled={!selectedRecipeId}>
          材料を追加
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .shopping-list-page {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .page-header h1 {
    margin: 0;
    font-size: 1.5rem;
    color: #1a1a2e;
  }

  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .back-btn:hover {
    background: #f5f5f5;
  }

  .error-banner {
    background: #fee2e2;
    color: #dc2626;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .shopping-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 1.5rem;
    min-height: 600px;
  }

  /* Lists Panel */
  .lists-panel {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .panel-header h2 {
    margin: 0;
    font-size: 1rem;
    color: #666;
  }

  .add-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    background: #667eea;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .add-btn:hover {
    background: #5a6fd6;
  }

  .new-list-form {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .new-list-form input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    margin-bottom: 0.5rem;
  }

  .form-actions {
    display: flex;
    gap: 0.5rem;
  }

  .lists {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .list-item:hover {
    background: #f5f5f5;
  }

  .list-item.active {
    background: #e8f0fe;
  }

  .list-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .list-name {
    font-weight: 500;
  }

  .list-count {
    font-size: 0.8rem;
    color: #888;
  }

  .delete-list-btn {
    padding: 0.25rem;
    background: transparent;
    border: none;
    color: #888;
    cursor: pointer;
    border-radius: 4px;
    opacity: 0;
    transition: all 0.2s;
  }

  .list-item:hover .delete-list-btn {
    opacity: 1;
  }

  .delete-list-btn:hover {
    background: #fee2e2;
    color: #dc2626;
  }

  /* Main Content */
  .list-content {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .list-header h2 {
    margin: 0;
    font-size: 1.25rem;
  }

  .list-actions {
    display: flex;
    gap: 0.5rem;
  }

  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: #f5f5f5;
  }

  .action-btn.danger {
    color: #dc2626;
    border-color: #fecaca;
  }

  .action-btn.danger:hover {
    background: #fee2e2;
  }

  /* Progress */
  .progress-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .progress-bar {
    flex: 1;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transition: width 0.3s;
  }

  .progress-text {
    font-size: 0.85rem;
    color: #666;
    min-width: 70px;
  }

  /* Add Item Form */
  .add-item-form {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .item-name-input {
    flex: 2;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
  }

  .item-amount-input {
    width: 80px;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
  }

  .item-unit-input {
    width: 70px;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
  }

  .add-item-btn {
    padding: 0.5rem 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
  }

  .add-item-btn:hover {
    background: #5a6fd6;
  }

  /* Grouped Items */
  .items-grouped {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .recipe-group {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    overflow: hidden;
  }

  .recipe-group-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    font-size: 0.95rem;
  }

  .recipe-group-header svg {
    flex-shrink: 0;
  }

  .recipe-group-header .item-count {
    font-size: 0.8rem;
    font-weight: 400;
    opacity: 0.85;
    margin-left: auto;
  }

  .recipe-group-header.other {
    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  }

  /* Items List */
  .items-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
  }

  .item:last-child {
    border-bottom: none;
  }

  .item:hover {
    background: #fafafa;
  }

  .item.checked {
    opacity: 0.6;
  }

  .item.checked .item-name {
    text-decoration: line-through;
    color: #888;
  }

  .item-checkbox {
    position: relative;
    cursor: pointer;
  }

  .item-checkbox input {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  .item-details {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .item-name {
    font-size: 0.95rem;
  }

  .item-quantity {
    font-size: 0.85rem;
    color: #888;
    background: #f0f0f0;
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
  }

  .delete-item-btn {
    padding: 0.25rem;
    background: transparent;
    border: none;
    color: #888;
    cursor: pointer;
    border-radius: 4px;
    opacity: 0;
    transition: all 0.2s;
  }

  .item:hover .delete-item-btn {
    opacity: 1;
  }

  .delete-item-btn:hover {
    background: #fee2e2;
    color: #dc2626;
  }

  /* Empty States */
  .empty-state, .empty-items, .no-list-selected {
    text-align: center;
    padding: 2rem;
    color: #888;
  }

  .hint {
    font-size: 0.85rem;
    color: #aaa;
  }

  .loading {
    padding: 1rem;
    text-align: center;
    color: #888;
  }

  /* Buttons */
  .btn-primary {
    padding: 0.5rem 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
  }

  .btn-primary:hover {
    background: #5a6fd6;
  }

  .btn-primary:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .btn-secondary {
    padding: 0.5rem 1rem;
    background: white;
    color: #666;
    border: 1px solid #ddd;
    border-radius: 6px;
    cursor: pointer;
  }

  .btn-secondary:hover {
    background: #f5f5f5;
  }

  /* Modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 12px;
    width: 90%;
    max-width: 480px;
    max-height: 80vh;
    overflow: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #eee;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.1rem;
  }

  .close-btn {
    padding: 0.25rem;
    background: transparent;
    border: none;
    cursor: pointer;
    color: #888;
    border-radius: 4px;
  }

  .close-btn:hover {
    background: #f0f0f0;
    color: #333;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .recipe-select, .multiplier-input {
    margin-bottom: 1rem;
  }

  .recipe-select label, .multiplier-input label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
  }

  .recipe-select select, .multiplier-input input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid #eee;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .shopping-layout {
      grid-template-columns: 1fr;
    }

    .lists-panel {
      display: none;
    }

    .add-item-form {
      flex-wrap: wrap;
    }

    .item-name-input {
      flex: 1 1 100%;
    }

    .item-amount-input, .item-unit-input {
      flex: 1;
    }

    .add-item-btn {
      flex: 1 1 100%;
    }
  }
</style>
