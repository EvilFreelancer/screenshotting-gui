# Authoring & maintaining `screenshotting-gui`

Agent guide for editing **this skill's own repo**. For the catalog-level sync
process see `AGENTS.md` in the [rpa-skills](https://github.com/EvilFreelancer/rpa-skills)
aggregator.

## What this skill is

A deterministic, general-purpose pipeline to screenshot a **running GUI app** on an
isolated Xvfb display, drive it with python-Xlib (XTEST), and annotate with
ImageMagick. The canonical instructions are `SKILL.md` (loaded by progressive
disclosure). Keep it app-agnostic - no per-application coordinate tables baked in.

## Non-negotiable invariant

**Target display `:99` (Xvfb), never `:0`.** The scripts default their own target to
`:99`; the launched app reads `$DISPLAY`, so the workflow always exports
`DISPLAY=:99`. Any change that could send input or a capture to `:0` is a defect.

## Layout

```
screenshotting-gui/
├─ SKILL.md                 # frontmatter (name, version, description) + workflow + gotchas
├─ scripts/
│  ├─ xctl.py               # XTEST driver (move/click/key/type/scroll/drag/place/shot/winlist)
│  ├─ xpaste.py             # CLIPBOARD owner for unicode paste
│  └─ annotate.py           # ImageMagick: box/crop/vstack/arrow
├─ README.md                # human overview
├─ .claude-plugin/ .codex-plugin/ .cursor-plugin/   # per-agent manifests (mirror version + description)
└─ LICENSE
```

## Dependency policy

Scripts use **stdlib + python-Xlib + ImageMagick only**. The optional faster capture
path may use Pillow, but the default (`import`) must keep working without it. No
`xdotool`/`wmctrl`/`pyautogui`, no root, no install steps at runtime.

## Testing changes

Validate on a real Xvfb, not by eye. Bring up `Xvfb :99`, launch a controllable GUI
(a small Tk window is enough; `xterm`/`xclock` if present), and exercise every
`xctl.py` command, the `xpaste.py` unicode path, and each `annotate.py` subcommand,
checking the output PNGs. A safe way to run the whole matrix is to dispatch it to a
subagent that is told the `:99`-only rule. Keep test artifacts out of the repo.

## When you change the skill

Bump `version` in `SKILL.md` **and** all three manifests together, keep the
`description` identical across the manifests, then mirror the change into the
`rpa-skills` catalog (both marketplace manifests, the README Skills table, and
`install.sh`) per that repo's `AGENTS.md`. Run `python3 -m py_compile scripts/*.py`
before committing.
