# 从零开始用 lecture-notes-maker（中文保姆级指南）

这份指南写给**没用过 Claude Code、也没跑过这套流程**的人。照着一节一节做就行。

这个工具能做两件事：

| 你给它什么 | 它给你什么 | 对应模式 |
|-----------|-----------|---------|
| 课件 PDF / 上课录像 | 5–7 页 A4 的复习笔记 PDF（定义 → 类比 → 规则/坑） | 笔记模式（默认） |
| 会议录像（mp4 等） | 一份会议纪要 `minutes.md`（TL;DR、决定、行动项、带时间戳） | 会议模式 |

整个流程分三层：**Claude Code**（跑 AI 的命令行工具）→ **这个 skill**（告诉 AI 怎么做笔记）→ **本地依赖**（ffmpeg、whisper 等，负责把视频变成文字和截图）。视频转文字**完全在你自己电脑上跑**，录像不会上传到任何地方；只有转出来的文字和截图会发给你选的模型。

---

## 第 0 步：装 Claude Code

Claude Code 是 Anthropic 官方的终端工具。三个系统装法不一样：

```bash
# macOS / Linux / WSL（打开"终端"，粘贴回车）
curl -fsSL https://claude.ai/install.sh | bash

# Windows：打开 PowerShell（不是 CMD），粘贴回车
irm https://claude.ai/install.ps1 | iex
```

装完关掉终端重新打开，输入 `claude --version`，能看到版本号就算装好了。

> Windows 建议顺手装一下 [Git for Windows](https://git-scm.com/downloads/win)，
> 这样 Claude Code 能用 bash 跑脚本；不装也能用，会退回到 PowerShell。

### 登录：三选一

第一次运行 `claude` 会让你登录。有三种方式，选一种就行：

**方式 A：Claude 订阅账号（最省事）**
有 Claude Pro / Max 的账号，直接 `claude`，跟着浏览器登录。免费版账号**不能**用 Claude Code。

**方式 B：Anthropic API key**
在 https://console.anthropic.com 建一个 key，然后设置环境变量，再运行 `claude`，它会问你要不要用这个 key：

```bash
# macOS / Linux：写进 ~/.zshrc 或 ~/.bashrc
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# Windows PowerShell（只对当前窗口有效；永久的话去"编辑系统环境变量"里加）
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxx"
```

**方式 C：搭配别家的 API（DeepSeek / Kimi / 智谱 GLM 等）**
这几家都提供"Anthropic 兼容接口"，Claude Code 只要改两个环境变量就能把请求发到它们那里。最干净的做法是写进 Claude Code 的配置文件，
macOS/Linux 在 `~/.claude/settings.json`，Windows 在 `C:\Users\你的用户名\.claude\settings.json`（没有就新建）：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "你的 DeepSeek API key",
    "ANTHROPIC_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-flash"
  }
}
```

换成别家只要改 `ANTHROPIC_BASE_URL`、key 和模型名：

| 服务商 | ANTHROPIC_BASE_URL | 模型名看哪里 |
|-------|-------------------|-------------|
| DeepSeek | `https://api.deepseek.com/anthropic` | https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/ |
| Kimi（月之暗面） | `https://api.moonshot.cn/anthropic`（国内）/ `https://api.moonshot.ai/anthropic`（海外） | https://platform.moonshot.cn/docs |
| 智谱 GLM | `https://open.bigmodel.cn/api/anthropic` | https://docs.bigmodel.cn/cn/guide/develop/claude |

模型名各家改得很勤，**以它们自己的文档为准**。用方式 C 时注意两点：

- **做课件笔记需要模型能看图**（截帧、contact sheet、PDF 里的图）。选一个支持图片输入的模型，不然录像里的幻灯片它读不了。纯会议纪要只用到文字，什么模型都行。
- 用了 `ANTHROPIC_AUTH_TOKEN` 就不要再设 `ANTHROPIC_API_KEY`，两个一起设会打架。

改完配置重新运行 `claude`，输入 `/status` 能看到当前用的是哪个接口和模型。

