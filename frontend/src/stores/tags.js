/**
 * Tag Store - Svelte reactive store for tags
 */
import { writable } from 'svelte/store';
import { tagApi } from '../services/api.js';

// Store definitions
export const tags = writable([]);
export const loadingTags = writable(false);
export const tagError = writable(null);

/**
 * タグ一覧取得
 */
export async function fetchTags() {
  loadingTags.set(true);
  tagError.set(null);

  try {
    const response = await tagApi.list();
    if (response.status === 'ok') {
      tags.set(response.data);
    }
  } catch (e) {
    tagError.set(e.message);
    tags.set([]);
  } finally {
    loadingTags.set(false);
  }
}

/**
 * タグ作成
 */
export async function createTag(name) {
  loadingTags.set(true);
  tagError.set(null);

  try {
    const response = await tagApi.create({ name });
    if (response.status === 'ok') {
      await fetchTags();
      return response.data;
    }
  } catch (e) {
    tagError.set(e.message);
    throw e;
  } finally {
    loadingTags.set(false);
  }
}

/**
 * タグ削除
 */
export async function deleteTag(id) {
  loadingTags.set(true);
  tagError.set(null);

  try {
    const response = await tagApi.delete(id);
    if (response.status === 'ok') {
      await fetchTags();
      return true;
    }
  } catch (e) {
    tagError.set(e.message);
    throw e;
  } finally {
    loadingTags.set(false);
  }
}
