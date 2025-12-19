/**
 * 📡 onMcpEvent Hook - MCPイベント処理
 * Browser / Puppeteer / Filesystem の状態を監視・制御
 * @icon 📡
 */

import mcpManager from './mcp-manager.js';

/**
 * MCPイベントタイプ
 */
const MCP_EVENT_TYPES = {
  STARTED: 'started',
  COMPLETED: 'completed',
  ERROR: 'error',
  TIMEOUT: 'timeout',
  IDLE: 'idle',
};

/**
 * MCP設定
 */
const MCP_CONFIG = {
  browser: {
    maxRetries: 1,
    timeoutMs: 30000,
  },
  puppeteer: {
    maxRetries: 1,
    timeoutMs: 30000,
  },
  filesystem: {
    maxRetries: 1,
    timeoutMs: 10000,
  },
};

/**
 * MCPイベントハンドラ
 * @param {object} event - MCPイベント
 * @param {object} context - コンテキスト情報
 */
export default async function onMcpEvent(event, context) {
  const { type, mcpType, data, error } = event;

  console.log(`[onMcpEvent] Event: ${type} for MCP: ${mcpType}`);

  switch (type) {
    case MCP_EVENT_TYPES.STARTED:
      return handleMcpStarted(mcpType, data);

    case MCP_EVENT_TYPES.COMPLETED:
      return handleMcpCompleted(mcpType, data);

    case MCP_EVENT_TYPES.ERROR:
      return handleMcpError(mcpType, error, context);

    case MCP_EVENT_TYPES.TIMEOUT:
      return handleMcpTimeout(mcpType, context);

    case MCP_EVENT_TYPES.IDLE:
      return handleMcpIdle(mcpType);

    default:
      console.warn(`[onMcpEvent] Unknown event type: ${type}`);
      return { success: false, error: `Unknown event type: ${type}` };
  }
}

/**
 * MCP開始時の処理
 */
function handleMcpStarted(mcpType, data) {
  console.log(`[onMcpEvent] MCP ${mcpType} started`);

  // Browser と Puppeteer の同時起動チェック
  if (mcpType === 'browser' && mcpManager.isMcpBusy('puppeteer')) {
    console.error('[onMcpEvent] VIOLATION: Browser started while Puppeteer is busy!');
    return { success: false, error: 'MCP concurrency violation' };
  }
  if (mcpType === 'puppeteer' && mcpManager.isMcpBusy('browser')) {
    console.error('[onMcpEvent] VIOLATION: Puppeteer started while Browser is busy!');
    return { success: false, error: 'MCP concurrency violation' };
  }

  return { success: true };
}

/**
 * MCP完了時の処理
 */
function handleMcpCompleted(mcpType, data) {
  console.log(`[onMcpEvent] MCP ${mcpType} completed`);

  // 結果を適切なAgentへルーティング
  const routingMap = {
    browser: 'ScraperAgent',
    puppeteer: 'ScraperAgent',
    filesystem: 'OcrAgent',
  };

  const targetAgent = routingMap[mcpType];

  return {
    success: true,
    routeTo: targetAgent,
    data,
  };
}

/**
 * MCPエラー時の処理
 */
async function handleMcpError(mcpType, error, context) {
  console.error(`[onMcpEvent] MCP ${mcpType} error:`, error);

  const config = MCP_CONFIG[mcpType];
  const retryCount = context.retryCount || 0;

  if (retryCount < config.maxRetries) {
    console.log(`[onMcpEvent] Retrying MCP ${mcpType} (attempt ${retryCount + 1})`);

    // リトライ実行
    return {
      success: false,
      retry: true,
      retryCount: retryCount + 1,
    };
  }

  console.error(`[onMcpEvent] MCP ${mcpType} failed after ${config.maxRetries} retries`);

  // MCPを解放
  mcpManager.releaseMCP(mcpType);

  return {
    success: false,
    error: `MCP ${mcpType} failed: ${error.message || error}`,
  };
}

/**
 * MCPタイムアウト時の処理
 */
function handleMcpTimeout(mcpType, context) {
  console.warn(`[onMcpEvent] MCP ${mcpType} timeout`);

  // MCPを強制解放
  mcpManager.releaseMCP(mcpType);

  return {
    success: false,
    error: `MCP ${mcpType} timeout`,
  };
}

/**
 * MCPアイドル時の処理
 */
function handleMcpIdle(mcpType) {
  console.log(`[onMcpEvent] MCP ${mcpType} idle - auto stopping`);

  // MCPを解放
  mcpManager.releaseMCP(mcpType);

  // キューに待機中のタスクがあれば実行
  const nextTask = mcpManager.nextTask(mcpType);
  if (nextTask) {
    console.log(`[onMcpEvent] Processing queued task for ${mcpType}`);
    return {
      success: true,
      processNext: true,
      task: nextTask,
    };
  }

  return { success: true };
}

/**
 * MCP状態の取得
 */
export function getMcpStatus() {
  return mcpManager.getMcpStatus();
}
