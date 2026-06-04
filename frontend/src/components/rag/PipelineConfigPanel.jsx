/**
 * @file PipelineConfigPanel.jsx
 * @brief 配置 RAG 展示请求的模式、检索数量和模型信息。
 */
import PropTypes from 'prop-types';

const RAG_MODES = [
  { value: 'llm_only', label: 'LLM-only' },
  { value: 'basic_rag', label: 'Basic RAG' },
  { value: 'optimized_rag', label: 'Optimized RAG' },
];

/**
 * @brief 渲染 RAG pipeline 配置控件。
 * @param {object} props 组件属性。
 * @returns {JSX.Element} 配置面板。
 */
const PipelineConfigPanel = ({
  config,
  onConfigChange,
  onUseMockAnswer,
  onMirrorGeneratedAnswer,
  hasGeneratedAnswer,
}) => {
  const updateConfig = (key, value) => {
    onConfigChange({ ...config, [key]: value });
  };

  return (
    <section className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Pipeline 配置</h3>
        <p className="text-xs text-gray-500">只生成前端请求配置，不读取后端私有文件。</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">RAG 模式</label>
          <select
            value={config.ragMode}
            onChange={(event) => updateConfig('ragMode', event.target.value)}
            className="mt-1 block w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm"
          >
            {RAG_MODES.map((mode) => (
              <option key={mode.value} value={mode.value}>
                {mode.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Top K：{config.topK}</label>
          <input
            type="range"
            min="1"
            max="10"
            value={config.topK}
            onChange={(event) => updateConfig('topK', Number(event.target.value))}
            className="mt-2 block w-full"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Provider</label>
            <input
              value={config.provider}
              onChange={(event) => updateConfig('provider', event.target.value)}
              className="mt-1 block w-full rounded border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Model</label>
            <input
              value={config.model}
              onChange={(event) => updateConfig('model', event.target.value)}
              className="mt-1 block w-full rounded border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Collection</label>
          <input
            value={config.collectionId}
            onChange={(event) => updateConfig('collectionId', event.target.value)}
            className="mt-1 block w-full rounded border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        <div className="grid grid-cols-1 gap-2">
          <button
            type="button"
            onClick={onUseMockAnswer}
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            使用课程 QA Mock
          </button>
          <button
            type="button"
            onClick={onMirrorGeneratedAnswer}
            disabled={!hasGeneratedAnswer}
            className="rounded bg-gray-800 px-4 py-2 text-sm font-medium text-white hover:bg-gray-900 disabled:bg-gray-300"
          >
            映射当前生成结果
          </button>
        </div>
      </div>
    </section>
  );
};

PipelineConfigPanel.propTypes = {
  config: PropTypes.shape({
    ragMode: PropTypes.string.isRequired,
    topK: PropTypes.number.isRequired,
    provider: PropTypes.string.isRequired,
    model: PropTypes.string.isRequired,
    collectionId: PropTypes.string.isRequired,
  }).isRequired,
  onConfigChange: PropTypes.func.isRequired,
  onUseMockAnswer: PropTypes.func.isRequired,
  onMirrorGeneratedAnswer: PropTypes.func.isRequired,
  hasGeneratedAnswer: PropTypes.bool.isRequired,
};

export default PipelineConfigPanel;
