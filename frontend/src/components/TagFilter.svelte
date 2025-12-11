<script>
  import { createEventDispatcher } from 'svelte';

  export let tags = [];
  export let selectedTags = [];
  export let maxVisible = 10;

  const dispatch = createEventDispatcher();

  let showAll = false;

  $: visibleTags = showAll ? tags : tags.slice(0, maxVisible);
  $: hasMore = tags.length > maxVisible;

  function toggleTag(tag) {
    if (selectedTags.includes(tag)) {
      selectedTags = selectedTags.filter(t => t !== tag);
    } else {
      selectedTags = [...selectedTags, tag];
    }
    dispatch('change', { selectedTags });
  }

  function clearAll() {
    selectedTags = [];
    dispatch('change', { selectedTags });
  }

  function toggleShowAll() {
    showAll = !showAll;
  }

  function isSelected(tag) {
    return selectedTags.includes(tag);
  }
</script>

<div class="tag-filter">
  <div class="filter-header">
    <h3 class="filter-title">タグ絞り込み</h3>
    {#if selectedTags.length > 0}
      <button on:click={clearAll} class="clear-all-button">
        すべてクリア ({selectedTags.length})
      </button>
    {/if}
  </div>

  {#if tags.length === 0}
    <p class="no-tags">タグがありません</p>
  {:else}
    <div class="tags-container">
      {#each visibleTags as tag}
        <button
          on:click={() => toggleTag(tag)}
          class="tag-button"
          class:selected={isSelected(tag)}
          aria-pressed={isSelected(tag)}
        >
          {tag}
        </button>
      {/each}
    </div>

    {#if hasMore}
      <button on:click={toggleShowAll} class="show-more-button">
        {showAll ? '一部のみ表示' : `さらに表示 (+${tags.length - maxVisible})`}
      </button>
    {/if}
  {/if}
</div>

<style>
  .tag-filter {
    width: 100%;
    margin-bottom: 1.5rem;
    padding: 1.25rem;
    background-color: #f9fafb;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
  }

  .filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .filter-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
  }

  .clear-all-button {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    color: #3b82f6;
    background: none;
    border: 1px solid #3b82f6;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .clear-all-button:hover {
    background-color: #3b82f6;
    color: #fff;
  }

  .no-tags {
    color: #6b7280;
    font-size: 0.875rem;
    margin: 0;
    text-align: center;
    padding: 1rem 0;
  }

  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .tag-button {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    border: 1px solid #d1d5db;
    border-radius: 9999px;
    background-color: #fff;
    color: #4b5563;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
  }

  .tag-button:hover {
    border-color: #3b82f6;
    color: #3b82f6;
    background-color: #eff6ff;
  }

  .tag-button.selected {
    background-color: #3b82f6;
    color: #fff;
    border-color: #3b82f6;
  }

  .tag-button.selected:hover {
    background-color: #2563eb;
    border-color: #2563eb;
  }

  .tag-button:active {
    transform: scale(0.97);
  }

  .show-more-button {
    margin-top: 0.75rem;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    color: #6b7280;
    background: none;
    border: 1px dashed #d1d5db;
    border-radius: 0.375rem;
    cursor: pointer;
    width: 100%;
    transition: all 0.2s ease;
  }

  .show-more-button:hover {
    color: #1f2937;
    border-color: #9ca3af;
    background-color: #f3f4f6;
  }

  /* レスポンシブデザイン */
  @media (max-width: 640px) {
    .tag-filter {
      padding: 1rem;
    }

    .filter-title {
      font-size: 0.875rem;
    }

    .tag-button {
      padding: 0.375rem 0.75rem;
      font-size: 0.8125rem;
    }

    .clear-all-button {
      font-size: 0.8125rem;
      padding: 0.25rem 0.625rem;
    }
  }
</style>
