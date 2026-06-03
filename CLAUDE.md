# Claude Code 指示

本仓库的 Claude Code 使用规则与 `AGENTS.md` 一致。开始任何任务前，请先阅读：

1. `AGENTS.md`
2. `docs/agent_rules.md`
3. `docs/interfaces.md`
4. 对应 Issue 的 `docs/agent_instructions/.../AGENTS.md`

核心要求：

- 只修改 Issue 的 `ALLOWED_PATHS`。
- 代码注释必须使用中文 Doxygen 风格。
- 面向 LLM 的 prompt、mock 输出、展示文案尽量使用中文。
- 单元测试不得依赖真实网络、真实 API、真实模型下载。
- 不得删除 fake/mock fallback。
- 第一阶段默认测试数据是 `sample_data/course_qa_public.json`。
- `answer_quality` 档次只能由评测脚本读取，禁止进入 RAG 索引、prompt、trace 或前端展示。

完成后必须运行对应 Issue 的验收命令，并在 PR 中列出修改文件、测试结果和风险点。
