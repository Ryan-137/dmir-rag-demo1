/**
 * @file MarkdownAnswer.jsx
 * @brief 展示 RagAnswer 中的 Markdown 回答和警告信息。
 */
/* eslint-disable react/prop-types */
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * @brief 渲染有引用支撑的 Markdown 回答。
 * @param {{answerMarkdown: string, warnings?: string[], contractVersion?: string}} props 组件属性。
 * @returns {JSX.Element} Markdown 回答面板。
 */
const MarkdownAnswer = ({ answerMarkdown, warnings = [], contractVersion = 'unknown' }) => (
  <section className="rounded-lg border bg-white p-4 shadow-sm">
    <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">RAG 回答</h3>
        <p className="text-xs text-gray-500">Contract v{contractVersion}</p>
      </div>
      {warnings.length > 0 && (
        <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
          {warnings.length} 条警告
        </span>
      )}
    </div>

    {warnings.length > 0 && (
      <div className="mb-4 space-y-2">
        {warnings.map((warning, index) => (
          <div key={`${warning}-${index}`} className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            {warning}
          </div>
        ))}
      </div>
    )}

    <div className="prose prose-sm max-w-none rounded-md bg-gray-50 p-4 text-gray-800">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {answerMarkdown || '暂无回答。'}
      </ReactMarkdown>
    </div>
  </section>
);

export default MarkdownAnswer;
