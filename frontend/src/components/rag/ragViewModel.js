/**
 * @file ragViewModel.js
 * @brief 将 RagAnswer contract 转换为前端安全展示模型。
 */

const FORBIDDEN_KEYS = new Set(['answer_quality']);

export const RAG_MODE_LABELS = {
  llm_only: 'LLM-only',
  basic_rag: 'Basic RAG',
  optimized_rag: 'Optimized RAG',
};

const RAG_MODE_ORDER = ['llm_only', 'basic_rag', 'optimized_rag'];

/**
 * @brief 深度移除前端禁止展示的隐藏评测字段。
 * @param {unknown} value 任意 contract 或扩展数据。
 * @returns {unknown} 不包含隐藏评测字段的安全数据。
 */
export const removeForbiddenFields = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => removeForbiddenFields(item));
  }

  if (!value || typeof value !== 'object') {
    return value;
  }

  return Object.entries(value).reduce((safeObject, [key, nestedValue]) => {
    if (FORBIDDEN_KEYS.has(key)) {
      return safeObject;
    }
    return {
      ...safeObject,
      [key]: removeForbiddenFields(nestedValue),
    };
  }, {});
};

/**
 * @brief 把 RagAnswer 标准字段整理为组件可直接读取的结构。
 * @param {object | null | undefined} answer RagAnswer 序列化对象。
 * @returns {object} 安全展示模型。
 */
export const createSafeRagAnswerViewModel = (answer) => {
  const safeAnswer = removeForbiddenFields(answer || {});

  return {
    contractVersion: safeAnswer.contract_version || 'unknown',
    answerMarkdown: safeAnswer.answer_markdown || '',
    warnings: Array.isArray(safeAnswer.warnings) ? safeAnswer.warnings : [],
    citations: Array.isArray(safeAnswer.citations) ? safeAnswer.citations : [],
    retrievedHits: Array.isArray(safeAnswer.retrieved_hits) ? safeAnswer.retrieved_hits : [],
    trace: Array.isArray(safeAnswer.trace) ? safeAnswer.trace : [],
    metadata: safeAnswer.metadata || {},
  };
};

/**
 * @brief 构造三模式评测表行，并固定展示顺序。
 * @param {object} summary 三模式评测摘要。
 * @returns {Array<object>} 表格行。
 */
export const buildEvaluationRows = (summary = {}) =>
  RAG_MODE_ORDER.map((mode) => ({
    mode,
    label: RAG_MODE_LABELS[mode],
    ...(summary[mode] || {}),
  }));

/**
 * @brief 将数值耗时格式化为毫秒。
 * @param {number | string | null | undefined} value 原始耗时。
 * @returns {string} 前端展示文本。
 */
export const formatLatency = (value) => {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return '-';
  }
  return `${numericValue.toFixed(numericValue >= 10 ? 0 : 1)} ms`;
};

/**
 * @brief 将检索相关性分数格式化为定长小数。
 * @param {number | string | null | undefined} value 原始分数。
 * @returns {string} 前端展示文本。
 */
export const formatScore = (value) => {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return '-';
  }
  return numericValue.toFixed(3);
};
