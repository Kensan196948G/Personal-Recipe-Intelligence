<script>
  import Sidebar from './components/Sidebar.svelte';
  import Dashboard from './components/Dashboard.svelte';
  import RecipeList from './components/RecipeList.svelte';
  import RecipeDetail from './components/RecipeDetail.svelte';
  import RecipeForm from './components/RecipeForm.svelte';
  import CsvImport from './components/CsvImport.svelte';
  import RecipeCollector from './components/RecipeCollector.svelte';
  import ShoppingList from './components/ShoppingList.svelte';
  import MobileNav from './components/MobileNav.svelte';
  import { fetchRecipe, currentRecipe, fetchRecipes } from './stores/recipes.js';

  // View state
  let view = 'dashboard'; // 'dashboard', 'list', 'detail', 'create', 'edit', 'import', 'collector', 'shopping'
  let selectedRecipe = null;

  function handleNavigation(event) {
    const newView = event.detail.view;
    if (newView === 'list') {
      view = 'list';
      selectedRecipe = null;
    } else if (newView === 'create') {
      view = 'create';
      selectedRecipe = null;
    } else if (newView === 'import') {
      view = 'import';
    } else if (newView === 'collector') {
      view = 'collector';
    } else if (newView === 'shopping') {
      view = 'shopping';
    } else if (newView === 'dashboard') {
      view = 'dashboard';
    }
  }

  function handleTagFilter(event) {
    const { tagId } = event.detail;
    view = 'list';
    // タグフィルター付きでレシピ一覧を取得
    fetchRecipes({ tag_id: tagId });
  }

  async function handleViewRecipe(event) {
    const recipe = event.detail;
    await fetchRecipe(recipe.id);
    if ($currentRecipe) {
      selectedRecipe = $currentRecipe;
      view = 'detail';
    }
  }

  async function handleView(event) {
    selectedRecipe = event.detail;
    await fetchRecipe(selectedRecipe.id);
    if ($currentRecipe) {
      selectedRecipe = $currentRecipe;
      view = 'detail';
    }
  }

  function handleEdit(event) {
    selectedRecipe = event.detail;
    view = 'edit';
  }

  function handleCreate() {
    selectedRecipe = null;
    view = 'create';
  }

  function handleBack() {
    view = 'list';
    selectedRecipe = null;
  }

  function handleSaved() {
    view = 'list';
    selectedRecipe = null;
  }

  function handleImport() {
    view = 'import';
  }

  async function handleImported() {
    await fetchRecipes();
    view = 'list';
  }

  function handleCollector() {
    view = 'collector';
  }
</script>

<div class="app-layout">
  <Sidebar
    currentView={view}
    on:navigate={handleNavigation}
    on:filterTag={handleTagFilter}
  />

  <main class="main-content">
    <header class="main-header">
      <h1>Personal Recipe Intelligence</h1>
      <p>個人向け料理レシピ収集・管理システム</p>
    </header>

    <section class="content">
      {#if view === 'dashboard'}
        <Dashboard on:viewRecipe={handleViewRecipe} />
      {:else if view === 'list'}
        <RecipeList
          on:view={handleView}
          on:edit={handleEdit}
          on:create={handleCreate}
          on:import={handleImport}
          on:collector={handleCollector}
        />
      {:else if view === 'detail' && selectedRecipe}
        <RecipeDetail
          recipe={selectedRecipe}
          on:back={handleBack}
          on:edit={handleEdit}
        />
      {:else if view === 'create'}
        <RecipeForm mode="create" on:back={handleBack} on:saved={handleSaved} />
      {:else if view === 'edit' && selectedRecipe}
        <RecipeForm
          recipe={selectedRecipe}
          mode="edit"
          on:back={handleBack}
          on:saved={handleSaved}
        />
      {:else if view === 'import'}
        <CsvImport
          on:back={handleBack}
          on:imported={handleImported}
        />
      {:else if view === 'collector'}
        <div class="collector-view">
          <button class="back-btn" on:click={handleBack}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            戻る
          </button>
          <RecipeCollector />
        </div>
      {:else if view === 'shopping'}
        <ShoppingList on:back={handleBack} />
      {/if}
    </section>

    <footer class="main-footer">
      <p>Personal Recipe Intelligence v0.2.0</p>
    </footer>
  </main>

  <MobileNav currentView={view} on:navigate={handleNavigation} />
</div>

<style>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      'Hiragino Sans', 'Noto Sans JP', sans-serif;
    margin: 0;
    padding: 0;
    background: #f0f2f5;
    min-height: 100vh;
  }

  :global(*) {
    box-sizing: border-box;
  }

  .app-layout {
    display: flex;
    min-height: 100vh;
  }

  .main-content {
    flex: 1;
    margin-left: 240px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    transition: margin-left 0.3s ease;
  }

  .main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    text-align: center;
  }

  .main-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.75rem;
    font-weight: 700;
  }

  .main-header p {
    margin: 0;
    opacity: 0.9;
    font-size: 0.9rem;
  }

  .content {
    flex: 1;
    padding: 2rem;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
  }

  .main-footer {
    text-align: center;
    padding: 1rem 2rem;
    border-top: 1px solid #e0e0e0;
    background: white;
  }

  .main-footer p {
    color: #888;
    font-size: 0.85rem;
    margin: 0;
  }

  .collector-view {
    position: relative;
  }

  .collector-view .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    transition: all 0.2s;
  }

  .collector-view .back-btn:hover {
    background: #f5f5f5;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .main-content {
      margin-left: 0;
      padding-bottom: 70px; /* Space for mobile nav */
    }

    .content {
      padding: 1rem;
    }

    .main-header {
      padding: 1.5rem 1rem;
    }

    .main-header h1 {
      font-size: 1.25rem;
    }

    .main-footer {
      padding-bottom: 80px;
    }
  }

  @media (max-width: 480px) {
    .main-header h1 {
      font-size: 1.1rem;
    }

    .main-header p {
      font-size: 0.8rem;
    }

    .content {
      padding: 0.75rem;
    }
  }
</style>
