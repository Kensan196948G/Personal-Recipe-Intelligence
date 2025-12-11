<script>
  import RecipeList from './components/RecipeList.svelte';
  import RecipeDetail from './components/RecipeDetail.svelte';
  import RecipeForm from './components/RecipeForm.svelte';
  import CsvImport from './components/CsvImport.svelte';
  import RecipeCollector from './components/RecipeCollector.svelte';
  import { fetchRecipe, currentRecipe, fetchRecipes } from './stores/recipes.js';

  // View state
  let view = 'list'; // 'list', 'detail', 'create', 'edit', 'import', 'collector'
  let selectedRecipe = null;

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

<main>
  <header>
    <h1>Personal Recipe Intelligence</h1>
    <p>個人向け料理レシピ収集・管理システム</p>
  </header>

  <section class="content">
    {#if view === 'list'}
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
    {/if}
  </section>

  <footer>
    <p>Personal Recipe Intelligence v0.1.0</p>
  </footer>
</main>

<style>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      'Hiragino Sans', 'Noto Sans JP', sans-serif;
    margin: 0;
    padding: 0;
    background: #f5f5f5;
    min-height: 100vh;
  }

  :global(*) {
    box-sizing: border-box;
  }

  main {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    text-align: center;
    margin-bottom: 2rem;
  }

  h1 {
    color: #333;
    margin-bottom: 0.5rem;
    font-size: 1.75rem;
  }

  header p {
    color: #666;
    margin: 0;
  }

  .content {
    flex: 1;
  }

  footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #ddd;
  }

  footer p {
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
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }

  .collector-view .back-btn:hover {
    background: #f5f5f5;
  }
</style>
