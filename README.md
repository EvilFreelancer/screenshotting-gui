# screenshotting-gui

**`/screenshotting-gui`** — take clean, repeatable screenshots of a GUI
desktop application (Cursor, an IDE, a native app, a browser window) for docs, a
course, or a bug report. The app runs on an **isolated Xvfb display** so synthetic
input and captures never touch the operator's real desktop; you drive it with
**python-Xlib** (XTEST), capture with **ImageMagick**, and annotate with a rounded
highlight box, crop, or arrow.

## Why a skill and not just `import -window root`

A good documentation screenshot needs the app driven to an exact state (a menu open,
a diff visible), captured without a mouse cursor artifact or the operator's private
desktop behind it, and annotated consistently. Doing that by hand every time is slow
and error-prone. This skill packages the safe, deterministic pipeline.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Agent instructions (frontmatter `name`, `version`, `description`) + workflow and gotchas. |
| `scripts/xctl.py` | Drive the app on an X display via XTEST: `move click key type scroll drag place shot winlist`. python-Xlib only. |
| `scripts/xpaste.py` | Own the X CLIPBOARD to serve UTF-8 text, so `ctrl+v` pastes unicode / Russian. python-Xlib only. |
| `scripts/annotate.py` | ImageMagick post-processing: `box`, `crop`, `vstack`, `arrow`. |

## Requirements

`Xvfb`, `python3` with `python-Xlib`, and ImageMagick (`import`, `convert`). Optional
faster capture fallback: `Pillow`. No window manager needed. No root, no `xdotool`.

## Usage

```bash
export XCTL_DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac & sleep 1

# launch the app ON :99 (export DISPLAY, not only XCTL_DISPLAY)
DISPLAY=:99 <app> & sleep 3
python3 scripts/xctl.py winlist        # note the window geometry

# drive -> capture -> annotate
python3 scripts/xpaste.py "текст с @ и {скобками}" 15 & sleep 0.6
python3 scripts/xctl.py click 1580 200 && python3 scripts/xctl.py key ctrl+v
python3 scripts/xctl.py shot raw.png --crop X Y W H
python3 scripts/annotate.py box raw.png final.png X1 Y1 X2 Y2
```

Run any script with `--help` for all flags. **Safety:** everything targets display
`:99` (Xvfb); never `:0`, the operator's live desktop.

## Install

This skill is distributed through the **rpa-skills** catalog (a Claude Code plugin
marketplace), and also installs as a plain **skill folder** (Cursor, OpenAI Codex,
Kimi Code CLI, and others).

**As a plugin (Claude Code)** — add the catalog once, then install this skill from it:

```text
/plugin marketplace add EvilFreelancer/rpa-skills
/plugin install screenshotting-gui@rpa-skills
```

**In Coddy**: the rpa-skills catalog is built into [Coddy](https://coddy.dev) as a system source,
so there is nothing to connect. One sync installs this skill together with the rest of the collection
into `~/.coddy/skills/screenshotting-gui/` and keeps it up to date (or press **Sync all** in Settings → Skills):

```bash
coddy skills sync
```

**As a plain skill folder** — copy or symlink this repository into a skill root (its
`SKILL.md` lives at the repo root):

| Tool          | Path                                        |
|---------------|---------------------------------------------|
| Coddy         | `~/.coddy/skills/screenshotting-gui/`  |
| Claude Code   | `~/.claude/skills/screenshotting-gui/` |
| Cursor        | `~/.cursor/skills/screenshotting-gui/` |
| OpenAI Codex  | `~/.codex/skills/screenshotting-gui/`  |
| Kimi Code CLI | `~/.kimi/skills/screenshotting-gui/`   |

The directory name must match the `name` field in `SKILL.md`.

## How to invoke

- **Slash command** — type `/screenshotting-gui` in agent chat.
- **`@` context** — attach the skill folder or `SKILL.md`.
- **Automatic** — the agent may load it when your request matches the `description` in
  `SKILL.md` (e.g. "redo the screenshot of the app's settings dialog").

## Source & attribution

Part of **[rpa-skills](https://github.com/EvilFreelancer/rpa-skills)** —
[Pavel Rykov](https://t.me/evilfreelancer)'s agent-skills collection (see
[notes on vibe coding](https://t.me/evilfreelancer/1485) and
[cursor-vibe-prompts](https://github.com/EvilFreelancer/cursor-vibe-prompts)).

Distilled from the screenshot pipeline built for the *"Cursor AI"* course.

Licensed under the MIT License — see [LICENSE](LICENSE).