---

## 第 1 步：装这个 skill

skill 就是一个文件夹，放到 Claude Code 的 skills 目录下它就会自动认识：

```bash
# macOS / Linux
git clone https://github.com/normanqvq/lecture-notes-maker ~/.claude/skills/lecture-notes-maker

# Windows PowerShell
git clone https://github.com/normanqvq/lecture-notes-maker "$env:USERPROFILE\.claude\skills\lecture-notes-maker"
```

没有 git 的话，去 GitHub 页面点绿色的 **Code → Download ZIP**，解压后把文件夹改名为 `lecture-notes-maker`，放进上面那个 `skills` 目录里。

验证：在终端运行 `claude`，输入 `/skills`，列表里应该有 `lecture-notes-maker`。

---

## 第 2 步：装本地依赖

下面按"你要用哪个功能"分开。先装 Python 3（macOS 自带，Windows 去 python.org 装，勾上 *Add to PATH*）。
指南里写 `python`，如果你的电脑上只有 `python3`（macOS 常见），把 `python` 换成 `python3`、`pip` 换成 `pip3` 即可。

### 2a. 生成 PDF 笔记（笔记模式必装）

```bash
pip install weasyprint pillow pypdfium2
```

Windows 还要装 GTK 运行库，否则 weasyprint 会报 `cannot load library 'libgobject-2.0-0'`：

```powershell
winget install tschoonj.GTKForWindows
```

页面检查用 poppler（可选但推荐，没有它会退回用 pypdfium2）：

```bash
brew install poppler                     # macOS
winget install oschwartz10612.Poppler    # Windows
sudo apt install poppler-utils           # Linux
```

中文笔记需要字体（约 33 MB，下载一次）：

```bash
cd ~/.claude/skills/lecture-notes-maker
python assets/get_fonts.py
```

### 2b. 读视频（上课录像和会议录像都要）

需要 ffmpeg（拆音频、截图）和 whisper.cpp（本地语音转文字）：

```bash
# macOS
brew install ffmpeg whisper-cpp

# Windows PowerShell
winget install Gyan.FFmpeg
#   whisper：去 https://github.com/ggml-org/whisper.cpp/releases 下载 whisper-bin-x64.zip，
#   解压，然后把解压出来的文件夹加进 PATH，或者设置：
#   $env:WHISPER_CLI = "C:\path\to\whisper-cli.exe"

# Linux
sudo apt install ffmpeg
#   whisper.cpp 需要自己编译，把 whisper-cli 放到 PATH 里
```

然后下载 whisper 模型（约 1.6 GB，一次性）。第一次运行脚本时它会把适合你系统的下载命令打印出来，直接复制运行即可。macOS/Linux 是：

```bash
mkdir -p ~/.local/share/whisper-cpp && curl -L -o ~/.local/share/whisper-cpp/ggml-large-v3-turbo.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
```

自检：

```bash
ffmpeg -version
whisper-cli --help
```

两个都能出东西就好了。

---

## 第 3 步：用起来

**关键习惯：在放材料的文件夹里启动 `claude`。** 它只看得到当前文件夹和子文件夹。

### 课件 → 笔记

```bash
cd ~/Desktop/CG2028_Lec5     # 里面放着 Lec5.pdf
claude
```

然后用中文或英文说：

> 用 Lec5.pdf 给我做一份复习笔记 PDF，中文的。

它会自己读 PDF、写 HTML、生成 `notes.pdf`，并且渲染出图片检查排版。整个过程会让你确认几次是否允许它运行命令，看一眼点允许就行。

### 上课录像 → 笔记

把录像放进同一个文件夹，说：

> 这是第 5 节课的录像 lecture.mp4，做成复习笔记。

它会先跑 `assets/extract_video.py`（转文字 + 截幻灯片），再写笔记。一小时的录像转文字大约要 15–20 分钟，耐心等。
如果课件 PDF 和录像都有，两个都放进去：课件是内容来源，录像只用来标"老师强调了什么"。

### 会议录像 → 会议纪要

