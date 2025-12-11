/**
 * API Service Tests
 */
import { describe, test, expect, vi, beforeEach } from 'vitest';

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

// Import after mocking
const { recipeApi, tagApi } = await import('../src/services/api.js');

describe('Recipe API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('list recipes', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          status: 'ok',
          data: {
            items: [],
            total: 0,
            page: 1,
            per_page: 20,
            total_pages: 1,
          },
        }),
    });

    const result = await recipeApi.list();
    expect(result.status).toBe('ok');
    expect(result.data.items).toEqual([]);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  test('list recipes with params', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          status: 'ok',
          data: { items: [], total: 0, page: 2, per_page: 10, total_pages: 1 },
        }),
    });

    await recipeApi.list({ page: 2, per_page: 10, search: 'カレー' });
    expect(mockFetch).toHaveBeenCalledTimes(1);

    const callUrl = mockFetch.mock.calls[0][0];
    expect(callUrl).toContain('page=2');
    expect(callUrl).toContain('per_page=10');
    expect(callUrl).toContain('search=');
  });

  test('get recipe', async () => {
    const mockRecipe = {
      id: 1,
      title: 'Test Recipe',
      ingredients: [],
      steps: [],
      tags: [],
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', data: mockRecipe }),
    });

    const result = await recipeApi.get(1);
    expect(result.status).toBe('ok');
    expect(result.data.id).toBe(1);
    expect(result.data.title).toBe('Test Recipe');
  });

  test('create recipe', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({ status: 'ok', data: { id: 1, title: 'New Recipe' } }),
    });

    const result = await recipeApi.create({
      title: 'New Recipe',
      source_type: 'manual',
    });
    expect(result.status).toBe('ok');
    expect(result.data.title).toBe('New Recipe');

    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe('POST');
    expect(JSON.parse(options.body).title).toBe('New Recipe');
  });

  test('update recipe', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          status: 'ok',
          data: { id: 1, title: 'Updated Recipe' },
        }),
    });

    const result = await recipeApi.update(1, { title: 'Updated Recipe' });
    expect(result.status).toBe('ok');
    expect(result.data.title).toBe('Updated Recipe');

    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe('PUT');
  });

  test('delete recipe', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', data: { deleted: true } }),
    });

    const result = await recipeApi.delete(1);
    expect(result.status).toBe('ok');
    expect(result.data.deleted).toBe(true);

    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe('DELETE');
  });

  test('handles API error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Recipe not found' }),
    });

    await expect(recipeApi.get(999)).rejects.toThrow('Recipe not found');
  });
});

describe('Tag API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('list tags', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          status: 'ok',
          data: [
            { id: 1, name: '和食' },
            { id: 2, name: '洋食' },
          ],
        }),
    });

    const result = await tagApi.list();
    expect(result.status).toBe('ok');
    expect(result.data.length).toBe(2);
    expect(result.data[0].name).toBe('和食');
  });

  test('create tag', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({ status: 'ok', data: { id: 1, name: '中華' } }),
    });

    const result = await tagApi.create({ name: '中華' });
    expect(result.status).toBe('ok');
    expect(result.data.name).toBe('中華');

    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe('POST');
  });

  test('delete tag', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', data: { deleted: true } }),
    });

    const result = await tagApi.delete(1);
    expect(result.status).toBe('ok');
    expect(result.data.deleted).toBe(true);

    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe('DELETE');
  });
});
