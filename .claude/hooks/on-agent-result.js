/**
 * ⛓ onAgentResult Hook - Agent完了時の連鎖処理
 * SubAgentの結果に基づいて次のAgentを自動起動
 * @icon ⛓
 */

import mcpManager from './mcp-manager.js';

/**
 * Agent連鎖マッピング
 * fromAgent → toAgents
 */
const AGENT_CHAIN_MAP = {
  ScraperAgent: {
    next: ['TranslationAgent', 'CleanerAgent'],
    condition: (result) => {
      // 海外サイトの場合はTranslationAgentを経由
      if (result.language && result.language !== 'ja') {
        return ['TranslationAgent'];
      }
      return ['CleanerAgent'];
    },
  },
  OcrAgent: {
    next: ['CleanerAgent'],
  },
  TranslationAgent: {
    next: ['CleanerAgent'],
  },
  CleanerAgent: {
    next: ['DevAPIAgent', 'DevUIAgent'],
    parallel: true, // 並列実行
  },
  DevAPIAgent: {
    next: ['QaAgent'],
    triggers: ['schema_change', 'endpoint_change'],
  },
  DevUIAgent: {
    next: ['QaAgent'],
    triggers: ['component_change'],
  },
  QaAgent: {
    next: ['WriterAgent'],
  },
  WriterAgent: {
    next: [], // 終端
  },
};

/**
 * Agent結果受信時のハンドラ
 * @param {object} result - Agentの実行結果
 * @param {object} context - コンテキスト情報
 */
export default async function onAgentResult(result, context) {
  const { agent, success, data, taskId } = result;

  console.log(`[onAgentResult] Result from ${agent}: ${success ? 'success' : 'failed'}`);

  if (!success) {
    console.error(`[onAgentResult] Agent ${agent} failed:`, result.error);
    return { success: false, error: result.error };
  }

  // 連鎖マッピングを取得
  const chainConfig = AGENT_CHAIN_MAP[agent];
  if (!chainConfig || chainConfig.next.length === 0) {
    console.log(`[onAgentResult] No chain defined for ${agent}`);
    return { success: true, chainComplete: true };
  }

  // 条件付きルーティング
  let nextAgents = chainConfig.next;
  if (chainConfig.condition) {
    nextAgents = chainConfig.condition(data);
  }

  console.log(`[onAgentResult] Chaining to: ${nextAgents.join(', ')}`);

  // MCPが必要なAgentの確認
  const mcpAgents = ['ScraperAgent', 'OcrAgent'];
  const needsMcp = nextAgents.some((a) => mcpAgents.includes(a));

  if (needsMcp) {
    // MCP必要な場合は直列実行
    const results = [];
    for (const nextAgent of nextAgents) {
      const agentResult = await executeChainedAgent(nextAgent, data, context);
      results.push(agentResult);
    }
    return { success: true, results };
  }

  // 並列実行可能な場合
  if (chainConfig.parallel) {
    const promises = nextAgents.map((nextAgent) =>
      executeChainedAgent(nextAgent, data, context)
    );
    const results = await Promise.all(promises);
    return { success: true, results };
  }

  // デフォルトは順次実行
  const results = [];
  for (const nextAgent of nextAgents) {
    const agentResult = await executeChainedAgent(nextAgent, data, context);
    results.push(agentResult);
  }

  return { success: true, results };
}

/**
 * 連鎖Agentを実行
 * @param {string} agentName - Agent名
 * @param {object} inputData - 入力データ
 * @param {object} context - コンテキスト
 */
async function executeChainedAgent(agentName, inputData, context) {
  console.log(`[onAgentResult] Executing chained agent: ${agentName}`);

  // 実際のAgent実行ロジックはここに実装
  return {
    agent: agentName,
    executed: true,
    timestamp: new Date().toISOString(),
  };
}
