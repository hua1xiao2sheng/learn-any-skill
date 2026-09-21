# Installation / 安装

Checked against [OpenAI's local skill discovery documentation](https://learn.chatgpt.com/docs/build-skills) on 2026-09-21. The current recommended user directory is `$HOME/.agents/skills`; a repository may contain `.agents/skills`. The skill name must match the installed folder name.

## Copy from the downloaded folder (no Git required)

Copy the **whole** `learn-any-skill` directory into the chosen skills directory. Do not copy the ZIP or only `SKILL.md`. Do not nest the folder twice. On Windows the user directory is usually:

```text
C:\Users\YOUR_WINDOWS_USER\.agents\skills\learn-any-skill\SKILL.md
```

Create `.agents` and `skills` if missing. If a destination already exists, inspect or back it up before replacing it; avoid duplicate copies with the same skill name at both user and project scope. Keep the source repository you publish separate from personal study output.

## Git clone after publication

Replace `YOUR_GITHUB_USER` with the actual owner. These URLs are templates, not an existing repository claim.

macOS / Linux:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/YOUR_GITHUB_USER/learn-any-skill.git "$HOME/.agents/skills/learn-any-skill"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
git clone https://github.com/YOUR_GITHUB_USER/learn-any-skill.git "$HOME\.agents\skills\learn-any-skill"
```

For a project-scoped installation, place the folder at `<project>/.agents/skills/learn-any-skill/`. For a skill checked into another repository, copying the folder is simpler than accidentally creating an embedded Git repository; use a submodule only deliberately.

A fresh clone must target a non-existing directory. To update an existing Git installation, inspect `git status` and your changes before using `git pull --ff-only`; do not overwrite local work blindly.

## Invocation

Inside Codex CLI or IDE chat, mention `$learn-any-skill` or inspect `/skills`. These are agent-chat interactions, not terminal programs. Restart the host when an installed skill does not appear. Installation does not automatically enable browsing, shell access, or filesystem writes; use the host's actual permissions.

The optional `agents/openai.yaml` file configures Codex metadata. Other Agent Skills hosts may load the core format but have different locations/tools; this release does not certify their compatibility. GitHub source distribution is separate from packaging and registering a product-directory plugin.

## Troubleshooting

**Not listed:** check the final path, exact filename `SKILL.md`, lowercase folder name, host skill settings, duplicate installations, and host version. **Can plan but cannot search:** the host lacks an available search/page-reading tool; the correct behavior is a provisional plan, not an invented search. **Helper cannot be found:** resolve its path from the installed skill directory, not the study project's working directory. **Windows `python` is missing:** install a supported Python interpreter to run helpers, or use `py` when the Windows launcher is present. Reading the Skill itself does not require Python.
