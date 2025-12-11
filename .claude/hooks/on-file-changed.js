/**
 * onFileChanged Hook - ファイル変更時の自動同期
 * backend/frontend の変更を監視し、関連SubAgentに通知
 */

/**
 * ファイルパスパターンとAgent対応
 */
const FILE_AGENT_MAP = [
  { pattern: /^backend\/api\/.*\.py$/, agents: ['DevAPIAgent'] },
  { pattern: /^backend\/models\/.*\.py$/, agents: ['DevAPIAgent', 'DevUIAgent'] },
  { pattern: /^backend\/services\/.*\.py$/, agents: ['DevAPIAgent'] },
  { pattern: /^backend\/scraper\/.*\.py$/, agents: ['ScraperAgent'] },
  { pattern: /^backend\/ocr\/.*\.py$/, agents: ['OcrAgent'] },
  { pattern: /^backend\/translation\/.*\.py$/, agents: ['TranslationAgent'] },
  { pattern: /^frontend\/src\/.*\.svelte$/, agents: ['DevUIAgent'] },
  { pattern: /^frontend\/src\/.*\.js$/, agents: ['DevUIAgent'] },
  { pattern: /^data\/json-schema\/.*\.json$/, agents: ['DevAPIAgent', 'DevUIAgent'] },
  { pattern: /^tests\/.*\.py$/, agents: ['QaAgent'] },
  { pattern: /^docs\/.*\.md$/, agents: ['WriterAgent'] },
];

/**
 * デバウンス用のタイマー管理
 */
const debounceTimers = new Map();
const DEBOUNCE_MS = 200;

/**
 * ファイル変更時のハンドラ
 * @param {object} event - ファイル変更イベント
 * @param {object} context - コンテキスト情報
 */
export default async function onFileChanged(event, context) {
  const { filePath, changeType } = event;

  console.log(`[onFileChanged] File ${changeType}: ${filePath}`);

  // デバウンス処理
  const existingTimer = debounceTimers.get(filePath);
  if (existingTimer) {
    clearTimeout(existingTimer);
  }

  return new Promise((resolve) => {
    const timer = setTimeout(async () => {
      debounceTimers.delete(filePath);

      // マッチするAgentを検索
      const matchedAgents = [];
      for (const mapping of FILE_AGENT_MAP) {
        if (mapping.pattern.test(filePath)) {
          matchedAgents.push(...mapping.agents);
        }
      }

      // 重複を除去
      const uniqueAgents = [...new Set(matchedAgents)];

      if (uniqueAgents.length === 0) {
        console.log(`[onFileChanged] No matching agents for: ${filePath}`);
        resolve({ success: true, agents: [] });
        return;
      }

      console.log(`[onFileChanged] Notifying agents: ${uniqueAgents.join(', ')}`);

      // 各Agentに通知（MCP不要のタスクは並列実行）
      const notifications = uniqueAgents.map((agent) =>
        notifyAgent(agent, {
          type: 'file_changed',
          filePath,
          changeType,
        })
      );

      const results = await Promise.all(notifications);

      resolve({
        success: true,
        agents: uniqueAgents,
        results,
      });
    }, DEBOUNCE_MS);

    debounceTimers.set(filePath, timer);
  });
}

/**
 * Agentに変更を通知
 * @param {string} agentName - Agent名
 * @param {object} event - イベント情報
 */
async function notifyAgent(agentName, event) {
  console.log(`[onFileChanged] Notifying ${agentName}`);

  // 実際の通知ロジックはここに実装
  return {
    agent: agentName,
    notified: true,
    timestamp: new Date().toISOString(),
  };
}
