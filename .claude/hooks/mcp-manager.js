/**
 * MCP Manager - MCP同時起動制御ユーティリティ
 * Browser / Puppeteer / Filesystem の同時起動数を1に制限
 */

// MCP状態管理
const mcpState = {
  browser: { busy: false, queue: [] },
  puppeteer: { busy: false, queue: [] },
  filesystem: { busy: false, queue: [] },
};

/**
 * MCPを取得する（使用中なら待機キューに追加）
 * @param {string} type - MCP種別 (browser, puppeteer, filesystem)
 * @returns {Promise<boolean>} - 取得成功時true
 */
export async function acquireMCP(type) {
  if (!mcpState[type]) {
    throw new Error(`Unknown MCP type: ${type}`);
  }

  // Browser と Puppeteer は同時使用不可
  if (type === 'browser' && mcpState.puppeteer.busy) {
    return new Promise((resolve) => {
      mcpState[type].queue.push(resolve);
    });
  }
  if (type === 'puppeteer' && mcpState.browser.busy) {
    return new Promise((resolve) => {
      mcpState[type].queue.push(resolve);
    });
  }

  if (mcpState[type].busy) {
    return new Promise((resolve) => {
      mcpState[type].queue.push(resolve);
    });
  }

  mcpState[type].busy = true;
  return true;
}

/**
 * MCPを解放する
 * @param {string} type - MCP種別
 */
export function releaseMCP(type) {
  if (!mcpState[type]) {
    throw new Error(`Unknown MCP type: ${type}`);
  }

  mcpState[type].busy = false;

  // 待機キューから次のタスクを実行
  if (mcpState[type].queue.length > 0) {
    const nextResolve = mcpState[type].queue.shift();
    mcpState[type].busy = true;
    nextResolve(true);
  }
}

/**
 * MCPが使用中かどうか確認
 * @param {string} type - MCP種別（省略時は全体）
 * @returns {boolean}
 */
export function isMcpBusy(type = null) {
  if (type) {
    return mcpState[type]?.busy || false;
  }
  return Object.values(mcpState).some((state) => state.busy);
}

/**
 * タスクをキューに追加
 * @param {string} type - MCP種別
 * @param {object} task - タスク情報
 */
export function queueTask(type, task) {
  if (!mcpState[type]) {
    throw new Error(`Unknown MCP type: ${type}`);
  }
  mcpState[type].queue.push(task);
}

/**
 * 次のタスクを取得
 * @param {string} type - MCP種別
 * @returns {object|null}
 */
export function nextTask(type) {
  if (!mcpState[type]) {
    throw new Error(`Unknown MCP type: ${type}`);
  }
  return mcpState[type].queue.shift() || null;
}

/**
 * MCP状態の取得
 * @returns {object}
 */
export function getMcpStatus() {
  return {
    browser: {
      busy: mcpState.browser.busy,
      queueLength: mcpState.browser.queue.length,
    },
    puppeteer: {
      busy: mcpState.puppeteer.busy,
      queueLength: mcpState.puppeteer.queue.length,
    },
    filesystem: {
      busy: mcpState.filesystem.busy,
      queueLength: mcpState.filesystem.queue.length,
    },
  };
}

export default {
  acquireMCP,
  releaseMCP,
  isMcpBusy,
  queueTask,
  nextTask,
  getMcpStatus,
};
