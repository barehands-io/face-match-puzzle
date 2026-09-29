---
name: blender-art-pipeline
description: Create or modify character artwork in Blender and export game-ready face pieces. Use when adding a character, editing art, or exporting PNG pieces for Godot.
---

# Blender art pipeline

Blender 5.2 lives at `/Applications/Blender.app/Contents/MacOS/Blender` (macOS). Everything is scripted
with Blender's Python (`bpy`) and run headless — no manual clicking needed.

## Current style and characters: flat painted GBAM
The owner corrected the rendering style: **flat painted illustration, NOT 3D clay**.
Read `docs/GAME_DESIGN.md` and view
`art/gbam_kit/01_REFERENCE_IMAGES/OWN_STYLE_PRIMARY/gbam_flat_style_reference_sheet.png`.
That reference takes precedence over the kit's 3D material/lighting instructions. GBAM still
supplies the character designs, diversity, soft proportions and warm palette.

- Launch pair: `CHR_M_001_COILS_YELLOW` and `CHR_F_001_PUFFS_OVERALLS`.
- Script: `art/blender/scripts/create_gbam_character.py`.
- Run: `Blender --background --factory-startup --python-exit-code 1 --python art/blender/scripts/create_gbam_character.py -- --character all`.
  Use `boy` or `girl` instead of `all` for one character.
- Validate existing scenes/images without rebuilding: the same command with `--verify-only`.
- Reuse `create_character.py` helpers: `shape`, `oval`, `polygon`, `brush`, `pigment`.
  Editable Bezier layers have tiny extrusion/bevel. Pigment noise ramps feed directly into
  emission, with no diffuse/specular shaders, lights or volumetric meshes. Standard colour
  management preserves flat palette colours and the paint texture.
- Outputs: `art/blender/gbam-{boy,girl}-portrait-flat.blend`,
  `art/renders/gbam-{boy,girl}-portrait-flat.png`, `art/renders/gbam-{boy,girl}-blank-flat.png`.
  Canvas: 1502×1600, front orthographic, same alignment for full/blank.
- Preserve all earlier non-`-flat` GBAM scenes/renders as history. Their former 3D generator is
  embedded in those `.blend` files and remains in Git history; do not iterate that pipeline.
- Each eye is a flat white almond + dark outline + single dark pupil, with no iris/catchlight.
  Noses have at most two paint accents. Hair uses flat masses with short curved/hatching strokes.
- Hide collections with `draggable = True` for blank faces. Each has a stable `piece_id`.
  The boy has seven pieces; the girl has nine (cap and each puff/flower are separate).
  Collections 01–03 retain head/ears/neck, flat cheek circles and fixed portrait outfits.
- Backgrounds are bold flat panels: yellow boy, coral girl. Keep grain and painted strokes,
  but never introduce 3D shading, gradients or shiny dots.
- Whole-feature exports and the first Godot drag-and-snap prototype now exist in `game/`.

## Original redhead artwork (reuse technique, not character design)
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

## Exporting game pieces
Run `Blender --background --factory-startup --python-exit-code 1 --python art/blender/scripts/export_puzzle_pieces.py`.
The script exports both launch characters from their saved flat scenes without changing the scenes.
It generates the complete example, blank base, cropped transparent feature PNGs, and `pieces.json`
under `game/assets/characters/<character_id>/`. Target coordinates are crop centres in source pixels.
The Godot mechanics test reconstructs the complete face and compares it against the example.

Each draggable piece must become **one transparent PNG**, all rendered from the same front camera so
positions line up:
1. For each piece, render only its collection(s) with `film_transparent = True`, other collections hidden.
2. Crop to the alpha bounding box; record the crop offset.
3. Write `pieces.json`: `{ "id", "file", "target_x", "target_y", "z_order" }` in base-image pixels.
4. Render the **blank base** (head, ears, neck, cheeks, fixed outfit/background) separately.
5. Render the **example thumbnail** (everything).
Output to `game/assets/characters/<character_id>/`.

Group multi-part features into one piece (eye = white + iris + pupil + highlight).
GBAM piece boundaries are recorded in `piece_id` collections. Keep the camera, but hide
`00 - Painted background`, the base and other pieces for alpha. Do not add lights.
Presentation PNGs include coloured backgrounds and are not individual transparent game pieces.

## Verification
Re-open the saved .blend headlessly and assert object/collection counts; always view the rendered PNG.
