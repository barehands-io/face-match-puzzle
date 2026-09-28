---
name: blender-art-pipeline
description: Create or modify character artwork in Blender and export game-ready face pieces. Use when adding a character, editing art, or exporting PNG pieces for Godot.
---

# Blender art pipeline

Blender 5.2 lives at `/Applications/Blender.app/Contents/MacOS/Blender` (macOS). Everything is scripted
with Blender's Python (`bpy`) and run headless — no manual clicking needed.

## Current style and characters: GBAM
The supplied modular 3D kit replaces the old painted-paper art. Read `docs/GAME_DESIGN.md`,
`art/gbam_kit/00_START_HERE/README.md`, `AI_TASK_SEQUENCE.md`, and
`art/gbam_kit/02_STYLE_SYSTEM/STYLE_BIBLE.md` before building.

- Launch pair: `CHR_M_001_COILS_YELLOW` and `CHR_F_001_PUFFS_OVERALLS`.
- Script: `art/blender/scripts/create_gbam_character.py`.
- Run: `Blender --background --factory-startup --python-exit-code 1 --python art/blender/scripts/create_gbam_character.py -- --character all`.
  Use `boy` or `girl` instead of `all` for one character; `--no-render` saves scenes only.
- Validate existing scenes/images without rebuilding: the same command with `--verify-only`.
- The script runs the kit bootstrap (adapted for the Blender 5 Eevee engine name), then builds the
  shared neutral head, required face modules, and coils/puffs. It uses matte Principled materials,
  metric units, forward -Y, up +Z, 1024×1024 front orthographic framing and soft Cycles lighting.
- Outputs: `art/blender/gbam-{boy,girl}-portrait.blend`,
  `art/renders/gbam-{boy,girl}-portrait.png`, `art/renders/gbam-{boy,girl}-blank.png`.
- `01_BASE` contains the head, neck, ears and coral cheeks. `02_FACE` contains one subcollection
  per eye, brow, nose and mouth. `03_HAIR_HEADWEAR` contains one boy hair piece or three girl hair
  pieces (cap, left puff/flower, right puff/flower). Each draggable collection has a `piece_id`.
- Hide `02_FACE` and `03_HAIR_HEADWEAR` for the blank render. `04_CLOTHING` contains fixed
  portrait-only shoulder accents, not full-body outfits.
- The common neutral cage is 0.440×0.400×0.500 m (X/Y/Z), with 4,056 quads. The wide eye variant
  uses 1.20× canonical width and 1.10× height; the kit's iris/pupil sizes and anchors stay unchanged.
- These are portrait prototypes. Full face/hair libraries, rigging, facial deformation topology,
  full bodies, UV/LOD work and individual game-piece exports are not complete.

## Historical artwork: redhead girl (do not build on for launch)
- Script: `art/blender/scripts/create_character.py` — builds the redhead girl as an editable 2.5D
  cut-paper scene (Bezier curve layers with small extrusion, emission-heavy pigment materials,
  orthographic front camera at 1502×1600).
- Run: `Blender --background --factory-startup --python art/blender/scripts/create_character.py -- --preview`
  (`--no-render` to only save the .blend).
- Collections are numbered layers: `00 Paper`, `01 Charcoal halo`, `02 Silhouette`, `03 Face and cheeks`,
  `04 Eyes`, `05 Nose`, `06 Mouth`, `07 Bob haircut`, `08 Hair strands`, `80 Cameras`, `90 Reference`.
- Coordinates are authored in reference-image pixels via `position(x, y)` (SCALE=200 px per Blender unit).

## Historical painted-paper style
Flat painted-paper look: saturated orange hair with sienna brush strokes, peach skin, red round cheeks,
ivory eyes with dusty-blue irises, sage-green paper background with grey charcoal halo.

## Historical artwork: clown (no longer a launch character)
- Script: `art/blender/scripts/create_clown.py`, reusing the adjacent redhead script's shape,
  brush, pigment and camera helpers.
- Run: `Blender --background --factory-startup --python art/blender/scripts/create_clown.py`
  (`--preview` for a half-size draft, `--no-render` to only save the .blend).
- Output: `art/blender/clown-portrait.blend` and `art/renders/clown-portrait.png`.
- Collections 00–03 form the blank base: paper, charcoal halo, head/ears/neck, red cheeks.
- Collections 04–11 are eight complete pieces: hat, left tuft, right tuft, round eye, X eye,
  red nose, white smile, bow tie. Each has a stable `piece_id` and `draggable = True`.
  All decorations stay inside their owning piece collection.
- The saved scene always retains the full 1502×1600 front-camera framing, even with `--preview`.
  Preview output is `art/renders/clown-preview.png`.

## Exporting game pieces (to build)
Each draggable piece must become **one transparent PNG**, all rendered from the same front camera so
positions line up:
1. For each piece, render only its collection(s) with `film_transparent = True`, other collections hidden.
2. Crop to the alpha bounding box; record the crop offset.
3. Write `pieces.json`: `{ "id", "file", "target_x", "target_y", "z_order" }` in base-image pixels.
4. Render the **blank base** (head, ears, neck, cheeks, fixed outfit/background) separately.
5. Render the **example thumbnail** (everything).
Output to `game/assets/characters/<character_id>/`.

Group multi-part features into one piece (eye = white + iris + pupil + highlight).
GBAM piece boundaries are already recorded in `piece_id` subcollections. Keep the lights and camera
enabled when isolating a piece, but hide `STUDIO_BACKDROP`, the base and other geometry for alpha.
Presentation PNGs include the mint backdrop and are not individual transparent game pieces.

## Verification
Re-open the saved .blend headlessly and assert object/collection counts; always view the rendered PNG.
