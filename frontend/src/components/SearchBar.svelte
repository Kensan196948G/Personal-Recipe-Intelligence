<script>
  import { createEventDispatcher } from 'svelte';

  export let placeholder = 'レシピを検索...';
  export let value = '';

  const dispatch = createEventDispatcher();

  let inputElement;

  function handleInput(event) {
    value = event.target.value;
    dispatch('search', { query: value });
  }

  function handleClear() {
    value = '';
    dispatch('search', { query: '' });
    inputElement?.focus();
  }

  function handleSubmit(event) {
    event.preventDefault();
    dispatch('submit', { query: value });
  }
</script>

<form on:submit={handleSubmit} class="search-bar">
  <div class="search-container">
    <svg class="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM18.5 18.5l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>

    <input
      bind:this={inputElement}
      type="text"
      bind:value
      on:input={handleInput}
      {placeholder}
      class="search-input"
      aria-label="レシピ検索"
    />

    {#if value}
      <button
        type="button"
        on:click={handleClear}
        class="clear-button"
        aria-label="クリア"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    {/if}
  </div>
</form>

<style>
  .search-bar {
    width: 100%;
    margin-bottom: 1.5rem;
  }

  .search-container {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    color: #9ca3af;
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 2.5rem 0.75rem 3rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 1rem;
    transition: all 0.2s ease;
    background-color: #fff;
  }

  .search-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .search-input::placeholder {
    color: #9ca3af;
  }

  .clear-button {
    position: absolute;
    right: 0.75rem;
    padding: 0.25rem;
    background: none;
    border: none;
    color: #6b7280;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.25rem;
    transition: all 0.2s ease;
  }

  .clear-button:hover {
    color: #1f2937;
    background-color: #f3f4f6;
  }

  .clear-button:active {
    transform: scale(0.95);
  }

  /* レスポンシブデザイン */
  @media (max-width: 640px) {
    .search-input {
      font-size: 0.875rem;
      padding: 0.625rem 2.5rem 0.625rem 2.75rem;
    }

    .search-icon {
      left: 0.75rem;
      width: 18px;
      height: 18px;
    }
  }
</style>
