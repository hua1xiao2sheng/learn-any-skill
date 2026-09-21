# 发布到 GitHub：Windows 操作指南

此文件只提供操作说明，不会替你创建仓库、登录账号或推送内容。

## 1. 先下载并解压

压缩包名可以是 `learn-any-skill-v0.2.0.zip`，里面的顶层文件夹是 `learn-any-skill`。进入这一层，应当直接看到 `SKILL.md`、`README.md`、`README.zh-CN.md`、`scripts/` 等。

不要把压缩包本身当作仓库源码上传；也不要把最外层文件夹再套一层。正确仓库首页直接显示 `SKILL.md`。同时保留点开头的文件和目录：`.github/`、`.gitignore`、`.gitattributes`。

## 2. 建一个空仓库

在 GitHub 右上角点 `+` → `New repository`。仓库名填 `learn-any-skill`，需要开源就选 Public。不要自动添加 README、License 或 .gitignore，因为文件夹里已有这些文件。创建仓库后，保留页面显示的真实仓库地址。

建议描述：

```text
A source-grounded learning skill that curates resources into practical courses with projects and mastery checks.
```

## 3A. 网页上传（不需要 Git）

在空仓库页面选择 `uploading an existing file`；已有仓库则用 `Add file` → `Upload files`。把解压目录**里面的文件和子目录**拖入，填写提交说明 `Release v0.2.0`，点击 `Commit changes`。

确认上传列表有 `.github/workflows/validate.yml`。有些浏览器或拖拽方式可能漏掉点目录；若缺失，可用网页 `Add file` → `Create new file` 创建这个完整路径，再粘贴对应文件内容，或使用下方 Git 方法。不要为“解决漏文件”而上传个人 `.env`、密钥或 `.learning/`。

## 3B. PowerShell + Git（便于后续更新）

先确保已安装 Git，然后在实际解压目录打开 PowerShell。路径只是示例，请替换为你电脑上的路径：

```powershell
cd "C:\Users\你的Windows用户名\Downloads\learn-any-skill"
git init
git add .
git status
git commit -m "Release v0.2.0"
git branch -M main
```

提交前检查 `git status`：这里只应有公开的 Skill 源码，不应出现个人学习进度、访问令牌、付费课件或私有数据。第一次提交提示没有身份时，按自己的身份配置当前仓库，勿照填别人的信息：

```powershell
git config user.name "你的GitHub显示名"
git config user.email "你的GitHub已验证邮箱或noreply邮箱"
git commit -m "Release v0.2.0"
```

把下面的 `YOUR_GITHUB_USER` 换成自己的真实用户名；也可直接复制空仓库页面给出的远程地址：

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USER/learn-any-skill.git
git push -u origin main
```

按 Git/GitHub 的认证提示操作。不要把 token 写进 URL 或文档。若 `origin` 已存在，先 `git remote -v` 查看，不要盲目重复添加或改成错误账号的地址。

如果远程仓库已经自动生成过 README，可能出现历史冲突或 push 被拒绝。不要使用 `--force` 覆盖未知远程内容；改为先克隆该仓库到新目录、把本项目文件复制进去，再正常提交推送。

## 4. 检查源码和 CI

确认仓库根目录有 `SKILL.md`，打开 `README.zh-CN.md` 查看中文说明。到 `Actions` 页查看 `validate` 工作流的**实际运行结果**。本压缩包配置了多平台测试，但本地通过不代表 GitHub Actions 已经通过；没有运行记录时不要添加虚假的“通过”徽章。

本地提前检查：

```powershell
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py .
python -m unittest discover -s tests -v
python -m unittest discover -s examples/python-testing/lab -v
```

只有 Windows `py` 命令时，可相应替换 `python`。

## 5. 可选：创建版本发布

源码推送成功后，可在仓库的 `Releases` 页面新建 release，tag 用 `v0.2.0`，说明可参考 `CHANGELOG.md`。这一步不是别人克隆使用 Skill 的前提。GitHub 发布与 ChatGPT / Codex 插件目录注册是两件事；本项目没有自动完成后者。

## 以后更新

修改文件 → 本地测试 → `git diff` / `git status` 检查 → `git add .` → `git commit -m "Describe the change"` → `git push`。发布记录应与 `VERSION`、`SKILL.md` 的 metadata 版本和 `CHANGELOG.md` 保持一致。

依据：[GitHub 官方创建项目仓库指南](https://docs.github.com/en/get-started/start-your-journey/creating-a-repository-for-your-project-on-github)，核对日期 2026-09-21。界面文案可能随语言和账户配置略有变化。
