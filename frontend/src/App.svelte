<script>
  let recipes = [];
  let loading = true;
  let error = null;

  async function fetchRecipes() {
    try {
      const response = await fetch('/api/v1/recipes');
      const data = await response.json();
      if (data.status === 'ok') {
        recipes = data.data;
      } else {
        error = data.error;
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  // Fetch recipes on mount
  fetchRecipes();
</script>

<main>
  <header>
    <h1>Personal Recipe Intelligence</h1>
    <p>個人向け料理レシピ収集・管理システム</p>
  </header>

  <section class="recipes">
    {#if loading}
      <p>読み込み中...</p>
    {:else if error}
      <p class="error">エラー: {error}</p>
    {:else if recipes.length === 0}
      <p>レシピがありません。</p>
    {:else}
      <ul>
        {#each recipes as recipe}
          <li>
            <h3>{recipe.title}</h3>
            <p>{recipe.description}</p>
          </li>
        {/each}
      </ul>
    {/if}
  </section>
</main>

<style>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    background: #f5f5f5;
  }

  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  header {
    text-align: center;
    margin-bottom: 2rem;
  }

  h1 {
    color: #333;
    margin-bottom: 0.5rem;
  }

  header p {
    color: #666;
  }

  .recipes {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .error {
    color: #c00;
  }

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    border-bottom: 1px solid #eee;
    padding: 1rem 0;
  }

  li:last-child {
    border-bottom: none;
  }

  h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
  }

  li p {
    margin: 0;
    color: #666;
  }
</style>
