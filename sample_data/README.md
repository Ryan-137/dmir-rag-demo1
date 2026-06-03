# 默认测试数据

`course_qa_public.json` 是第一阶段 RAG 系统默认输入，来自老师要求的课程 QA 数据。

该文件只包含：

- 课程主题
- 问题
- 候选答案
- 不含语义的 `answer_id`

该文件不包含 0-9 质量档次，允许进入 RAG 索引、prompt、trace 和前端展示。

质量标签在 `eval/labels/course_qa_quality_labels.json` 中，只允许评测脚本在模型生成完成后读取。
