<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { tagApi } from '../services/api.js';

  export let currentView = 'dashboard';

  const dispatch = createEventDispatcher();

  let tags = [];
  let tagsLoading = false;
  let collapsed = false;

  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'ダッシュボード' },
    { id: 'list', icon: '📚', label: 'レシピ一覧' },
    { id: 'create', icon: '➕', label: '新規作成' },
    { id: 'shopping', icon: '🛒', label: '買い物リスト' },
    { id: 'collector', icon: '🌍', label: '海外レシピ収集' },
    { id: 'import', icon: '📥', label: 'CSVインポート' },
  ];

  onMount(async () => {
    await loadTags();
  });

  async function loadTags() {
    tagsLoading = true;
    try {
      const response = await tagApi.list();
      if (response.status === 'ok') {
        tags = response.data || [];
      }
    } catch (e) {
      console.error('Failed to load tags:', e);
    } finally {
      tagsLoading = false;
    }
  }

  function handleNavigation(viewId) {
    dispatch('navigate', { view: viewId });
  }

  function handleTagFilter(tagId) {
    dispatch('filterTag', { tagId });
  }

  function toggleCollapse() {
    collapsed = !collapsed;
  }
</script>

<aside class="sidebar" class:sidebar--collapsed={collapsed}>
  <div class="sidebar-header">
    <div class="logo">
      <span class="logo-icon">🍳</span>
      {#if !collapsed}
        <span class="logo-text">PRI</span>
      {/if}
    </div>
    <button class="collapse-btn" on:click={toggleCollapse} aria-label="サイドバーを{collapsed ? '展開' : '折りたたみ'}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
        {#if collapsed}
          <path d="M9 18l6-6-6-6"/>
        {:else}
          <path d="M15 18l-6-6 6-6"/>
        {/if}
      </svg>
    </button>
  </div>

  <nav class="sidebar-nav">
    <ul class="nav-list">
      {#each menuItems as item}
        <li>
          <button
            class="nav-item"
            class:nav-item--active={currentView === item.id}
            on:click={() => handleNavigation(item.id)}
            title={collapsed ? item.label : ''}
          >
            <span class="nav-icon">{item.icon}</span>
            {#if !collapsed}
              <span class="nav-label">{item.label}</span>
            {/if}
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  {#if !collapsed}
    <div class="sidebar-section">
      <div class="section-header">
        <span class="section-title">タグ</span>
      </div>
      {#if tagsLoading}
        <div class="tags-loading">読込中...</div>
      {:else if tags.length === 0}
        <div class="tags-empty">タグなし</div>
      {:else}
        <div class="tags-list">
          {#each tags.slice(0, 10) as tag}
            <button class="tag-item" on:click={() => handleTagFilter(tag.id)}>
              <span class="tag-icon">🏷️</span>
              <span class="tag-name">{tag.name}</span>
            </button>
          {/each}
          {#if tags.length > 10}
            <div class="tags-more">+{tags.length - 10} more</div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}

  <div class="sidebar-footer">
    {#if !collapsed}
      <div class="version">v0.2.0</div>
    {/if}
  </div>
</aside>

<style>
  .sidebar {
    width: 240px;
    min-height: 100vh;
    background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    color: #2c3e50;
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
  }

  .sidebar--collapsed {
    width: 64px;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .logo-icon {
    font-size: 1.5rem;
  }

  .logo-text {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .collapse-btn {
    padding: 0.5rem;
    background: transparent;
    border: none;
    color: rgba(0, 0, 0, 0.5);
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .collapse-btn:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #2c3e50;
  }

  .sidebar-nav {
    flex: 1;
    padding: 1rem 0.5rem;
  }

  .nav-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    width: 100%;
    padding: 0.75rem 1rem;
    background: transparent;
    border: none;
    border-radius: 8px;
    color: rgba(0, 0, 0, 0.7);
    cursor: pointer;
    font-size: 0.9rem;
    text-align: left;
    transition: all 0.2s;
  }

  .nav-item:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #2c3e50;
  }

  .nav-item--active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .nav-icon {
    font-size: 1.25rem;
    min-width: 24px;
    text-align: center;
  }

  .nav-label {
    white-space: nowrap;
  }

  .sidebar-section {
    padding: 0 0.5rem 1rem;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
    margin-top: auto;
  }

  .section-header {
    padding: 1rem 1rem 0.5rem;
  }

  .section-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: rgba(0, 0, 0, 0.5);
    letter-spacing: 0.5px;
    font-weight: 600;
  }

  .tags-loading,
  .tags-empty {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
    color: rgba(0, 0, 0, 0.5);
  }

  .tags-list {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .tag-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.5rem 1rem;
    background: transparent;
    border: none;
    border-radius: 6px;
    color: rgba(0, 0, 0, 0.7);
    cursor: pointer;
    font-size: 0.85rem;
    text-align: left;
    transition: all 0.2s;
  }

  .tag-item:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #2c3e50;
  }

  .tag-icon {
    font-size: 0.9rem;
  }

  .tag-name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .tags-more {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
    color: rgba(0, 0, 0, 0.4);
  }

  .sidebar-footer {
    padding: 1rem;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
  }

  .version {
    font-size: 0.75rem;
    color: rgba(0, 0, 0, 0.4);
    text-align: center;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .sidebar {
      display: none;
    }
  }
</style>
