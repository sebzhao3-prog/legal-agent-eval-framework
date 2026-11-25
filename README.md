# Legal Agent Evaluation Framework

**法律 Agent 工作流评测框架**

合同审查 Agent 在初审时识别了责任风险，换到对方修改稿后却继续引用旧条款。这类错误需要跨阶段测试才能发现。本框架把法律判断、工作流状态和交付物放进同一套验收流程。

An evaluation framework for legal AI workflows, with a runnable synthetic example covering contract review, version handoff, and task memory.

## 从哪里开始

| 内容 | 你可以用它做什么 |
| --- | --- |
| [评测方法与评分表](docs/framework.md) | 定义覆盖范围、六维指标、失败条件和证据记录方式 |
| [采购合同示例](examples/README.md) | 逐步执行初审、版本流转和会话恢复三个场景 |
| [评测用例](examples/cases.json) · [演示观测](examples/observations.json) | 查看机器可读的预期行为，以及一份故意含有失败的模拟记录 |

## 运行示例

在仓库根目录执行。运行环境为 Python 3，无需安装依赖或配置 API Key。

```sh
python3 score.py
```

汇总结果如下。脚本还会列出失败和缺失记录的观察项。

```text
REVIEW-01   PASS        required 4/4  bonus 0/1
HANDOFF-01  FAIL        required 4/5  bonus 0/0
MEMORY-01   PASS        required 3/3  bonus 0/0
2 passed, 1 failed, 0 incomplete
```

`HANDOFF-01` 的观测记录在签署阶段仍指向旧稿，触发关键失败，命令退出码为 `1`。脚本对照预期与人工整理的观测值，示例记录为模拟数据。评测自己的 Agent 时，按[示例操作说明](examples/README.md)运行工作流并填写观测记录。

## 评测范围

| 触发覆盖 | 流程完整 | Skill 路由 | 输出适配 | 法律专业质量 | 记忆留存 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 15 | 15 | 10 | 35 | 15 |

案例级判定保留必测项、加分项和关键失败条件。六维百分制用于完整验收，公开示例覆盖三条场景，结果按案例展示。
