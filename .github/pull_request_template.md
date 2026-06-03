### 本 PR 做了什么


### 修改范围

- ALLOWED_PATHS:

### 如何测试

- [ ] `python -m compileall backend`
- [ ] `pytest tests/contract tests/unit -m "not integration and not benchmark"`
- [ ] `python scripts/run_smoke_pipeline.py --mode fake`
- [ ] `cd frontend && npm run build`（涉及前端时）

### 是否修改 contracts

- [ ] 否
- [ ] 是，已附 ADR 并请求 `answerend42` review

### 风险与回滚方案


