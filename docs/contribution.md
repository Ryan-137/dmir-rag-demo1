# RAG Demo 贡献与 PR 规则

v1.0 | 2026-06-03

## 开工前

1. 先读 [agent_rules.md](agent_rules.md) 和 [interfaces.md](interfaces.md)。
2. 从 GitHub Issues 认领自己的任务。
3. 按 Issue 里的 `ALLOWED_PATHS` 修改文件。
4. 开分支，不直接在 `main` 上开发。

## 分支命名

- `feat/<issue>-<module>`
- `fix/<issue>-<short-name>`
- `docs/<issue>-<short-name>`

示例：

```shell
git checkout -b feat/3-qwen-embedding
```

## PR 标准

- 一个 PR 只做一个功能，必须关联一个 Issue。
- 建议小于 400 行有效改动；超过就拆分。
- 必须写清：做了什么、如何测试、是否涉及 contract、风险点。
- 涉及 contracts、CI、主流水线的 PR 必须由 `answerend42` review。
- `main` 必须始终可运行；发现破坏主线，优先 revert PR。

## 必跑测试

按改动范围选择测试。普通 PR 至少跑后端快速检查；涉及前端必须跑前端 build；涉及流水线必须跑 smoke pipeline。

```shell
python -m compileall backend
pytest tests/contract tests/unit -m "not integration and not benchmark"
python scripts/run_smoke_pipeline.py --mode fake
cd frontend && npm run build
```

真实 API、本地大模型、OCR、大 corpus benchmark 只放在 integration/benchmark 任务中，不阻塞普通 PR。

## CI 门禁目标

现有 CI 已包含前端 build、后端依赖安装、`compileall` 和 import 检查。下一步要补：

| Job | 触发 | 内容 | 是否阻塞 |
| --- | --- | --- | --- |
| `frontend-build` | push/PR | `npm ci` + `npm run build` + lint | 是 |
| `backend-fast-tests` | push/PR | `compileall` + contract/unit pytest | 是 |
| `smoke-fake-pipeline` | push/PR | Mock 流水线输出 `RagAnswer` | 是 |
| `integration-real-small` | 手动 | 小 PDF + Chroma + 可选真实 key | 否 |
| `benchmark` | 手动/nightly | Chroma profiles、eval report | 否 |

## Review 检查清单

- [ ] 改动只发生在 Issue 允许的路径。
- [ ] 没有提交 API key、模型权重、大型二进制文件、临时缓存。
- [ ] 没有修改他人模块或降低 CI 门禁。
- [ ] 跨模块数据遵守 contract，`SearchHit.score` 仍然是越大越相关。
- [ ] 有测试命令、结果摘要和必要截图/日志。
- [ ] 失败、空检索、无证据回答等边界有处理。
