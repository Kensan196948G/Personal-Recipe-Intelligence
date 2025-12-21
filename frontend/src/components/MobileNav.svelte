<script>
  import { createEventDispatcher } from 'svelte';

  export let currentView = 'dashboard';

  const dispatch = createEventDispatcher();

  const navItems = [
    { id: 'dashboard', icon: '📊', label: 'ホーム' },
    { id: 'list', icon: '📚', label: 'レシピ' },
    { id: 'shopping', icon: '🛒', label: '買物' },
    { id: 'create', icon: '➕', label: '追加' },
  ];

  function handleNav(viewId) {
    dispatch('navigate', { view: viewId });
  }
</script>

<nav class="mobile-nav">
  {#each navItems as item}
    <button
      class="nav-item"
      class:active={currentView === item.id}
      on:click={() => handleNav(item.id)}
    >
      <span class="nav-icon">{item.icon}</span>
      <span class="nav-label">{item.label}</span>
    </button>
  {/each}
</nav>

<style>
  .mobile-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e0e0e0;
    padding: 0.5rem 0;
    padding-bottom: calc(0.5rem + env(safe-area-inset-bottom, 0));
    z-index: 1000;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 768px) {
    .mobile-nav {
      display: flex;
      justify-content: space-around;
    }
  }

  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem 1rem;
    background: transparent;
    border: none;
    color: #888;
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.2s;
  }

  .nav-item.active {
    color: #667eea;
  }

  .nav-item.active .nav-icon {
    transform: scale(1.1);
  }

  .nav-icon {
    font-size: 1.5rem;
    transition: transform 0.2s;
  }

  .nav-label {
    font-size: 0.7rem;
    font-weight: 500;
  }
</style>
