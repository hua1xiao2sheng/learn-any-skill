# Learn Any Skill：把学习目标变成可执行的课程

**不是再推荐十门课，而是筛出少量合适资料，编排成有讲解、练习、项目和验收的课程。**

[English](README.md) · [安装指南](docs/INSTALLATION.md) · [GitHub 发布教程](docs/PUBLISH.zh-CN.md) · [本次检查报告](docs/AUDIT.zh-CN.md)

版本：**0.2.0**｜协议：MIT｜可选辅助脚本：Python 3.10+

## 适合什么需求？

例如：学习 RAG、Agent、vLLM、CUDA、分布式训练，或者其他可定义明确成果的技能。先明确“学完能做什么”，再找资料、选章节、排依赖、安排实践。不会因为用户说自己是博士就自动判定已经掌握全部前置知识。

```text
学习目标 + 当前基础 + 时间/预算/硬件限制
                ↓
            能力依赖图
                ↓
     搜索并阅读课程、官方文档、论文和代码
                ↓
    核验来源 → 去重复 → 保留少量必要资料
                ↓
   逐课安排：原理讲解 + 练习 + 产物 + 验收
                ↓
      独立重做 → 迁移项目 → 保存学习进度
```

## 先分清：它是什么，不是什么

这是给 Codex 等支持 Skill 的宿主使用的**流程指令包，加上几个本地辅助脚本**。不是双击运行的软件，不内置大模型、搜索引擎、视频下载器或后台定时服务。搜索和写文件由宿主已有的工具完成；工具不可用时必须明确说明。

| 能力 | 由谁执行 |
|---|---|
| 搜索资料、阅读页面、组织课程、授课和反馈 | 宿主模型按 Skill 指令执行 |
| 按给定分数计算资源排名 | `score_resources.py` |
| 检查前置依赖、引用、能力覆盖、学时预算 | `validate_plan.py` |
| 检查发布目录、YAML、JSON Schema、本地文档链接 | `validate_repo.py` |
| 跨会话继续学习 | 读取实际保存的 `progress.json`，不是自动永久记忆 |

Skill 指令不能保证模型每次都严格执行。脚本通过，也不等于课程一定好、网上内容一定正确或学习者一定学会。

## 安装：先复制完整文件夹

Codex 的用户级目录：

```text
Windows：C:\Users\你的Windows用户名\.agents\skills\learn-any-skill\
macOS / Linux：~/.agents/skills/learn-any-skill/
```

项目级目录：

```text
你的项目/.agents/skills/learn-any-skill/
```

最终必须能直接找到：

```text
.agents/skills/learn-any-skill/SKILL.md
```

不是只复制一个 `SKILL.md`，也不是再套一层 `learn-any-skill/learn-any-skill/`。GitHub 的源码 ZIP 可能解压成 `learn-any-skill-main`，安装时把这一层改名为 `learn-any-skill`。复制后在 Codex 中查看 Skill 列表；没有出现时重启宿主。

这些路径依据 2026-09-21 核对的 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)。旧文档中的 `~/.codex/skills` 不再作为本项目推荐的用户级安装路径。更多命令见 [安装指南](docs/INSTALLATION.md)。

## 最简单的使用方式

下面的内容发到 **Codex 对话框，不是 PowerShell 终端**：

```text
使用 $learn-any-skill 帮我学习 RAG。

我会 Python 和基础 PyTorch。
总预算 14 小时，只用免费资源，最多 3 个核心资料。
目标：独立搭建一个检索流程，评估检索结果并排查常见问题。
先搜索和核验资料，再整理成逐课课程；不要只给课程链接。
把文件保存到当前项目的 .learning/rag/。
```

后续可以直接说：

```text
使用 $learn-any-skill 把 .learning/rag/ 的课程展开成完整课卡。

开始第一课，先讲例子，再给我一道不附答案的练习。

检查我的作业，根据真实完成情况更新进度。

读取 .learning/rag/ 的进度，继续下一课。
```

