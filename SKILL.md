---
name: screenshotting-gui
version: 1.0.0
description: >
  Use when you must produce clean, repeatable screenshots of a running GUI desktop
  application (an IDE like Cursor or VS Code, a native app, a browser window) for
  documentation, a course, a README, or a bug report - captured on an isolated Xvfb
  virtual display so synthetic input and captures never touch the operator's real
  desktop, scripted with python-Xlib (XTEST), and annotated (rounded highlight box,
  crop, arrow) with ImageMagick. Triggers include "take / redo a screenshot of an
  app's UI", "screenshot a menu or dialog in a specific state", "automate app
  screenshots for docs", "highlight a region on a screenshot". Not for grabbing the
  operator's live :0 desktop, and not for pure web-page shots (use a headless browser
  for those).
---

# Screenshotting a GUI app

Produce documentation-grade screenshots of a **running GUI application** without a
window manager and without touching the operator's screen. The app runs on a
throwaway **Xvfb** display; you drive it to the exact state you want with synthetic
X input, capture the frame, and annotate it.

Everything the model already knows (what X11, ImageMagick or a clipboard are) is
omitted on purpose - this file is only the parts that are easy to get wrong.

## The one rule that keeps it safe

**Run on display `:99` (Xvfb), never `:0`.** `:0` is the operator's live desktop -
clicking, typing and screenshotting it is a privacy and correctness disaster.

The subtle trap: `xctl.py` / `xpaste.py` default *their own* target to `:99`, but any
GUI app you launch reads **`$DISPLAY`**. If `$DISPLAY` is still `:0`, the app opens
on the real screen while your captures read `:99` - `winlist` comes back empty and
you capture a black frame. **Always `export DISPLAY=:99` for the app launch**, not
just `XCTL_DISPLAY`.

## Toolchain

Deterministic pieces live in `scripts/` (run any with `--help`):

| Script | Role |
|--------|------|
| `scripts/xctl.py` | Drive the app: `move click key type scroll drag place shot winlist` via python-Xlib XTEST. |
| `scripts/xpaste.py` | Serve UTF-8 on the CLIPBOARD so `key ctrl+v` pastes unicode / non-Latin text. |
| `scripts/annotate.py` | ImageMagick post-processing: `box` (rounded highlight), `crop`, `vstack`, `arrow`. |

Requirements: `Xvfb`, `python3` + `python-Xlib`, ImageMagick (`import`, `convert`).
Capture default is ImageMagick `import` (no extra dependency, no max-size ceiling).
Fallback if ImageMagick is unavailable: python-Xlib `root.get_image` + Pillow
(~2x faster, but needs `Pillow` and must tile a root above ~4.2 MP; pixel order is
`BGRX`, not `RGB`).

## Workflow

```bash
DISP=:99
export XCTL_DISPLAY=$DISP
S=scripts   # path to this skill's scripts

# 1. Isolated display
Xvfb $DISP -screen 0 1920x1080x24 -ac >/tmp/xvfb.log 2>&1 &
sleep 1; DISPLAY=$DISP xdpyinfo >/dev/null || { echo "Xvfb down"; exit 1; }

# 2. Launch the app ON :99 (export DISPLAY, not only XCTL_DISPLAY)
DISPLAY=$DISP <app> &            # e.g. an IDE, a browser, a native app
sleep 2                          # heavy Electron/JVM apps need 3-8 s; poll with winlist
python3 $S/xctl.py winlist       # confirm the window is on :99, note its geometry

# 3. Drive it to the exact state you want (see command table below)
python3 $S/xctl.py click 1490 1003        # open a menu, toggle a panel, etc.
sleep 0.5

# 4. Capture (full, or crop to the region)
python3 $S/xctl.py shot /tmp/raw.png --crop 1270 560 650 520

# 5. Annotate and save
python3 $S/annotate.py box /tmp/raw.png out.png 1300 600 1720 680
```

Find pixel coordinates from a `winlist` geometry plus a full `shot` you eyeball;
without a window manager, screen coordinate = window origin + widget offset.

## Driving the app - `xctl.py`

