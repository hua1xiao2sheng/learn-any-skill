# 示例课程：为小型 Python 数据处理函数写可靠的单元测试

这是一套完整的小课程示例，用来展示 Skill 应产出的结构。假定学习者会写 Python 函数、导入模块和运行脚本；这只是示例假设，不是对任何真实用户的评估。总预算 **4 小时**：输入 0.75 小时，实践 2 小时，验收 0.75 小时，缓冲 0.5 小时。实际耗时需在第一课后校准。

## 学完做什么

独立为分数归一化函数和依赖数据加载器的统计函数编写测试，覆盖正常输入、异常、边界和外部依赖。能用一处故意制造的错误验证测试是否有效。**不包含**完整 CI 运维、数据库集成测试、性能测试或 RAG 系统评测。

## 能力依赖

`c-python（假定已会）→ c-test（正常测试）→ c-boundaries（边界和错误）→ c-isolation（隔离依赖）`

## 只选三个来源

| ID | 来源 | 学哪些部分 | 不学哪些部分 |
|---|---|---|---|
| r-unittest | [Python unittest 官方文档](https://docs.python.org/3/library/unittest.html) | Basic example、Test Discovery、assertRaises | 自定义 TestRunner、扩展测试协议等高级内容 |
| r-mock | [Python unittest.mock 官方文档](https://docs.python.org/3/library/unittest.mock.html) | The Mock Class 中的 return_value、side_effect、assert_called_once_with | patch 装饰器组合、异步与线程 mock |
| r-lab | [本地原创实验](lab/normalize_scores.py) | 两个小函数与其输入契约 | 不扩展为生产级数据平台 |

官方资料的相关章节核对日期为 2026-09-21。具体观察和范围限制见 [resources.json](resources.json)。没有宣称读完全部官方文档。实验只用标准库，运行不需要联网或 API Key。

## 三课安排

| 课次 | 任务 | 输入/实践/验收（小时） | 产物 |
|---|---|---|---|
| [第一课](lessons/01-first-test.md) | 正常与边界断言，主动观察一次失败 | 0.25 / 0.50 / 0.25 | 自己写的测试和失败解释 |
| [第二课](lessons/02-boundaries.md) | 从空白文件测试异常与数据契约 | 0.25 / 0.75 / 0.25 | 非法输入测试集、一个回归测试 |
| [第三课](lessons/03-isolation-transfer.md) | 隔离 loader，再迁移到中位数统计 | 0.25 / 0.75 / 0.25 | Mock 测试、独立迁移函数与测试 |

课内共 3.5 小时，另留 0.5 小时处理环境、调试与复习。课卡不要求学完整门视频课；官方文档只是精确参考，课程串联与练习均为原创设计。

## 使用实验文件

维护者的发布检查可直接在仓库根目录执行：

```bash
python -m unittest discover -s examples/python-testing/lab -v
```

学习者不要把这些参考测试的通过当作自己的掌握证据。建议先复制课程到自己的工作区，避免修改已安装的 Skill。仓库根目录下可运行以下命令；目标存在时会拒绝覆盖：

```bash
python -c "import shutil; shutil.copytree('examples/python-testing', '.learning/python-testing')"
```

然后进入 `.learning/python-testing/lab`，在同目录写 `test_mine.py`，运行：

```bash
python -m unittest -v test_mine
```

先独立完成，再看 `test_normalize_scores.py` 作为参考答案。第三课的迁移题 `median_from_loader` 故意不附完整答案，需要学习者独立实现和测试。

## 验收与进度

最终需提交自己的测试文件、一个故意出错再恢复的实验记录，以及独立完成的中位数迁移任务。不能仅凭“看过”或“复制后能运行”通过验收。

[progress.json](progress.json) 的所有课程初始状态均为 `not_started`，没有冒充真实学习记录。文件格式与时间依赖可用仓库内的 `scripts/validate_plan.py` 检查；课程质量和真实掌握需要实际教学评估。
