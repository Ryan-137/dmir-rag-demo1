/**
 * @file EvaluationDashboard.jsx
 * @brief 展示 LLM-only、Basic RAG 和 Optimized RAG 三模式评测摘要。
 */
import PropTypes from 'prop-types';
import { buildEvaluationRows, formatLatency } from './ragViewModel';

const asDisplayValue = (value) => {
  if (value === undefined || value === null || value === '') {
    return '-';
  }
  return value;
};

/**
 * @brief 渲染三模式评测表。
 * @param {{summary: object}} props 组件属性。
 * @returns {JSX.Element} 评测 dashboard。
 */
const EvaluationDashboard = ({ summary }) => {
  const rows = buildEvaluationRows(summary);

  return (
    <section className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">三模式评测</h3>
        <p className="text-xs text-gray-500">展示聚合指标；隐藏质量标签不进入前端。</p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase text-gray-500">
            <tr>
              <th className="px-3 py-2">模式</th>
              <th className="px-3 py-2">可回答</th>
              <th className="px-3 py-2">有引用</th>
              <th className="px-3 py-2">拒答</th>
              <th className="px-3 py-2">平均耗时</th>
              <th className="px-3 py-2">备注</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {rows.map((row) => (
              <tr key={row.mode}>
                <td className="px-3 py-2 font-medium text-gray-900">{row.label}</td>
                <td className="px-3 py-2 text-gray-700">{asDisplayValue(row.answerable)}</td>
                <td className="px-3 py-2 text-gray-700">{asDisplayValue(row.cited)}</td>
                <td className="px-3 py-2 text-gray-700">{asDisplayValue(row.refused)}</td>
                <td className="px-3 py-2 text-gray-700">{formatLatency(row.avg_latency_ms)}</td>
                <td className="px-3 py-2 text-gray-600">{asDisplayValue(row.note)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

EvaluationDashboard.propTypes = {
  summary: PropTypes.object.isRequired,
};

export default EvaluationDashboard;
