/**
 * Recipe Store - Svelte reactive store for recipes
 */
import { writable, derived } from "svelte/store";
import { recipeApi } from "../services/api.js";

// Store definitions
export const recipes = writable([]);
export const currentRecipe = writable(null);
export const loading = writable(false);
export const error = writable(null);
export const pagination = writable({
  page: 1,
  per_page: 20,
  total: 0,
  total_pages: 0,
});
export const searchQuery = writable("");
export const selectedTagId = writable(null);

// Derived stores
export const hasRecipes = derived(recipes, ($recipes) => $recipes.length > 0);

/**
 * レシピ一覧取得
 */
export async function fetchRecipes(params = {}) {
  loading.set(true);
  error.set(null);

  try {
    const response = await recipeApi.list(params);
    if (response.status === "ok") {
      recipes.set(response.data.items);
      pagination.set({
        page: response.data.page,
        per_page: response.data.per_page,
        total: response.data.total,
        total_pages: response.data.total_pages,
      });
    }
  } catch (e) {
    error.set(e.message);
    recipes.set([]);
  } finally {
    loading.set(false);
  }
}

/**
 * レシピ詳細取得
 */
export async function fetchRecipe(id) {
  loading.set(true);
  error.set(null);

  try {
    const response = await recipeApi.get(id);
    if (response.status === "ok") {
      currentRecipe.set(response.data);
      return response.data;
    }
  } catch (e) {
    error.set(e.message);
    currentRecipe.set(null);
  } finally {
    loading.set(false);
  }
}

/**
 * レシピ作成
 */
export async function createRecipe(recipe) {
  loading.set(true);
  error.set(null);

  try {
    const response = await recipeApi.create(recipe);
    if (response.status === "ok") {
      await fetchRecipes();
      return response.data;
    }
  } catch (e) {
    error.set(e.message);
    throw e;
  } finally {
    loading.set(false);
  }
}

/**
 * レシピ更新
 */
export async function updateRecipe(id, recipe) {
  loading.set(true);
  error.set(null);

  try {
    const response = await recipeApi.update(id, recipe);
    if (response.status === "ok") {
      await fetchRecipes();
      return response.data;
    }
  } catch (e) {
    error.set(e.message);
    throw e;
  } finally {
    loading.set(false);
  }
}

/**
 * レシピ削除
 */
export async function deleteRecipe(id) {
  loading.set(true);
  error.set(null);

  try {
    const response = await recipeApi.delete(id);
    if (response.status === "ok") {
      await fetchRecipes();
      return true;
    }
  } catch (e) {
    error.set(e.message);
    throw e;
  } finally {
    loading.set(false);
  }
}

/**
 * 検索実行
 */
export async function searchRecipes(query) {
  searchQuery.set(query);
  await fetchRecipes({ search: query });
}

/**
 * タグでフィルタ
 */
export async function filterByTag(tagId) {
  selectedTagId.set(tagId);
  await fetchRecipes({ tag_id: tagId });
}

/**
 * ページ変更
 */
export async function changePage(page) {
  let params = { page };
  const query = searchQuery;
  const tagId = selectedTagId;

  if (query) params.search = query;
  if (tagId) params.tag_id = tagId;

  await fetchRecipes(params);
}