`plan / build / teach / review / resume / refresh` 是指令中识别的六种意图，不是已经注册的 `/learn` 等斜杠命令。主 Skill 不依赖某个写死的搜索工具名，也不自动配置 MCP。

## 六种模式

| 模式 | 含义 |
|---|---|
| plan | 找资料并编排学习路线、项目和验收 |
| build | 在已有课程基础上写原创讲解、逐课练习与课卡 |
| teach | 按当前课卡授课，不重新堆一遍资源列表 |
| review | 根据提交的答案或测试输出反馈，不无依据地判定通过 |
| resume | 先读保存的进度，再继续，不凭空记忆 |
| refresh | 核验过期资料，只改受影响的部分，保留已完成内容 |

## 导出的课程长什么样？

```text
.learning/rag/
├── brief.json          # 学习目标、基础和限制
├── resources.json      # 来源、具体章节、核验记录
├── plan.json           # 能力依赖、课程引用、学时预算
├── curriculum.md       # 可读课程表
├── progress.json       # 实际学习进度
└── lessons/            # build 模式生成逐课正文
    ├── 01-....md
    └── ...
```

每课必须说明：为什么学、读哪一小段、核心原理是什么、动手做什么、留下什么产物、达到什么标准才能算完成。独立练习允许查 API 文档，但不能把照抄答案当作独立掌握。

网络不可用时，课程标为“暂定 / offline”，不会编造搜索结果、章节或已核验标记。付费限制、硬件限制、用户禁止联网等都是硬限制，而不是可以被高分覆盖的选项。

## 不接 API 也能先检查这个项目

项目内附有一套完整的 [Python 单元测试小课程](examples/python-testing/curriculum.zh-CN.md)：3 节课、2 个官方资料页、1 个原创实验。4 小时是示例规划预算，不是学习效果保证；它用来展示课程结构，并不是完整 RAG 教学产品。

在仓库根目录运行：

```bash
python scripts/score_resources.py examples/resources.example.json
python scripts/validate_plan.py examples/python-testing/plan.json --resources examples/python-testing/resources.json
python -m unittest discover -s examples/python-testing/lab -v
```

Windows 没有 `python` 命令而有 Python 启动器时，把 `python` 换成 `py`。第一个评分文件明确标记为**人工构造的测试样例**；90、89、68 分只验证算术，不是真实课程排名。

完整开发检查另需安装两个校验依赖：

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py .
python -m unittest discover -s tests -v
```

普通使用 Skill 不必安装这些开发依赖。测试范围、未验证项见 [测试说明](docs/TESTING.md) 和 [审计报告](docs/AUDIT.zh-CN.md)。

## 发布到 GitHub

下载压缩包，解压后把**里面的全部文件和子目录**放到仓库根目录。不要只上传 ZIP，不要漏掉 `.github/`、`.gitignore` 和 `.gitattributes`。完整的 Windows 网页上传与命令行步骤在 [发布教程](docs/PUBLISH.zh-CN.md)。

本仓库不预填你的 GitHub 用户名，不伪造 Stars 或 CI 徽章，不会自动替你创建或推送远程仓库。发布到 GitHub 不等于注册到 ChatGPT / Codex 插件商店。

## 数据与版权

个人课程和作业默认放在 `.learning/`，不要公开上传。辅助脚本不联网、不收集遥测、不读取账号密钥；宿主调用外部工具时仍需遵守权限和用户授权。MIT 协议只覆盖本仓库的原创内容，不授予第三方课程转载权。详见 [安全说明](SECURITY.md)。

## 依据与边界

结构参照 [Agent Skills 格式规范](https://agentskills.io/specification)；Codex 安装与调用依据 [官方文档](https://learn.chatgpt.com/docs/build-skills)，核对日期为 2026-09-21。未声称已在所有宿主中通过端到端实测，未声称能找到全网最优课程或使学习速度固定提升多少倍。
