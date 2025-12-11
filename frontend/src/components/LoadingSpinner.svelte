<script>
  export let size = 'medium'; // 'small', 'medium', 'large'
  export let message = '読み込み中...';
  export let fullScreen = false;
</script>

{#if fullScreen}
  <div class="fullscreen-overlay">
    <div class="spinner-container">
      <div class="spinner" class:small={size === 'small'} class:large={size === 'large'}></div>
      {#if message}
        <p class="loading-message">{message}</p>
      {/if}
    </div>
  </div>
{:else}
  <div class="spinner-wrapper">
    <div class="spinner" class:small={size === 'small'} class:large={size === 'large'}></div>
    {#if message}
      <p class="loading-message">{message}</p>
    {/if}
  </div>
{/if}

<style>
  .fullscreen-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }

  .spinner-container,
  .spinner-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .spinner-wrapper {
    padding: 2rem;
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .spinner.small {
    width: 24px;
    height: 24px;
    border-width: 3px;
  }

  .spinner.large {
    width: 64px;
    height: 64px;
    border-width: 5px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .loading-message {
    margin: 0;
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
  }

  .fullscreen-overlay .loading-message {
    font-size: 1rem;
  }

  /* レスポンシブデザイン */
  @media (max-width: 640px) {
    .spinner {
      width: 40px;
      height: 40px;
      border-width: 3px;
    }

    .spinner.small {
      width: 20px;
      height: 20px;
      border-width: 2px;
    }

    .spinner.large {
      width: 56px;
      height: 56px;
      border-width: 4px;
    }

    .loading-message {
      font-size: 0.8125rem;
    }
  }
</style>
