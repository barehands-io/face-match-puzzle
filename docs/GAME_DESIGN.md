# Game design — Face Match Puzzle

Status: **discussion / pre-production**. No game code yet.

## Concept
A digital version of a magnetic face-building toy for young children. Each "card" is a character.
The child rebuilds the character's face by placing its features on a blank head.

Gameplay reference:
- `art/reference/gameplay-concept-clown-box.png` — example card (left), blank face (middle), loose pieces (right).

Authoritative rendering reference:
`art/gbam_kit/01_REFERENCE_IMAGES/OWN_STYLE_PRIMARY/gbam_flat_style_reference_sheet.png`.
The toy-box characters and `art/reference/redhead-girl-reference.png` are historical art references,
not designs to recreate for launch.

## Core loop
1. Pick a character card.
2. Screen shows: small **example** of the finished face, the **blank face base**, and a **tray** of loose pieces.
3. Child drags a piece onto the face.
4. Near the correct spot → it **snaps** in with a sound/wiggle. Elsewhere → it gently floats back or stays (TBD).
5. All pieces placed → character **celebrates** (animation, sound). Next card.

## Pieces (split by whole facial feature)
Blank base (not draggable): shared rounded-square head, ears with inner details, neck, coral cheek
patches, portrait outfit and flat panel background (yellow for the boy, coral for the girl).
Ears and cheeks remain separate editable assets, but
stay on the blank base. No eyes, eyebrows, nose, mouth or hair remain in the blank render.

**Boy — `CHR_M_001_COILS_YELLOW` (7 draggable pieces)**

| Piece ID | Includes |
|---|---|
| `eye_l` | left flat almond eye white + dark outline + single dark pupil |
| `eye_r` | right flat almond eye white + dark outline + single dark pupil |
| `brow_l` | left thick curved eyebrow |
| `brow_r` | right thick curved eyebrow |
| `nose` | rounded flat skin shape + curved contour + one paint stroke |
| `mouth` | wide happy smile + lip edge + interior + upper teeth + tongue |
| `hair_coils` | flat coiled-hair silhouette + short curved painted strokes |

Skin: `SKIN_WARM_MEDIUM`. Yellow hoodie shoulders are a fixed portrait accent.

**Girl — `CHR_F_001_PUFFS_OVERALLS` (9 draggable pieces)**

| Piece ID | Includes |
|---|---|
| `eye_l` | left flat almond eye white + dark outline + single dark pupil |
| `eye_r` | right flat almond eye white + dark outline + single dark pupil |
| `brow_l` | left thick curved eyebrow |
| `brow_r` | right thick curved eyebrow |
| `nose` | rounded flat skin shape + curved contour + one paint stroke |
| `mouth` | wide happy smile + lip edge + interior + upper teeth + tongue |
| `hair_cap` | swept flat hair silhouette + tapered paint strokes |
| `hair_puff_l` | left puff bun + its small pink flower |
| `hair_puff_r` | right puff bun + its small pink flower |

Skin: `SKIN_WARM_BROWN`. Green overall straps/bib and coral shirt shoulders are fixed portrait accents.
Left/right IDs follow the kit's labels (L = the left side of the portrait).
Each piece is one collection with a stable `piece_id`; all its component objects travel together.

## Launch scope (decided)
- **v1 launches with 2 characters**, in the **GBAM style** (see below): `CHR_M_001_COILS_YELLOW` (boy,
  short coils, yellow hoodie) and `CHR_F_001_PUFFS_OVERALLS` (girl, two puff buns, green overalls).
  The earlier redhead-girl/clown painted-paper scenes and scripts in `art/blender/`, plus their
  portrait renders, are kept for history; their flat illustration technique is reused.
  The GBAM clay-style scenes/renders without `-flat` are also historical and must not be
  overwritten or developed further. Only the new `gbam-*-flat` artwork is active.

## Art style (corrected): flat painted GBAM illustration
- **Flat gouache/poster-style illustration, not 3D clay.** The owner's flat reference sheet above
  takes precedence over the kit's earlier 3D material, mesh and lighting instructions.
- Keep GBAM's character designs, African-led diversity, warm brown palette, oversized head/eyes,
  soft shapes and modular facial features.
- Use flat colour blocks, dark brown outlines, visible paint grain and tapered brush marks.
  Hair is a graphic silhouette with curved/hatching strokes, never shaded spheres.
- Eyes have flat whites and one dark pupil: no iris dome, catchlight dot or specular reflection.
  Noses use at most two painted accents. Mouths are broad flat shapes with visible teeth.
- Blender is an illustration workshop: shallow editable Bezier layers, using the original
  redhead/clown helpers with fully unlit pigment materials. No studio shading, gradients or lights.
- The game needs **front-facing rendered PNGs per piece**, not 3D models.

## Modes (open question)
- **Match mode** — recreate the example exactly (pieces have a correct slot).
- **Free/creative mode** — mix features from any character; no wrong answers.

## Audience & UX
- Target age: TBD (toy box shows 3+).
- Big pieces, generous snap radius, no timers, no losing, positive audio.
- Offline, no ads, no accounts, no data collection in v1.

## Platforms & tech
- Godot 4, GDScript, 2D scenes.
- iOS/iPadOS + Android native (primary). Web export (secondary).
- Landscape orientation (tablet-first) — TBD.

## Art pipeline
Blender (`art/blender/`) → render each piece to its own transparent PNG + a JSON of target positions
→ imported into Godot. See `.github/skills/blender-art-pipeline/SKILL.md`.

Current source: `art/blender/scripts/create_gbam_character.py -- --character all` (run with Blender).
It reuses `create_character.py` for Bezier shapes, ovals, tapered brush strokes and procedural
noise-ramp pigment. Both characters share the same flat head outline with different palette colours.

| Character | Editable scene | Complete portrait | Blank base |
|---|---|---|---|
| Boy | `art/blender/gbam-boy-portrait-flat.blend` | `art/renders/gbam-boy-portrait-flat.png` | `art/renders/gbam-boy-blank-flat.png` |
| Girl | `art/blender/gbam-girl-portrait-flat.blend` | `art/renders/gbam-girl-portrait-flat.png` | `art/renders/gbam-girl-blank-flat.png` |

The canvas is 1502×1600, matching the original illustration pipeline, with a shared front
orthographic camera. Pigment shaders feed directly into emission: colour variations are paint
texture, not 3D lighting. The owner reference and both scripts are embedded in each saved scene.

Each draggable collection has a `piece_id` and `draggable = True`. Hide those collections to
produce the blank base; head, ears, neck, cheeks and clothing remain, with identical camera framing.
The generator reopens both saved scenes and checks flat-only materials, piece grouping and PNG sizes.
Use `--verify-only` to repeat those checks without rebuilding.
Individual transparent piece exports and Godot code are not built yet. Rigging/full-body 3D work
is not part of this corrected illustration pipeline.

## Open questions
- Target age range?
- Match mode, free mode, or both for v1?
- Wrong-spot behaviour: bounce back to tray, or stay where dropped?
- Voice-over / names of features ("Where does the nose go?")?
- Monetisation: paid app, free with character packs, or free?