```bash
cd ~/Desktop/weekly_sync     # 里面放着 meeting.mp4
claude
```

> 这是我们周会的录像 meeting.mp4，帮我总结成会议纪要。

它会进入会议模式：

1. 运行 `python assets/extract_video.py meeting.mp4 --transcript-only --lang auto`
   （`--transcript-only` 表示不截图，因为会议画面基本是人脸；`--lang auto` 自动识别中英文）。
2. 通读转出来的 `meeting_extracted/index.md`。
3. 写出 `minutes.md`：三句话总结、决定了什么、行动项表格（谁 / 做什么 / 什么时候 / 录像时间戳）、没解决的问题、按顺序的议题。**没说过的负责人和截止日期它不会瞎编**，会写"未指定"。

要 PDF 的话再说一句"导出成 PDF"。会议里如果共享了屏幕（有 PPT 或文档），告诉它"会议里有共享屏幕，截图也要看"，它就不会加 `--transcript-only`。

### 只想要文字稿，不要 AI 总结

这一步不需要 AI，脚本可以单独跑：

```bash
python ~/.claude/skills/lecture-notes-maker/assets/extract_video.py meeting.mp4 --transcript-only --lang zh
```

输出在 `meeting_extracted/` 里：`transcript.srt`（带时间戳的字幕文件）和 `index.md`（按 5 分钟分段的可读版本）。

---

## 不用 Claude Code，用别的工具怎么办

这个 skill 的核心就是 `SKILL.md` 这份"说明书"加几个 Python 脚本，不绑定 Claude Code：

- **OpenAI Codex CLI**：它用同样的 SKILL.md 格式，把文件夹放到 `~/.codex/skills/lecture-notes-maker` 就行，然后在 Codex 里用 `$lecture-notes-maker` 或 `/skills` 调用。
- **Cursor / 其他能读文件、能跑命令的 agent**：把整个仓库放进项目，对它说"先读 SKILL.md，按照里面的流程用 lecture.mp4 做笔记"。
- **只有网页版 ChatGPT / Claude / Kimi 的情况**：自己先跑上面"只想要文字稿"那一步，然后把 `index.md` 和 `references/meeting-summary.md`（会议纪要的模板和规则）一起粘进对话框，说"按这个模板总结"。
  做课件笔记的话就把 `SKILL.md` 里的 Step 2–4 和课件一起给它；只是没有 build 脚本，最后的 PDF 得自己想办法。

---

## 常见问题

**`claude: command not found`** — 装完没重开终端，或者 PATH 没加上。重开终端再试；Windows 检查 `%USERPROFILE%\.local\bin` 在不在 PATH 里。

**`whisper-cli not found`** — Windows 上解压后的文件夹没进 PATH。最简单的是设置 `WHISPER_CLI` 环境变量指向 `whisper-cli.exe` 的完整路径。

**`whisper model not found at …`** — 模型没下。复制报错下面打印的那条命令运行即可。

**转出来的字幕是英文，但会议是中文** — 加 `--lang zh`。中英混说用 `--lang auto`。

**20 分钟的录像只截出五六张幻灯片** — 白底 PPT 加淡入淡出会被默认阈值漏掉，让 Claude 加 `--scene 0.012` 重跑一次。

**中文 PDF 打开是乱码或方块** — 字体没装，运行 `python assets/get_fonts.py`。

**用了第三方 API，读视频截图时报错或答非所问** — 那个模型不支持图片输入。换支持视觉的模型，或者只用会议纪要功能。

**一小时的录像跑了 10 分钟就断了** — 让 Claude 用 `nohup … &` 在后台跑（SKILL.md 里有写），它默认会这么做；如果没有，提醒一句。

---

## 一句话版本

```
装 Claude Code → 登录（订阅 / API key / 第三方接口）
→ git clone 到 ~/.claude/skills/
→ pip install weasyprint pillow pypdfium2；brew install ffmpeg whisper-cpp poppler；下模型
→ cd 到放材料的文件夹，运行 claude，说"给我做笔记"或"总结这个会议"
```
