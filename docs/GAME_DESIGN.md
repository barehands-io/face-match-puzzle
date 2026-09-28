# Game design — Face Match Puzzle

Status: **discussion / pre-production**. No game code yet.

## Concept
A digital version of a magnetic face-building toy for young children. Each "card" is a character.
The child rebuilds the character's face by placing its features on a blank head.

Gameplay reference:
- `art/reference/gameplay-concept-clown-box.png` — example card (left), blank face (middle), loose pieces (right).

Current character references: `art/gbam_kit/01_REFERENCE_IMAGES/OWN_STYLE_PRIMARY/`.
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
patches, portrait outfit and mint background. Ears and cheeks remain separate editable assets, but
stay on the blank base. No eyes, eyebrows, nose, mouth or hair remain in the blank render.

**Boy — `CHR_M_001_COILS_YELLOW` (7 draggable pieces)**

| Piece ID | Includes |
|---|---|
| `eye_l` | left eye white + brown iris + dark pupil + catchlight |
| `eye_r` | right eye white + brown iris + dark pupil + catchlight |
| `brow_l` | left thick curved eyebrow |
| `brow_r` | right thick curved eyebrow |
| `nose` | soft geometric wedge |
| `mouth` | wide happy smile + lip edge + interior + upper teeth + tongue |
| `hair_coils` | scalp cap + all short, dense coil masses |

Skin: `SKIN_WARM_MEDIUM`. Yellow hoodie shoulders are a fixed portrait accent.

**Girl — `CHR_F_001_PUFFS_OVERALLS` (9 draggable pieces)**

| Piece ID | Includes |
|---|---|
| `eye_l` | left eye white + brown iris + dark pupil + catchlight |
| `eye_r` | right eye white + brown iris + dark pupil + catchlight |
| `brow_l` | left thick curved eyebrow |
| `brow_r` | right thick curved eyebrow |
| `nose` | soft geometric wedge |
| `mouth` | wide happy smile + lip edge + interior + upper teeth + tongue |
| `hair_cap` | swept scalp cap + shallow hair ridges |
| `hair_puff_l` | left puff bun + its small pink flower |
| `hair_puff_r` | right puff bun + its small pink flower |

Skin: `SKIN_WARM_BROWN`. Green overall straps/bib and coral shirt shoulders are fixed portrait accents.
Left/right IDs follow the kit's anchor labels (L = negative X).
Each piece is one collection with a stable `piece_id`; all its component objects travel together.

## Launch scope (decided)
- **v1 launches with 2 characters**, in the **GBAM style** (see below): `CHR_M_001_COILS_YELLOW` (boy,
  short coils, yellow hoodie) and `CHR_F_001_PUFFS_OVERALLS` (girl, two puff buns, green overalls).
  The earlier redhead-girl/clown painted-paper scenes and scripts in `art/blender/`, plus their
  portrait renders, are superseded and kept only for history. New `gbam-*` files are the active art.

## Art style (decided): GBAM
- The full modular 3D character system supplied in `art/gbam_kit/` replaces the flat cut-paper style.
- Read `art/gbam_kit/00_START_HERE/README.md` and `02_STYLE_SYSTEM/STYLE_BIBLE.md` first.
- Its modular face/hair/headwear parts map directly onto our draggable pieces — even better than the
  original flat art, since GBAM was designed to swap eyes/nose/mouth/hair/headwear independently.
- Game still only needs **front-facing rendered PNGs per piece**, not the full rigged 3D model in-engine.

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
It runs the kit's scene bootstrap, then builds the shared head, required face modules, and coils/puffs
in separate passes. Both characters use the identical 0.440 m wide × 0.500 m high × 0.400 m deep,
4,056-quad neutral head mesh with different palette materials.

| Character | Editable scene | Complete portrait | Blank base |
|---|---|---|---|
| Boy | `art/blender/gbam-boy-portrait.blend` | `art/renders/gbam-boy-portrait.png` | `art/renders/gbam-boy-blank.png` |
| Girl | `art/blender/gbam-girl-portrait.blend` | `art/renders/gbam-girl-portrait.png` | `art/renders/gbam-girl-blank.png` |

Presentation uses the kit's 1024×1024 canvas, a shared front orthographic camera, matte Principled
materials and a soft three-light studio. The `EYE_02_WIDE` variant is 20% wider and 10% taller than
the canonical round globe, keeping the kit's iris/pupil sizes and eye anchors for phone readability.
The slight brow/cheek/flower offsets are intentional asymmetry.

This pass is a **portrait prototype**, not the complete kit asset library: only the face and hair
variants needed by these two characters are built. Full-body modelling, finished clothing assets,
facial deformation loops, rigging, UV/LOD work, and individual transparent piece exports are deferred.
No Godot code yet. The saved scenes contain the complete characters; hiding `02_FACE` and
`03_HAIR_HEADWEAR` produces the blank bases without changing camera framing.

## Open questions
- Target age range?
- Match mode, free mode, or both for v1?
- Wrong-spot behaviour: bounce back to tray, or stay where dropped?
- Voice-over / names of features ("Where does the nose go?")?
- Monetisation: paid app, free with character packs, or free?
