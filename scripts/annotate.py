#!/usr/bin/env python3
"""annotate.py - post-process screenshots with ImageMagick (deterministic).

Wraps the few `convert` invocations that are fiddly to get right by hand: a
rounded highlight rectangle around a region, a crop, and a vertical stack of two
honest crops of the same window (the "red run -> green run" montage).

Commands:
  box   IN OUT X1 Y1 X2 Y2 [--color #ff6b35] [--width 5] [--radius 14]
        draw a rounded rectangle outline around the corners (X1,Y1)-(X2,Y2)
  crop  IN OUT X Y W H
        crop a W*H region at (X,Y)
  vstack OUT IN1 IN2 [--gap 12] [--bg '#0d1117']
        stack two images vertically, centered, with a gap
  arrow IN OUT X1 Y1 X2 Y2 [--color #ff6b35] [--width 5]
        draw a line from (X1,Y1) to (X2,Y2) with an arrow head at the end

The default accent (#ff6b35, width 5, radius 14) matches the course screenshots.
"""
import math
import subprocess
import sys


def _opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def box(a):
    inp, out, x1, y1, x2, y2 = a[0], a[1], *map(int, a[2:6])
    color = _opt(a, "--color", "#ff6b35")
    width = _opt(a, "--width", "5")
    radius = _opt(a, "--radius", "14")
    subprocess.run([
        "convert", inp, "-stroke", color, "-strokewidth", width,
        "-fill", "none",
        "-draw", f"roundrectangle {x1},{y1} {x2},{y2} {radius},{radius}",
        out,
    ], check=True)
    print(out)


def crop(a):
    inp, out, x, y, w, h = a[0], a[1], *map(int, a[2:6])
    subprocess.run(["convert", inp, "-crop", f"{w}x{h}+{x}+{y}", "+repage", out],
                   check=True)
    print(out)


def vstack(a):
    out, in1, in2 = a[0], a[1], a[2]
    gap = _opt(a, "--gap", "12")
    bg = _opt(a, "--bg", "#0d1117")
    subprocess.run([
        "convert", in1, in2, "-background", bg, "-gravity", "center",
        "-splice", f"0x{gap}", "-append", out,
    ], check=True)
    print(out)


def arrow(a):
    inp, out, x1, y1, x2, y2 = a[0], a[1], *map(int, a[2:6])
    color = _opt(a, "--color", "#ff6b35")
    width = _opt(a, "--width", "5")
    # arrow head: two barbs angled back from the tip along the line direction
    ang = math.atan2(y2 - y1, x2 - x1)
    head = max(12, int(float(width) * 4))
    spread = math.radians(28)
    lx, ly = x2 - head * math.cos(ang - spread), y2 - head * math.sin(ang - spread)
    rx, ry = x2 - head * math.cos(ang + spread), y2 - head * math.sin(ang + spread)
    subprocess.run([
        "convert", inp, "-stroke", color, "-strokewidth", width, "-fill", color,
        "-draw", f"line {x1},{y1} {x2},{y2}",
        "-draw", f"line {x2},{y2} {int(lx)},{int(ly)}",
        "-draw", f"line {x2},{y2} {int(rx)},{int(ry)}",
        out,
    ], check=True)
    print(out)


CMDS = {"box": box, "crop": crop, "vstack": vstack, "arrow": arrow}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help") or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help") else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
