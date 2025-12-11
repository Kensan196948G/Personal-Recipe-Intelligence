<script>
  import { createEventDispatcher } from 'svelte';
  import { createRecipe, updateRecipe, fetchRecipe } from '../stores/recipes.js';
  import { tags, fetchTags } from '../stores/tags.js';
  import { onMount } from 'svelte';

  export let recipe = null;
  export let mode = 'create';

  const dispatch = createEventDispatcher();

  let formData = {
    title: '',
    description: '',
    servings: null,
    prep_time_minutes: null,
    cook_time_minutes: null,
    source_url: '',
    source_type: 'manual',
    ingredients: [],
    steps: [],
    tag_ids: [],
  };

  let saving = false;
  let formError = null;

  onMount(async () => {
    await fetchTags();
    if (recipe && mode === 'edit') {
      const detail = await fetchRecipe(recipe.id);
      if (detail) {
        formData = {
          title: detail.title || '',
          description: detail.description || '',
          servings: detail.servings,
          prep_time_minutes: detail.prep_time_minutes,
          cook_time_minutes: detail.cook_time_minutes,
          source_url: detail.source_url || '',
          source_type: detail.source_type || 'manual',
          ingredients: detail.ingredients || [],
          steps: detail.steps || [],
          tag_ids: detail.tags ? detail.tags.map((t) => t.id) : [],
        };
      }
    }
  });

  function handleBack() {
    dispatch('back');
  }

  async function handleSubmit() {
    if (!formData.title.trim()) {
      formError = 'タイトルは必須です';
      return;
    }

    saving = true;
    formError = null;

    try {
      const data = {
        title: formData.title,
        description: formData.description || null,
        servings: formData.servings || null,
        prep_time_minutes: formData.prep_time_minutes || null,
        cook_time_minutes: formData.cook_time_minutes || null,
        source_url: formData.source_url || null,
        source_type: formData.source_type,
      };

      if (mode === 'create') {
        data.ingredients = formData.ingredients.map((i, idx) => ({
          name: i.name,
          amount: i.amount || null,
          unit: i.unit || null,
          note: i.note || null,
          order: idx,
        }));
        data.steps = formData.steps.map((s, idx) => ({
          description: s.description,
          order: idx + 1,
        }));
        data.tag_ids = formData.tag_ids;

        await createRecipe(data);
      } else {
        await updateRecipe(recipe.id, data);
      }

      dispatch('saved');
    } catch (e) {
      formError = e.message;
    } finally {
      saving = false;
    }
  }

  function addIngredient() {
    formData.ingredients = [
      ...formData.ingredients,
      { name: '', amount: null, unit: '', note: '' },
    ];
  }

  function removeIngredient(index) {
    formData.ingredients = formData.ingredients.filter((_, i) => i !== index);
  }

  function addStep() {
    formData.steps = [...formData.steps, { description: '' }];
  }

  function removeStep(index) {
    formData.steps = formData.steps.filter((_, i) => i !== index);
  }

  function toggleTag(tagId) {
    if (formData.tag_ids.includes(tagId)) {
      formData.tag_ids = formData.tag_ids.filter((id) => id !== tagId);
    } else {
      formData.tag_ids = [...formData.tag_ids, tagId];
    }
  }
</script>

