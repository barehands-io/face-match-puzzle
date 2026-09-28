---
name: blender-art-pipeline
description: Create or modify character artwork in Blender and export game-ready face pieces. Use when adding a character, editing art, or exporting PNG pieces for Godot.
---

# Blender art pipeline

Blender 5.2 lives at `/Applications/Blender.app/Contents/MacOS/Blender` (macOS). Everything is scripted
with Blender's Python (`bpy`) and run headless — no manual clicking needed.

## Existing character
- Script: `art/blender/scripts/create_character.py` — builds the redhead girl as an editable 2.5D
  cut-paper scene (Bezier curve layers with small extrusion, emission-heavy pigment materials,
  orthographic front camera at 1502×1600).
- Run: `Blender --background --factory-startup --python art/blender/scripts/create_character.py -- --preview`
  (`--no-render` to only save the .blend).
- Collections are numbered layers: `00 Paper`, `01 Charcoal halo`, `02 Silhouette`, `03 Face and cheeks`,
  `04 Eyes`, `05 Nose`, `06 Mouth`, `07 Bob haircut`, `08 Hair strands`, `80 Cameras`, `90 Reference`.
- Coordinates are authored in reference-image pixels via `position(x, y)` (SCALE=200 px per Blender unit).

## Style
Flat painted-paper look: saturated orange hair with sienna brush strokes, peach skin, red round cheeks,
ivory eyes with dusty-blue irises, sage-green paper background with grey charcoal halo.

## Exporting game pieces (to build)
Each draggable piece must become **one transparent PNG**, all rendered from the same front camera so
positions line up:
1. For each piece, render only its collection(s) with `film_transparent = True`, other collections hidden.
2. Crop to the alpha bounding box; record the crop offset.
3. Write `pieces.json`: `{ "id", "file", "target_x", "target_y", "z_order" }` in base-image pixels.
4. Render the **blank base** (paper, halo, silhouette, face, cheeks, ears, collar) separately.
5. Render the **example thumbnail** (everything).
Output to `game/assets/characters/<character_id>/`.

Group multi-part features into one piece (eye = white + iris + pupil + highlight + dry-brush edge).
Hair currently spans collections 07 + 08; decide whether it's one piece or left/right/fringe.

## Verification
Re-open the saved .blend headlessly and assert object/collection counts; always view the rendered PNG.
