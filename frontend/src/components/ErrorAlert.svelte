<script>
  import { createEventDispatcher, onDestroy } from 'svelte';

  export let type = 'error'; // 'error', 'warning', 'info', 'success'
  export let title = '';
  export let message = '';
  export let dismissible = true;
  export let autoClose = 0; // 0 = no auto close, otherwise milliseconds

  const dispatch = createEventDispatcher();

  let visible = true;
  let timeoutId;

  $: if (autoClose > 0 && visible) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      handleDismiss();
    }, autoClose);
  }

  function handleDismiss() {
    visible = false;
    dispatch('dismiss');
  }

  onDestroy(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  });
</script>

{#if visible}
  <div class="alert" class:error={type === 'error'} class:warning={type === 'warning'} class:info={type === 'info'} class:success={type === 'success'} role="alert">
    <div class="alert-content">
      <div class="alert-icon">
        {#if type === 'error'}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        {:else if type === 'warning'}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 20h20L12 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 9v4M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        {:else if type === 'success'}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        {:else}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 16v-4M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        {/if}
      </div>

      <div class="alert-text">
        {#if title}
          <h4 class="alert-title">{title}</h4>
        {/if}
        {#if message}
          <p class="alert-message">{message}</p>
        {/if}
      </div>
    </div>

    {#if dismissible}
      <button on:click={handleDismiss} class="dismiss-button" aria-label="閉じる">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    {/if}
  </div>
{/if}

<style>
  .alert {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border: 1px solid;
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .alert.error {
    background-color: #fef2f2;
    border-color: #fecaca;
    color: #991b1b;
  }

  .alert.warning {
    background-color: #fffbeb;
    border-color: #fde68a;
    color: #92400e;
  }

  .alert.info {
    background-color: #eff6ff;
    border-color: #bfdbfe;
    color: #1e40af;
  }

  .alert.success {
    background-color: #f0fdf4;
    border-color: #bbf7d0;
    color: #166534;
  }

  .alert-content {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    flex: 1;
  }

  .alert-icon {
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .alert-text {
    flex: 1;
  }

  .alert-title {
    margin: 0 0 0.25rem 0;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .alert-message {
    margin: 0;
    font-size: 0.875rem;
    opacity: 0.9;
  }

  .dismiss-button {
    flex-shrink: 0;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    margin: -0.25rem -0.25rem 0 0;
    border-radius: 0.25rem;
    color: currentColor;
    opacity: 0.6;
    transition: all 0.2s ease;
  }

  .dismiss-button:hover {
    opacity: 1;
    background-color: rgba(0, 0, 0, 0.05);
  }

  .dismiss-button:active {
    transform: scale(0.95);
  }

  /* レスポンシブデザイン */
  @media (max-width: 640px) {
    .alert {
      padding: 0.875rem;
    }

    .alert-content {
      gap: 0.5rem;
    }

    .alert-icon svg {
      width: 20px;
      height: 20px;
    }

    .alert-title {
      font-size: 0.8125rem;
    }

    .alert-message {
      font-size: 0.8125rem;
    }

    .dismiss-button svg {
      width: 18px;
      height: 18px;
    }
  }
</style>
