# Construction and assembly in CAD

These two films use the Baghdad design models to show how components fit
together. Both are downloadable MP4s with on-screen captions and chapter
markers. The staged timing illustrates the sequence of work.

| Film | Duration | What you can follow |
|---|---:|---|
| [Viaduct construction](https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/assets/assembly-animations/viaduct.mp4) | 1:19 | Two workfronts, excavation and footing pours, pier forms and shared crossheads, U-girder casting, flatbed delivery on temporary deck rail, gantry placement and the closure bay. |
| [Train body and bogie frame assembly](https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/assets/assembly-animations/train.mp4) | 1:20 | Stock preparation, the underframe and side frames, roof and end elements, assembly of the powered bogie frames, and the finished bare steel assembly. |

The viaduct uses the [20 m rail-fed concept model](../../../cities/Baghdad/engineering/mechanical/civil/rail-fed/CONCEPT-GEOMETRY.md).
Formwork, handling accessories and motions illustrate the sequence. The site
still needs surveyed foundations, verified temporary deck loads, an equipment
configuration and an approved erection method.

The train uses the named part geometry from the
[Baghdad prototype package](../../../cities/Baghdad/engineering/prototype/airport-prototype.zip).
The assembly contains 120 body pieces and 24 bogie-frame pieces.
The film follows the bare body and bogie frames in the
[rapid-production workcell study](../../../cities/Baghdad/engineering/prototype/rapid-production/README.md).
Production release, welding procedures, installed equipment and inspection of
finished interfaces have their own evidence requirements.

## Reproduce the films

Run from the repository root with Python, NumPy, Pillow, DejaVu Sans fonts and
FFmpeg with libx264. The renderer reads the named OBJ parts and keeps overlays
and equipment staging in the shot files. Each film has a 20,000,000-byte cap.
The [render receipt](receipt.json) identifies source and output hashes and lists
the chapter times.

```sh
python3 docs/assets/assembly-animations/render.py --output build/assembly-animations
python3 docs/assets/assembly-animations/render.py --clip train --still 22
```