<div class="recipe-form">
  <div class="header">
    <button class="back-btn" on:click={handleBack}>← 戻る</button>
    <h2>{mode === 'create' ? '新規レシピ作成' : 'レシピ編集'}</h2>
  </div>

  <form on:submit|preventDefault={handleSubmit}>
    {#if formError}
      <div class="error">{formError}</div>
    {/if}

    <div class="form-group">
      <label for="title">タイトル *</label>
      <input type="text" id="title" bind:value={formData.title} required />
    </div>

    <div class="form-group">
      <label for="description">説明</label>
      <textarea id="description" bind:value={formData.description} rows="3"></textarea>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="servings">人数</label>
        <input type="number" id="servings" bind:value={formData.servings} min="1" />
      </div>
      <div class="form-group">
        <label for="prep_time">準備時間（分）</label>
        <input
          type="number"
          id="prep_time"
          bind:value={formData.prep_time_minutes}
          min="0"
        />
      </div>
      <div class="form-group">
        <label for="cook_time">調理時間（分）</label>
        <input
          type="number"
          id="cook_time"
          bind:value={formData.cook_time_minutes}
          min="0"
        />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="source_type">取得元</label>
        <select id="source_type" bind:value={formData.source_type}>
          <option value="manual">手動入力</option>
          <option value="web">Web</option>
          <option value="ocr">OCR</option>
        </select>
      </div>
      <div class="form-group flex-1">
        <label for="source_url">URL</label>
        <input type="url" id="source_url" bind:value={formData.source_url} />
      </div>
    </div>

    {#if $tags.length > 0}
      <div class="form-group">
        <span class="label-text">タグ</span>
        <div class="tag-list" role="group" aria-label="タグ選択">
          {#each $tags as tag}
            <button
              type="button"
              class="tag-btn"
              class:selected={formData.tag_ids.includes(tag.id)}
              on:click={() => toggleTag(tag.id)}
            >
              {tag.name}
            </button>
          {/each}
        </div>
      </div>
    {/if}

    {#if mode === 'create'}
      <section class="form-section">
        <div class="section-header">
          <h3>材料</h3>
          <button type="button" class="add-btn" on:click={addIngredient}>+ 追加</button>
        </div>
        {#each formData.ingredients as ingredient, i}
          <div class="ingredient-row">
            <input type="text" placeholder="名前" bind:value={ingredient.name} />
            <input
              type="number"
              placeholder="量"
              bind:value={ingredient.amount}
              step="0.1"
            />
            <input type="text" placeholder="単位" bind:value={ingredient.unit} />
            <input type="text" placeholder="備考" bind:value={ingredient.note} />
            <button type="button" class="remove-btn" on:click={() => removeIngredient(i)}>
              ×
            </button>
          </div>
        {/each}
      </section>

      <section class="form-section">
        <div class="section-header">
          <h3>手順</h3>
          <button type="button" class="add-btn" on:click={addStep}>+ 追加</button>
        </div>
        {#each formData.steps as step, i}
          <div class="step-row">
            <span class="step-number">{i + 1}.</span>
            <textarea placeholder="手順を入力..." bind:value={step.description} rows="2"
            ></textarea>
            <button type="button" class="remove-btn" on:click={() => removeStep(i)}>×</button>
          </div>
        {/each}
      </section>
    {/if}

    <div class="form-actions">
      <button type="button" on:click={handleBack}>キャンセル</button>
      <button type="submit" class="btn-primary" disabled={saving}>
        {saving ? '保存中...' : '保存'}
      </button>
    </div>
  </form>
</div>

<style>
  .recipe-form {
    max-width: 800px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .header h2 {
    margin: 0;
    flex: 1;
  }

  .back-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
  }

  form {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .error {
    background: #ffe6e6;
    border: 1px solid #c00;
    color: #c00;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-row {
    display: flex;
    gap: 1rem;
  }

  .form-row .form-group {
    flex: 1;
  }

  .flex-1 {
    flex: 2 !important;
  }

  label,
  .label-text {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
  }

  input,
  select,
  textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  textarea {
    resize: vertical;
  }

  .tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .tag-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 16px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .tag-btn.selected {
    background: #0077aa;
    color: white;
    border-color: #0077aa;
  }

  .form-section {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .section-header h3 {
    margin: 0;
    color: #333;
  }

  .add-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #0077aa;
    border-radius: 4px;
    background: white;
    color: #0077aa;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .add-btn:hover {
    background: #e8f4f8;
  }

  .ingredient-row,
  .step-row {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    align-items: flex-start;
  }

  .ingredient-row input:first-child {
    flex: 2;
  }

  .ingredient-row input:nth-child(2),
  .ingredient-row input:nth-child(3) {
    flex: 0.75;
  }

  .ingredient-row input:nth-child(4) {
    flex: 1.5;
  }

  .step-row {
    align-items: flex-start;
  }

  .step-number {
    font-weight: bold;
    color: #0077aa;
    padding-top: 0.5rem;
  }

  .step-row textarea {
    flex: 1;
  }

  .remove-btn {
    padding: 0.5rem;
    border: 1px solid #c00;
    border-radius: 4px;
    background: white;
    color: #c00;
    cursor: pointer;
    font-size: 1rem;
    line-height: 1;
  }

  .remove-btn:hover {
    background: #ffe6e6;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
  }

  .form-actions button {
    padding: 0.75rem 1.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 1rem;
  }

  .btn-primary {
    background: #0077aa;
    color: white;
    border-color: #0077aa;
  }

  .btn-primary:hover:not(:disabled) {
    background: #005580;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
