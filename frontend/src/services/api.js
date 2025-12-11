/**
 * API Service - Backend API communication
 */

const API_BASE = '/api/v1';

/**
 * APIリクエスト共通処理
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'API Error');
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
    if (params.page) query.set('page', params.page);
    if (params.per_page) query.set('per_page', params.per_page);
    if (params.search) query.set('search', params.search);
    if (params.tag_id) query.set('tag_id', params.tag_id);

    const queryString = query.toString();
    const endpoint = queryString ? `/recipes?${queryString}` : '/recipes';
    return request(endpoint);
  },

  // レシピ詳細取得
  async get(id) {
    return request(`/recipes/${id}`);
  },

  // レシピ作成
  async create(recipe) {
    return request('/recipes', {
      method: 'POST',
      body: JSON.stringify(recipe),
    });
  },

  // レシピ更新
  async update(id, recipe) {
    return request(`/recipes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(recipe),
    });
  },

  // レシピ削除
  async delete(id) {
    return request(`/recipes/${id}`, {
      method: 'DELETE',
    });
  },

  // 材料追加
  async addIngredient(recipeId, ingredient) {
    return request(`/recipes/${recipeId}/ingredients`, {
      method: 'POST',
      body: JSON.stringify(ingredient),
    });
  },

  // 材料更新
  async updateIngredient(recipeId, ingredientId, ingredient) {
    return request(`/recipes/${recipeId}/ingredients/${ingredientId}`, {
      method: 'PUT',
      body: JSON.stringify(ingredient),
    });
  },

  // 材料削除
  async deleteIngredient(recipeId, ingredientId) {
    return request(`/recipes/${recipeId}/ingredients/${ingredientId}`, {
      method: 'DELETE',
    });
  },

  // 手順追加
  async addStep(recipeId, step) {
    return request(`/recipes/${recipeId}/steps`, {
      method: 'POST',
      body: JSON.stringify(step),
    });
  },

  // 手順更新
  async updateStep(recipeId, stepId, step) {
    return request(`/recipes/${recipeId}/steps/${stepId}`, {
      method: 'PUT',
      body: JSON.stringify(step),
    });
  },

  // 手順削除
  async deleteStep(recipeId, stepId) {
    return request(`/recipes/${recipeId}/steps/${stepId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Tag API
 */
export const tagApi = {
  // タグ一覧取得
  async list() {
    return request('/tags');
  },

  // タグ取得
  async get(id) {
    return request(`/tags/${id}`);
  },

  // タグ作成
  async create(tag) {
    return request('/tags', {
      method: 'POST',
      body: JSON.stringify(tag),
    });
  },

  // タグ削除
  async delete(id) {
    return request(`/tags/${id}`, {
      method: 'DELETE',
    });
  },
};
