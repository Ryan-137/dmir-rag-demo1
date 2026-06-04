/**
 * @file Generation.jsx
 * @brief 响应生成工作流页面。
 */
import { useMemo, useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { apiBaseUrl } from '../config/config';
import EvaluationDashboard from '../components/rag/EvaluationDashboard';
import MarkdownAnswer from '../components/rag/MarkdownAnswer';
import PipelineConfigPanel from '../components/rag/PipelineConfigPanel';
import RetrievalTracePanel from '../components/rag/RetrievalTracePanel';
import { createSafeRagAnswerViewModel, removeForbiddenFields } from '../components/rag/ragViewModel';
import { courseQaMockRagAnswer, demoEvaluationSummary } from '../config/ragDemoData';

/**
 * @brief 将旧检索结果包装成 RagAnswer 检索命中。
 * @param {Array<object>} searchResults 旧搜索端点返回的结果。
 * @returns {Array<object>} RagAnswer.retrieved_hits 兼容结构。
 */
const mapLegacyResultsToHits = (searchResults) =>
  searchResults.map((result, index) => {
    const metadata = result.metadata || {};
    const pageValue = metadata.page_number || metadata.page;

    return {
      chunk_id: String(metadata.chunk_id || metadata.chunk || `legacy-chunk-${index + 1}`),
      doc_id: String(metadata.doc_id || metadata.document_name || metadata.source || 'legacy-search-result'),
      text: result.text || result.content || '',
      score: Number(result.score || 0),
      rank: index + 1,
      source: String(metadata.source || result.source || 'legacy-search-results'),
      metadata: {
        ...metadata,
        page_numbers: pageValue ? [pageValue] : metadata.page_numbers || [],
        section_path: metadata.section_path || [],
      },
    };
  });

/**
 * @brief 将当前旧生成结果包装为前端可展示的 RagAnswer。
 * @param {object} params 包装参数。
 * @returns {object} RagAnswer 兼容对象。
 */
const buildRagAnswerFromGeneratedResponse = ({ query, response, searchResults, pipelineConfig }) => {
  const hits = mapLegacyResultsToHits(searchResults);
  const citations = hits.map((hit) => ({
    doc_id: hit.doc_id,
    chunk_id: hit.chunk_id,
    page_number: hit.metadata.page_numbers?.[0] || null,
    section_path: hit.metadata.section_path || [],
    quote: hit.text.slice(0, 240),
    source: hit.source,
    metadata: {},
  }));

  return removeForbiddenFields({
    contract_version: '0.1.0',
    answer_markdown: response || '暂无生成回答。',
    citations,
    retrieved_hits: hits,
    trace: [
      {
        stage_name: 'frontend_wrap',
        latency_ms: 0,
        input_summary: {
          query,
          rag_mode: pipelineConfig.ragMode,
          top_k: pipelineConfig.topK,
        },
        output_summary: {
          hits: hits.length,
          citations: citations.length,
        },
        artifacts: {},
      },
    ],
    warnings: hits.length === 0 ? ['当前生成结果没有检索上下文，引用信息为空。'] : [],
    metadata: {
      provider: pipelineConfig.provider,
      model: pipelineConfig.model,
      collection_id: pipelineConfig.collectionId,
      rag_mode: pipelineConfig.ragMode,
    },
  });
};

/**
 * @brief 渲染回答生成控件和检索上下文预览。
 * @returns {JSX.Element} 生成工作流页面。
 */
const Generation = () => {
  const location = useLocation();
  const [provider, setProvider] = useState('');
  const [modelName, setModelName] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [models, setModels] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState('');
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [searchFiles, setSearchFiles] = useState([]);
  const [showReasoning, setShowReasoning] = useState(true);
  const [loadModel, setLoadModel] = useState(false);
  const [pipelineConfig, setPipelineConfig] = useState({
    ragMode: 'basic_rag',
    topK: 3,
    provider: 'mock',
    model: 'mock-generator',
    collectionId: 'course-qa-smoke',
  });
  const [ragAnswer, setRagAnswer] = useState(courseQaMockRagAnswer);

  const safeRagAnswer = useMemo(() => createSafeRagAnswerViewModel(ragAnswer), [ragAnswer]);

  // 加载可用模型列表和搜索结果文件列表
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 获取模型列表
        const modelsResponse = await fetch(`${apiBaseUrl}/generation/models`);
        const modelsData = await modelsResponse.json();
        setModels(modelsData.models);

        // 获取搜索结果文件列表
        const filesResponse = await fetch(`${apiBaseUrl}/search-results`);
        const filesData = await filesResponse.json();
        setSearchFiles(filesData.files);
      } catch (error) {
        console.error('Error fetching data:', error);
        setStatus('获取数据失败');
      }
    };

    fetchData();
  }, []);

  // 加载选中的搜索结果文件内容
  useEffect(() => {
    const loadSearchResults = async () => {
      if (!selectedFile) {
        setQuery('');
        setSearchResults([]);
        return;
      }

      try {
        const response = await fetch(`${apiBaseUrl}/search-results/${selectedFile}`);
        const data = await response.json();
        setQuery(data.query);
        setSearchResults(data.results);
      } catch (error) {
        console.error('Error loading search results:', error);
        setStatus('加载搜索结果失败');
      }
    };

    loadSearchResults();
  }, [selectedFile]);

  // 如果从搜索页面跳转过来，获取搜索结果
  useEffect(() => {
    if (location.state) {
      const { query: searchQuery, results } = location.state;
      if (searchQuery) setQuery(searchQuery);
      if (results) setSearchResults(results);
    }
  }, [location]);

  const handleGenerate = async () => {
    if (!provider || !modelName) {
      setStatus('请选择生成模型');
      return;
    }

    if (!query /*|| searchResults.length === 0 */) {
      setStatus('请输入问题并确保有搜索结果');
      return;
    }

    setIsGenerating(true);
    setStatus('');
    try {
      const response = await fetch(`${apiBaseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          provider,
          model_name: modelName,
          search_results: searchResults,
          load_model: loadModel,
          api_key: apiKey || null,
          show_reasoning: showReasoning,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResponse(data.response);
      setLoadModel(false);
      setStatus(`生成完成！modelStatus: ${loadModel} 结果已保存至: ${data.saved_filepath}`);
    } catch (error) {
      console.error('Generation error:', error);
      setStatus(`生成失败: ${error.message}`);
    } finally {
      setIsGenerating(false);
      setLoadModel(false);
    }
  };

  const handleUseMockAnswer = () => {
    setRagAnswer(courseQaMockRagAnswer);
    setPipelineConfig((currentConfig) => ({
      ...currentConfig,
      ragMode: 'basic_rag',
      topK: 3,
      provider: 'mock',
      model: 'mock-generator',
      collectionId: 'course-qa-smoke',
    }));
  };

  const handleMirrorGeneratedAnswer = () => {
    setRagAnswer(
      buildRagAnswerFromGeneratedResponse({
        query,
        response,
        searchResults,
        pipelineConfig,
      }),
    );
  };

  return (
    <div className="p-6">
      <h1 className="text-blue-500 text-3xl font-bold text-center mb-6"> 检索增强生成工具 </h1>
      <hr />
      <h2 className="text-2xl font-bold mb-6">响应生成</h2>
      
      <div className="grid grid-cols-12 gap-6">
        {/* 左侧面板：生成控件 */}
        <div className="col-span-4 space-y-4">
          <div className="p-4 border rounded-lg bg-white shadow-sm">
            <div className="space-y-4">
              <div>
                    <label className="block text-sm font-medium mb-1">提问</label>
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Enter your question..."
                      className="block w-full p-2 border rounded h-32 resize-none"
                    />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">检索文档（可选）</label>
                <select
                  value={selectedFile}
                  onChange={(e) => setSelectedFile(e.target.value)}
                  className="block w-full p-2 border rounded"
                >
                  <option value="">Select search results file...</option>
                  {searchFiles.map(file => (
                    <option key={file.id} value={file.id}>
                      {file.name}
                    </option>
                  ))}
                </select>
              </div>

              {/*selectedFile && */ (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">生成模型提供方</label>
                    <select
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                      className="block w-full p-2 border rounded"
                    >
                      <option value="">Select provider...</option>
                      {Object.keys(models).map(p => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </div>

                  {provider && (
                    <div>
                      <label className="block text-sm font-medium mb-1">生成模型</label>
                      <select
                        value={modelName}
                        onChange={(e) => {setModelName(e.target.value); setLoadModel(true)}}
                        className="block w-full p-2 border rounded"
                      >
                        <option value="">Select model...</option>
                        {Object.entries(models[provider] || {}).map(([id, name]) => (
                          <option key={id} value={id}>
                            {id === 'deepseek-v3' ? 'DeepSeek V3' :
                             id === 'deepseek-r1' ? 'DeepSeek R1' :
                             name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {(provider === 'openai' || provider === 'deepseek') && (
                    <div>
                      <label className="block text-sm font-medium mb-1">API Key</label>
                      <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="Enter your API key..."
                        className="block w-full p-2 border rounded"
                      />
                    </div>
                  )}

                  {provider === 'deepseek' && modelName === 'deepseek-r1' && (
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="showReasoning"
                        checked={showReasoning}
                        onChange={(e) => setShowReasoning(e.target.checked)}
                        className="rounded border-gray-300 text-green-500 focus:ring-green-500"
                      />
                      <label htmlFor="showReasoning" className="text-sm font-medium">
                        显示思维链过程
                      </label>
                    </div>
                  )}

                  <button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-green-300"
                  >
                    {isGenerating ? '生成回答中...' : '生成回答'}
                  </button>

                  {status && (
                    <div className={`p-4 rounded-lg ${
                      status.includes('失败') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {status}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          <PipelineConfigPanel
            config={pipelineConfig}
            onConfigChange={setPipelineConfig}
            onUseMockAnswer={handleUseMockAnswer}
            onMirrorGeneratedAnswer={handleMirrorGeneratedAnswer}
            hasGeneratedAnswer={Boolean(response)}
          />
        </div>

        {/* 右侧面板：contract 展示、上下文和回答 */}
        <div className="col-span-8 space-y-6">
          <div className="rounded-lg border bg-slate-900 p-4 text-white shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-xl font-semibold">Contract RAG 展示</h3>
                <p className="text-sm text-slate-300">
                  前端只读取 RagAnswer 字段，可复用在课程 QA 和论文 RAG。
                </p>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="rounded bg-white/10 px-3 py-2">
                  <div className="text-slate-300">Hits</div>
                  <div className="text-lg font-semibold">{safeRagAnswer.retrievedHits.length}</div>
                </div>
                <div className="rounded bg-white/10 px-3 py-2">
                  <div className="text-slate-300">Citations</div>
                  <div className="text-lg font-semibold">{safeRagAnswer.citations.length}</div>
                </div>
                <div className="rounded bg-white/10 px-3 py-2">
                  <div className="text-slate-300">Trace</div>
                  <div className="text-lg font-semibold">{safeRagAnswer.trace.length}</div>
                </div>
              </div>
            </div>
          </div>

          <MarkdownAnswer
            answerMarkdown={safeRagAnswer.answerMarkdown}
            warnings={safeRagAnswer.warnings}
            contractVersion={safeRagAnswer.contractVersion}
          />

          <RetrievalTracePanel
            retrievedHits={safeRagAnswer.retrievedHits}
            citations={safeRagAnswer.citations}
            trace={safeRagAnswer.trace}
          />

          <EvaluationDashboard summary={demoEvaluationSummary} />

          <div className="rounded-lg border bg-white p-4 shadow-sm">
            <h3 className="mb-4 text-xl font-semibold">旧流程检索上下文</h3>
            {selectedFile ? (
              <div className="max-h-[300px] space-y-4 overflow-y-auto">
                {searchResults.map((result, idx) => (
                  <div key={`${result.text}-${idx}`} className="rounded border bg-gray-50 p-4">
                    <div className="mb-2 flex items-start justify-between gap-3">
                      <span className="text-sm font-medium text-gray-500">
                        Match Score: {(Number(result.score || 0) * 100).toFixed(1)}%
                      </span>
                      <div className="text-sm text-gray-500">
                        <div>Source: {result.metadata?.source || '-'}</div>
                        <div>Page: {result.metadata?.page || result.metadata?.page_number || '-'}</div>
                      </div>
                    </div>
                    <p className="whitespace-pre-wrap text-sm">{result.text}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded border border-dashed p-4 text-sm text-gray-500">无检索上下文。</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Generation;
