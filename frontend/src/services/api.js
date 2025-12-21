/**
 * API Service - Backend API communication
 */

const API_BASE = "/api/v1";

/**
 * APIリクエスト共通処理
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  };

  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "API Error");
  }

  return data;
}

/**
 * Recipe API
 */
export const recipeApi = {
  // レシピ一覧取得
  async list(params = {}) {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page);
    if (params.per_page) query.set("per_page", params.per_page);
    if (params.search) query.set("search", params.search);
    if (params.tag_id) query.set("tag_id", params.tag_id);

    const queryString = query.toString();
    const endpoint = queryString ? `/recipes?${queryString}` : "/recipes";
    return request(endpoint);
  },

  // レシピ詳細取得
  async get(id) {
    return request(`/recipes/${id}`);
  },

  // レシピ作成
  async create(recipe) {
    return request("/recipes", {
      method: "POST",
      body: JSON.stringify(recipe),
    });
  },

  // レシピ更新
  async update(id, recipe) {
    return request(`/recipes/${id}`, {
      method: "PUT",
      body: JSON.stringify(recipe),
    });
  },

  // レシピ削除
  async delete(id) {
    return request(`/recipes/${id}`, {
      method: "DELETE",
    });
  },

  // 材料追加
  async addIngredient(recipeId, ingredient) {
    return request(`/recipes/${recipeId}/ingredients`, {
      method: "POST",
      body: JSON.stringify(ingredient),
    });
  },

  // 材料更新
  async updateIngredient(recipeId, ingredientId, ingredient) {
    return request(`/recipes/${recipeId}/ingredients/${ingredientId}`, {
      method: "PUT",
      body: JSON.stringify(ingredient),
    });
  },

  // 材料削除
  async deleteIngredient(recipeId, ingredientId) {
    return request(`/recipes/${recipeId}/ingredients/${ingredientId}`, {
      method: "DELETE",
    });
  },

  // 手順追加
  async addStep(recipeId, step) {
    return request(`/recipes/${recipeId}/steps`, {
      method: "POST",
      body: JSON.stringify(step),
    });
  },

  // 手順更新
  async updateStep(recipeId, stepId, step) {
    return request(`/recipes/${recipeId}/steps/${stepId}`, {
      method: "PUT",
      body: JSON.stringify(step),
    });
  },

  // 手順削除
  async deleteStep(recipeId, stepId) {
    return request(`/recipes/${recipeId}/steps/${stepId}`, {
      method: "DELETE",
    });
  },
};

/**
 * Dashboard API
 */
export const dashboardApi = {
  // ダッシュボード統計取得
  async getStats() {
    return request("/recipes/stats/dashboard");
  },
};

/**
 * Tag API
 */
export const tagApi = {
  // タグ一覧取得
  async list() {
    return request("/tags");
  },

  // タグ取得
  async get(id) {
    return request(`/tags/${id}`);
  },

  // タグ作成
  async create(tag) {
    return request("/tags", {
      method: "POST",
      body: JSON.stringify(tag),
    });
  },

  // タグ削除
  async delete(id) {
    return request(`/tags/${id}`, {
      method: "DELETE",
    });
  },
};

/**
 * Get image URL for recipe
 * @param {Object} recipe - Recipe object with image_path or image_url
 * @returns {string|null} - Image URL or null if no image
 */
export function getImageUrl(recipe) {
  if (!recipe) return null;

  // Priority: image_path (local/backend) > image_url (external)
  if (recipe.image_path) {
    // Extract filename from path (e.g., "data/images/66_xxx.jpg" -> "66_xxx.jpg")
    const filename = recipe.image_path.split('/').pop();
    // Backend API serves images from /api/v1/recipes/images/{filename}
    return `${API_BASE}/recipes/images/${filename}`;
  }

  if (recipe.image_url) {
    return recipe.image_url;
  }

  return null;
}

/**
 * Shopping List API
 */
export const shoppingListApi = {
  // 買い物リスト一覧取得
  async list(params = {}) {
    const query = new URLSearchParams();
    if (params.include_completed) query.set("include_completed", "true");
    if (params.page) query.set("page", params.page);
    if (params.per_page) query.set("per_page", params.per_page);

    const queryString = query.toString();
    const endpoint = queryString ? `/shopping-lists?${queryString}` : "/shopping-lists";
    return request(endpoint);
  },

  // 買い物リスト詳細取得
  async get(id) {
    return request(`/shopping-lists/${id}`);
  },

  // 買い物リスト作成
  async create(data) {
    return request("/shopping-lists", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // 買い物リスト更新
  async update(id, data) {
    return request(`/shopping-lists/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  // 買い物リスト削除
  async delete(id) {
    return request(`/shopping-lists/${id}`, {
      method: "DELETE",
    });
  },

  // アイテム追加
  async addItem(listId, item) {
    return request(`/shopping-lists/${listId}/items`, {
      method: "POST",
      body: JSON.stringify(item),
    });
  },

  // アイテム更新
  async updateItem(listId, itemId, data) {
    return request(`/shopping-lists/${listId}/items/${itemId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  // アイテムチェック切替
  async toggleItem(listId, itemId) {
    return request(`/shopping-lists/${listId}/items/${itemId}/toggle`, {
      method: "POST",
    });
  },

  // アイテム削除
  async deleteItem(listId, itemId) {
    return request(`/shopping-lists/${listId}/items/${itemId}`, {
      method: "DELETE",
    });
  },

  // レシピ材料を追加
  async addRecipe(listId, recipeId, multiplier = 1.0) {
    return request(`/shopping-lists/${listId}/add-recipe/${recipeId}?multiplier=${multiplier}`, {
      method: "POST",
    });
  },

  // チェック済みをクリア
  async clearChecked(listId) {
    return request(`/shopping-lists/${listId}/clear-checked`, {
      method: "POST",
    });
  },
};
