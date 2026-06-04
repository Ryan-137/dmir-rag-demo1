import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildEvaluationRows,
  createRagAnswerRequestPayload,
  createSafeRagAnswerViewModel,
  normalizeEvaluationSummary,
} from './ragViewModel.js';

test('createSafeRagAnswerViewModel removes answer_quality from nested display data', () => {
  const viewModel = createSafeRagAnswerViewModel({
    answer_markdown: '## 回答',
    warnings: ['提示'],
    citations: [
      {
        doc_id: 'doc-1',
        chunk_id: 'chunk-1',
        quote: '证据',
        metadata: { answer_quality: 9, keep: 'visible' },
      },
    ],
    retrieved_hits: [
      {
        rank: 1,
        score: 0.98,
        source: 'sample_data/course_qa_public.json',
        text: '命中文本',
        metadata: { answer_quality: 8, question: '什么是自然语言处理？' },
      },
    ],
    trace: [
      {
        stage_name: 'search',
        latency_ms: 1.5,
        input_summary: { answer_quality: 7, top_k: 3 },
        output_summary: { hits: 1 },
      },
    ],
    metadata: { answer_quality: 6, rag_mode: 'basic_rag' },
  });

  assert.equal(JSON.stringify(viewModel).includes('answer_quality'), false);
  assert.equal(viewModel.retrievedHits[0].metadata.question, '什么是自然语言处理？');
  assert.equal(viewModel.citations[0].metadata.keep, 'visible');
});

test('buildEvaluationRows keeps stable llm/basic/optimized ordering', () => {
  const rows = buildEvaluationRows({
    llm_only: { answerable: 2, cited: 0, avg_latency_ms: 1200 },
    basic_rag: { answerable: 4, cited: 3, avg_latency_ms: 1800 },
    optimized_rag: { answerable: 5, cited: 5, avg_latency_ms: 2200 },
  });

  assert.deepEqual(
    rows.map((row) => row.mode),
    ['llm_only', 'basic_rag', 'optimized_rag'],
  );
  assert.equal(rows[2].label, 'Optimized RAG');
  assert.equal(rows[1].cited, 3);
});

test('createRagAnswerRequestPayload builds RagRequest compatible body without hidden labels', () => {
  const payload = createRagAnswerRequestPayload({
    query: '什么是自然语言处理？',
    ragMode: 'basic_rag',
    topK: 3,
    provider: 'mock',
    model: 'mock-generator',
    collectionId: 'course-qa-default',
    metadata: { answer_quality: 9, max_questions: 5 },
  });

  assert.deepEqual(payload, {
    query: '什么是自然语言处理？',
    rag_mode: 'basic_rag',
    top_k: 3,
    provider: 'mock',
    model: 'mock-generator',
    collection_id: 'course-qa-default',
    require_citations: true,
    metadata: { max_questions: 5 },
  });
  assert.equal(JSON.stringify(payload).includes('answer_quality'), false);
});

test('createRagAnswerRequestPayload falls back to stage A mock defaults', () => {
  const payload = createRagAnswerRequestPayload({
    query: '什么是自然语言处理？',
    ragMode: '',
    topK: 'bad-value',
    provider: '',
    model: '',
    collectionId: '',
  });

  assert.equal(payload.rag_mode, 'basic_rag');
  assert.equal(payload.top_k, 3);
  assert.equal(payload.provider, 'mock');
  assert.equal(payload.model, 'mock-generator');
  assert.equal(payload.collection_id, 'course-qa-default');
});

test('createRagAnswerRequestPayload normalizes topK to integer range', () => {
  const baseConfig = {
    query: '什么是自然语言处理？',
    ragMode: 'basic_rag',
    provider: 'mock',
    model: 'mock-generator',
    collectionId: 'course-qa-default',
  };

  assert.equal(createRagAnswerRequestPayload({ ...baseConfig, topK: 2.5 }).top_k, 2);
  assert.equal(createRagAnswerRequestPayload({ ...baseConfig, topK: -4 }).top_k, 1);
  assert.equal(createRagAnswerRequestPayload({ ...baseConfig, topK: 999 }).top_k, 50);
});

test('normalizeEvaluationSummary accepts remote wrapper payload and removes hidden labels', () => {
  const summary = normalizeEvaluationSummary({
    summary: {
      basic_rag: {
        answerable: 4,
        cited: 3,
        answer_quality: 8,
      },
    },
  });

  assert.equal(summary.basic_rag.answerable, 4);
  assert.equal(summary.basic_rag.cited, 3);
  assert.equal(JSON.stringify(summary).includes('answer_quality'), false);
});
