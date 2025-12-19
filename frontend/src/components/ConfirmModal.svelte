<script>
  import { createEventDispatcher } from 'svelte';

  export let show = false;
  export let title = '確認';
  export let message = '';
  export let confirmText = 'OK';
  export let cancelText = 'キャンセル';
  export let danger = false;

  const dispatch = createEventDispatcher();

  function handleConfirm() {
    dispatch('confirm');
    show = false;
  }

  function handleCancel() {
    dispatch('cancel');
    show = false;
  }

  function handleKeydown(event) {
    if (!show) return;
    if (event.key === 'Escape') {
      handleCancel();
    } else if (event.key === 'Enter') {
      handleConfirm();
    }
  }

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      handleCancel();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if show}
  <div
    class="modal-backdrop"
    on:click={handleBackdropClick}
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
    aria-describedby="modal-message"
  >
    <div class="modal-content" role="document">
      <h2 id="modal-title">{title}</h2>
      <p id="modal-message">{message}</p>
      <div class="modal-actions">
        <button
          type="button"
          class="btn-cancel"
          on:click={handleCancel}
          aria-label={cancelText}
        >
          {cancelText}
        </button>
        <button
          type="button"
          class="btn-confirm"
          class:danger
          on:click={handleConfirm}
          aria-label={confirmText}
        >
          {confirmText}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    animation: fadeIn 0.15s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal-content {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    animation: slideIn 0.15s ease-out;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(-10px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  h2 {
    margin: 0 0 0.75rem 0;
    font-size: 1.25rem;
    color: #333;
  }

  p {
    margin: 0 0 1.5rem 0;
    color: #666;
    line-height: 1.5;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
  }

  button {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-cancel {
    background: white;
    border: 1px solid #ddd;
    color: #666;
  }

  .btn-cancel:hover {
    background: #f5f5f5;
  }

  .btn-confirm {
    background: #0077aa;
    border: 1px solid #0077aa;
    color: white;
  }

  .btn-confirm:hover {
    background: #005580;
  }

  .btn-confirm.danger {
    background: #dc3545;
    border-color: #dc3545;
  }

  .btn-confirm.danger:hover {
    background: #c82333;
  }

  button:focus {
    outline: 2px solid #0077aa;
    outline-offset: 2px;
  }

  .btn-confirm.danger:focus {
    outline-color: #dc3545;
  }
</style>
