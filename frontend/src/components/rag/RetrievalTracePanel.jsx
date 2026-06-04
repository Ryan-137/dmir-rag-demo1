/**
 * @file RetrievalTracePanel.jsx
 * @brief 展示 RagAnswer 的检索命中、引用和流水线 trace。
 */
/* eslint-disable react/prop-types */
import { formatLatency, formatScore } from './ragViewModel';

const renderListValue = (value) => {
  if (Array.isArray(value)) {
    return value.filter(Boolean).join(' / ') || '-';
  }
  return value || '-';
};

const renderJsonSummary = (value) => {
  if (!value || Object.keys(value).length === 0) {
    return '-';
  }
  return JSON.stringify(value);
};

/**
 * @brief 渲染检索命中、引用和阶段追踪。
 * @param {{retrievedHits: Array<object>, citations: Array<object>, trace: Array<object>}} props 组件属性。
 * @returns {JSX.Element} 检索证据与 trace 面板。
 */
const RetrievalTracePanel = ({ retrievedHits = [], citations = [], trace = [] }) => (
  <section className="rounded-lg border bg-white p-4 shadow-sm">
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">证据与 Trace</h3>
        <p className="text-xs text-gray-500">同一组件支持课程 QA 和论文语料。</p>
      </div>
      <div className="flex gap-2 text-xs text-gray-600">
        <span className="rounded-full bg-gray-100 px-2 py-1">Hits {retrievedHits.length}</span>
        <span className="rounded-full bg-gray-100 px-2 py-1">Citations {citations.length}</span>
        <span className="rounded-full bg-gray-100 px-2 py-1">Trace {trace.length}</span>
      </div>
    </div>

    <div className="grid gap-4 xl:grid-cols-2">
      <div>
        <h4 className="mb-2 text-sm font-semibold text-gray-800">检索命中</h4>
        <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
          {retrievedHits.length > 0 ? (
            retrievedHits.map((hit) => (
              <article key={`${hit.chunk_id}-${hit.rank}`} className="rounded-md border bg-gray-50 p-3">
                <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-xs text-gray-600">
                  <span className="font-semibold text-blue-700">#{hit.rank || '-'} score {formatScore(hit.score)}</span>
                  <span>{hit.source || '-'}</span>
                </div>
                <p className="whitespace-pre-wrap text-sm text-gray-800">{hit.text}</p>
                <div className="mt-2 grid gap-1 text-xs text-gray-500">
                  <span>问题：{hit.metadata?.question || '-'}</span>
                  <span>页码：{renderListValue(hit.metadata?.page_numbers || hit.metadata?.page_number)}</span>
                  <span>章节：{renderListValue(hit.metadata?.section_path)}</span>
                  <span>类型：{hit.metadata?.block_type || hit.metadata?.block_types || '-'}</span>
                </div>
              </article>
            ))
          ) : (
            <div className="rounded-md border border-dashed p-4 text-sm text-gray-500">暂无检索命中。</div>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="mb-2 text-sm font-semibold text-gray-800">引用</h4>
          <div className="max-h-40 space-y-2 overflow-y-auto pr-1">
            {citations.length > 0 ? (
              citations.map((citation) => (
                <div key={`${citation.doc_id}-${citation.chunk_id}`} className="rounded-md border bg-blue-50 p-3 text-sm">
                  <div className="mb-1 text-xs font-medium text-blue-700">
                    {citation.doc_id} / {citation.chunk_id}
                  </div>
                  <p className="whitespace-pre-wrap text-gray-800">{citation.quote || '无引用片段'}</p>
                  <div className="mt-2 text-xs text-gray-600">
                    Source: {citation.source || '-'} | Page: {citation.page_number || '-'} | Section: {renderListValue(citation.section_path)}
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-md border border-dashed p-4 text-sm text-gray-500">暂无引用。</div>
            )}
          </div>
        </div>

        <div>
          <h4 className="mb-2 text-sm font-semibold text-gray-800">流水线 Trace</h4>
          <div className="max-h-52 space-y-2 overflow-y-auto pr-1">
            {trace.length > 0 ? (
              trace.map((stage, index) => (
                <div key={`${stage.stage_name}-${index}`} className="rounded-md border bg-gray-50 p-3">
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-gray-900">{index + 1}. {stage.stage_name}</span>
                    <span className="text-xs text-gray-500">{formatLatency(stage.latency_ms)}</span>
                  </div>
                  <div className="grid gap-1 text-xs text-gray-600">
                    <span>Input: {renderJsonSummary(stage.input_summary)}</span>
                    <span>Output: {renderJsonSummary(stage.output_summary)}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-md border border-dashed p-4 text-sm text-gray-500">暂无 trace。</div>
            )}
          </div>
        </div>
      </div>
    </div>
  </section>
);

export default RetrievalTracePanel;
