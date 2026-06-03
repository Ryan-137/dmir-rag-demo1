# 评测标签

`course_qa_quality_labels.json` 保存课程 QA 候选答案的 0-9 质量档次。

这些标签只允许评测脚本在模型生成完成后读取，用于计算报告指标。禁止进入：

- RAG 索引
- LLM prompt
- retrieved hits
- trace
- 前端展示

系统默认输入请使用 `sample_data/course_qa_public.json`。
