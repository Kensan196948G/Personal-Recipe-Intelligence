/**
 * IndexedDB Wrapper for Personal Recipe Intelligence
 * レシピデータのローカル保存と同期キュー管理
 */

class IndexedDBManager {
  constructor(dbName = 'PRIDatabase', version = 1) {
    this.dbName = dbName;
    this.version = version;
    this.db = null;

    this.stores = {
      recipes: 'recipes',
      syncQueue: 'syncQueue',
      favorites: 'favorites',
      tags: 'tags',
      settings: 'settings'
    };
  }

  /**
   * データベースを開く
   */
  async open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => {
        console.error('[IndexedDB] Failed to open database:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('[IndexedDB] Database opened successfully');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        console.log('[IndexedDB] Upgrading database...');
        const db = event.target.result;

        // recipes ストア
        if (!db.objectStoreNames.contains(this.stores.recipes)) {
          const recipesStore = db.createObjectStore(this.stores.recipes, {
            keyPath: 'id',
            autoIncrement: true
          });
          recipesStore.createIndex('title', 'title', { unique: false });
          recipesStore.createIndex('createdAt', 'createdAt', { unique: false });
          recipesStore.createIndex('updatedAt', 'updatedAt', { unique: false });
          recipesStore.createIndex('tags', 'tags', { unique: false, multiEntry: true });
        }

        // syncQueue ストア
        if (!db.objectStoreNames.contains(this.stores.syncQueue)) {
          const syncQueueStore = db.createObjectStore(this.stores.syncQueue, {
            keyPath: 'id',
            autoIncrement: true
          });
          syncQueueStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncQueueStore.createIndex('type', 'type', { unique: false });
        }

        // favorites ストア
        if (!db.objectStoreNames.contains(this.stores.favorites)) {
          const favoritesStore = db.createObjectStore(this.stores.favorites, {
            keyPath: 'recipeId'
          });
          favoritesStore.createIndex('addedAt', 'addedAt', { unique: false });
        }

        // tags ストア
        if (!db.objectStoreNames.contains(this.stores.tags)) {
          const tagsStore = db.createObjectStore(this.stores.tags, {
            keyPath: 'name'
          });
          tagsStore.createIndex('count', 'count', { unique: false });
        }

        // settings ストア
        if (!db.objectStoreNames.contains(this.stores.settings)) {
          db.createObjectStore(this.stores.settings, {
            keyPath: 'key'
          });
        }
      };
    });
  }

  /**
   * データベースを閉じる
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
      console.log('[IndexedDB] Database closed');
    }
  }

  /**
   * トランザクションを取得
   */
  getTransaction(storeNames, mode = 'readonly') {
    if (!this.db) {
      throw new Error('[IndexedDB] Database not opened');
    }

    const stores = Array.isArray(storeNames) ? storeNames : [storeNames];
    return this.db.transaction(stores, mode);
  }

  /**
   * オブジェクトストアを取得
   */
  getStore(storeName, mode = 'readonly') {
    const transaction = this.getTransaction(storeName, mode);
    return transaction.objectStore(storeName);
  }

  /**
   * データを追加
   */
  async add(storeName, data) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readwrite');
      const request = store.add(data);

      request.onsuccess = () => {
        console.log(`[IndexedDB] Added to ${storeName}:`, request.result);
        resolve(request.result);
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to add to ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * データを更新（または追加）
   */
  async put(storeName, data) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readwrite');
      const request = store.put(data);

      request.onsuccess = () => {
        console.log(`[IndexedDB] Put to ${storeName}:`, request.result);
        resolve(request.result);
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to put to ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * データを取得
   */
  async get(storeName, key) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readonly');
      const request = store.get(key);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to get from ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * すべてのデータを取得
   */
  async getAll(storeName) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readonly');
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to get all from ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * データを削除
   */
  async delete(storeName, key) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readwrite');
      const request = store.delete(key);

      request.onsuccess = () => {
        console.log(`[IndexedDB] Deleted from ${storeName}:`, key);
        resolve();
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to delete from ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * すべてのデータを削除
   */
  async clear(storeName) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readwrite');
      const request = store.clear();

      request.onsuccess = () => {
        console.log(`[IndexedDB] Cleared ${storeName}`);
        resolve();
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to clear ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * インデックスで検索
   */
  async getByIndex(storeName, indexName, value) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readonly');
      const index = store.index(indexName);
      const request = index.getAll(value);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to get by index from ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * カーソルで検索
   */
  async query(storeName, filterFn) {
    return new Promise((resolve, reject) => {
      const store = this.getStore(storeName, 'readonly');
      const request = store.openCursor();
      const results = [];

      request.onsuccess = (event) => {
        const cursor = event.target.result;

        if (cursor) {
          if (!filterFn || filterFn(cursor.value)) {
            results.push(cursor.value);
          }
          cursor.continue();
        } else {
          resolve(results);
        }
      };

      request.onerror = () => {
        console.error(`[IndexedDB] Failed to query ${storeName}:`, request.error);
        reject(request.error);
      };
    });
  }

  /**
   * レシピを保存
   */
  async saveRecipe(recipe) {
    const data = {
      ...recipe,
      updatedAt: new Date().toISOString()
    };

    if (!data.createdAt) {
      data.createdAt = data.updatedAt;
    }

    return await this.put(this.stores.recipes, data);
  }

  /**
   * レシピを取得
   */
  async getRecipe(id) {
    return await this.get(this.stores.recipes, id);
  }

  /**
   * すべてのレシピを取得
   */
  async getAllRecipes() {
    return await this.getAll(this.stores.recipes);
  }

  /**
   * レシピを削除
   */
  async deleteRecipe(id) {
    return await this.delete(this.stores.recipes, id);
  }

  /**
   * タグで検索
   */
  async searchRecipesByTag(tag) {
    return await this.getByIndex(this.stores.recipes, 'tags', tag);
  }

  /**
   * タイトルで検索
   */
  async searchRecipesByTitle(query) {
    const recipes = await this.getAllRecipes();
    return recipes.filter((recipe) =>
      recipe.title && recipe.title.toLowerCase().includes(query.toLowerCase())
    );
  }

  /**
   * 同期キューに追加
   */
  async addToSyncQueue(type, url, method, data) {
    const queueItem = {
      type,
      url,
      method,
      data,
      timestamp: new Date().toISOString(),
      retries: 0
    };

    return await this.add(this.stores.syncQueue, queueItem);
  }

  /**
   * 同期キューを取得
   */
  async getSyncQueue() {
    return await this.getAll(this.stores.syncQueue);
  }

  /**
   * 同期キューから削除
   */
  async removeFromSyncQueue(id) {
    return await this.delete(this.stores.syncQueue, id);
  }

  /**
   * 同期キューをクリア
   */
  async clearSyncQueue() {
    return await this.clear(this.stores.syncQueue);
  }

  /**
   * お気に入りに追加
   */
  async addFavorite(recipeId) {
    const favorite = {
      recipeId,
      addedAt: new Date().toISOString()
    };

    return await this.put(this.stores.favorites, favorite);
  }

  /**
   * お気に入りから削除
   */
  async removeFavorite(recipeId) {
    return await this.delete(this.stores.favorites, recipeId);
  }

  /**
   * お気に入りを取得
   */
  async getFavorites() {
    return await this.getAll(this.stores.favorites);
  }

  /**
   * お気に入りかチェック
   */
  async isFavorite(recipeId) {
    const favorite = await this.get(this.stores.favorites, recipeId);
    return !!favorite;
  }

  /**
   * 設定を保存
   */
  async saveSetting(key, value) {
    const setting = {
      key,
      value,
      updatedAt: new Date().toISOString()
    };

    return await this.put(this.stores.settings, setting);
  }

  /**
   * 設定を取得
   */
  async getSetting(key, defaultValue = null) {
    const setting = await this.get(this.stores.settings, key);
    return setting ? setting.value : defaultValue;
  }

  /**
   * データベースの統計情報を取得
   */
  async getStats() {
    const [recipes, syncQueue, favorites, tags] = await Promise.all([
      this.getAll(this.stores.recipes),
      this.getAll(this.stores.syncQueue),
      this.getAll(this.stores.favorites),
      this.getAll(this.stores.tags)
    ]);

    return {
      recipesCount: recipes.length,
      syncQueueCount: syncQueue.length,
      favoritesCount: favorites.length,
      tagsCount: tags.length,
      lastUpdated: new Date().toISOString()
    };
  }

  /**
   * データベースをエクスポート
   */
  async exportData() {
    const [recipes, favorites, tags, settings] = await Promise.all([
      this.getAll(this.stores.recipes),
      this.getAll(this.stores.favorites),
      this.getAll(this.stores.tags),
      this.getAll(this.stores.settings)
    ]);

    return {
      version: this.version,
      exportedAt: new Date().toISOString(),
      data: {
        recipes,
        favorites,
        tags,
        settings
      }
    };
  }

  /**
   * データベースをインポート
   */
  async importData(exportedData) {
    if (!exportedData || !exportedData.data) {
      throw new Error('Invalid export data');
    }

    const { recipes, favorites, tags, settings } = exportedData.data;

    // 既存データをクリア
    await Promise.all([
      this.clear(this.stores.recipes),
      this.clear(this.stores.favorites),
      this.clear(this.stores.tags),
      this.clear(this.stores.settings)
    ]);

    // データをインポート
    const promises = [];

    if (recipes) {
      recipes.forEach((recipe) => promises.push(this.put(this.stores.recipes, recipe)));
    }

    if (favorites) {
      favorites.forEach((favorite) => promises.push(this.put(this.stores.favorites, favorite)));
    }

    if (tags) {
      tags.forEach((tag) => promises.push(this.put(this.stores.tags, tag)));
    }

    if (settings) {
      settings.forEach((setting) => promises.push(this.put(this.stores.settings, setting)));
    }

    await Promise.all(promises);

    console.log('[IndexedDB] Data imported successfully');
  }
}

// グローバルインスタンスを作成
const dbManager = new IndexedDBManager();

// 初期化
dbManager.open().catch((error) => {
  console.error('[IndexedDB] Failed to initialize:', error);
});

// エクスポート（モジュール環境の場合）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = IndexedDBManager;
}