| Command | Purpose |
|---------|---------|
| `winlist` | List mapped windows with `class`, `name`, geometry - find your target and its origin. |
| `move X Y` | Move the pointer (origin = top-left of the display). |
| `click X Y [--button N] [--double]` | Move then click (1 left, 2 middle, 3 right). |
| `key COMBO ...` | Key chords: `ctrl+shift+p`, `ctrl+v`, `Return`, `Escape`, `BackSpace`. |
| `type TEXT` | Type **ASCII only** (layout-correct via the live keymap). |
| `scroll up\|down [N]` | Wheel N notches **at the current pointer** - `move` over the region first. |
| `drag X1 Y1 X2 Y2` | Press-move-release - resize a panel by dragging its splitter. |
| `place SUBSTR X Y W H` | Move+resize the first window matching name/class - fixes windows opened off-screen without a WM. |
| `shot OUT [--crop X Y W H]` | Capture the display; crop to a region. |

Focus follows X input focus: **click into the target widget before `type` or
`ctrl+v`**, or the keys go nowhere.

## Unicode / non-Latin text - `xpaste.py`

`type` is ASCII-only by design. For Cyrillic or any symbol-heavy string (`@`, `{}`),
never type it - paste it:

```bash
python3 $S/xpaste.py "любой текст с @ и {скобками}" 15 &   # own CLIPBOARD ~15 s
sleep 0.6                                                   # let it acquire first
python3 $S/xctl.py click 1580 200                          # focus the input
python3 $S/xctl.py key ctrl+v
```

## Annotating - `annotate.py`

```bash
python3 $S/annotate.py box  in.png out.png X1 Y1 X2 Y2   # rounded #ff6b35 outline
python3 $S/annotate.py crop in.png out.png X Y W H       # crop a region
python3 $S/annotate.py arrow in.png out.png X1 Y1 X2 Y2  # line + arrowhead at the tip
python3 $S/annotate.py vstack out.png top.png bottom.png # stack two honest crops
```

Default accent `#ff6b35`, width `5`, radius `14`.

## Gotchas

- **`$DISPLAY` vs `$XCTL_DISPLAY`.** The app reads `$DISPLAY`; the scripts default to
  `:99`. A mismatch silently launches the app on `:0` while you capture `:99` (empty
  `winlist`, black frames, and your keystrokes leaking to the real desktop). Export
  `DISPLAY=:99` for the launch.
- **No window manager is the simpler default.** Without a WM there is no reparenting,
  so screen coordinate = window origin + widget offset (clean math for `place`). Apps
  that need a WM for focus/stacking may want `openbox`/`twm`; try without first.
- **Focus before keys.** XTEST keystrokes and `ctrl+v` route to the focused window -
  click the widget first.
- **`scroll` ignores coordinates** - it wheels at the current pointer; `move` first.
- **Timing.** Give the app ~1-2 s (heavy Electron/JVM apps 3-8 s) before `winlist`;
  give `xpaste.py` ~0.5-1 s to acquire the selection before `ctrl+v`, or you paste
  stale or empty clipboard.
- **`type` skips non-ASCII** (with a stderr warning) - use `xpaste.py`. Shifted ASCII
  (`_ { } @ =`) is handled.
- **Blank-frame check.** A real capture has non-zero pixel stddev; a near-black frame
  means the app is not mapped or you shot the wrong display.
- **`pkill -f xpaste.py` footgun** - it also matches the killing shell's own command
  line. Kill background helpers by numeric PID.
- **UI coordinates drift** between app versions and window sizes - never hardcode from
  memory; `winlist` + a fresh full `shot` first.
- **Reset app state between shots.** For repo-mutating apps (an IDE agent editing
  files), snapshot and restore - e.g. `git -C <project> checkout . && git clean -fd`.

## Quick reference

```bash
export XCTL_DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac & sleep 1
DISPLAY=:99 <app> & sleep 3
python3 scripts/xctl.py winlist
python3 scripts/xpaste.py "текст" 15 & sleep 0.6; python3 scripts/xctl.py key ctrl+v
python3 scripts/xctl.py shot raw.png --crop X Y W H
python3 scripts/annotate.py box raw.png final.png X1 Y1 X2 Y2
pkill -x Xvfb   # or kill the specific PID when done
```
