<script>
  import RecipeList from './components/RecipeList.svelte';
  import RecipeDetail from './components/RecipeDetail.svelte';
  import RecipeForm from './components/RecipeForm.svelte';
  import CsvImport from './components/CsvImport.svelte';
  import { fetchRecipe, currentRecipe, fetchRecipes } from './stores/recipes.js';

  // View state
  let view = 'list'; // 'list', 'detail', 'create', 'edit', 'import'
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
</style>
