/**
 * 📬 onTaskCreated Hook - タスク生成時の自動振り分け
 * PlannerAgentが生成したタスクを適切なSubAgentへルーティング
 * @icon 📬
 */

import mcpManager from './mcp-manager.js';

/**
 * タスクタイプに応じたSubAgentマッピング
 */
const TASK_AGENT_MAP = {
  scrape: 'ScraperAgent',
  clean: 'CleanerAgent',
  api: 'DevAPIAgent',
  ui: 'DevUIAgent',
  ocr: 'OcrAgent',
  translate: 'TranslationAgent',
  test: 'QaAgent',
  docs: 'WriterAgent',
};

/**
 * MCPを必要とするタスクタイプ
 */
const MCP_REQUIRED_TASKS = {
  scrape: ['browser', 'puppeteer'],
  ocr: ['filesystem'],
};

/**
 * タスク作成時のハンドラ
 * @param {object} task - 作成されたタスク
 * @param {object} context - コンテキスト情報
 */
export default async function onTaskCreated(task, context) {
  const { type, id, description, priority } = task;

  console.log(`[onTaskCreated] Task received: ${id} (${type})`);

  // タスクタイプに対応するAgentを取得
  const agentName = TASK_AGENT_MAP[type];
  if (!agentName) {
    console.error(`[onTaskCreated] Unknown task type: ${type}`);
    return { success: false, error: `Unknown task type: ${type}` };
  }

  // MCPが必要なタスクの場合
  if (MCP_REQUIRED_TASKS[type]) {
    const mcpTypes = MCP_REQUIRED_TASKS[type];

    for (const mcpType of mcpTypes) {
      // MCP取得を試みる（使用中なら待機）
      console.log(`[onTaskCreated] Acquiring MCP: ${mcpType}`);
      await mcpManager.acquireMCP(mcpType);
    }

    try {
      // SubAgentを実行
      const result = await executeAgent(agentName, task, context);

      return result;
    } finally {
      // MCP解放
      for (const mcpType of mcpTypes) {
        console.log(`[onTaskCreated] Releasing MCP: ${mcpType}`);
        mcpManager.releaseMCP(mcpType);
      }
    }
  }

  // MCP不要のタスクは並列実行可能
  return executeAgent(agentName, task, context);
}

/**
 * SubAgentを実行
 * @param {string} agentName - Agent名
 * @param {object} task - タスク情報
 * @param {object} context - コンテキスト
 */
async function executeAgent(agentName, task, context) {
  console.log(`[onTaskCreated] Executing ${agentName} for task: ${task.id}`);

  // 実際のAgent実行ロジックはここに実装
  // ClaudeCodeのSubAgent APIを呼び出す

  return {
    success: true,
    agent: agentName,
    taskId: task.id,
    timestamp: new Date().toISOString(),
  };
}
