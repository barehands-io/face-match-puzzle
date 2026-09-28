# Game design — Face Match Puzzle

Status: **discussion / pre-production**. No game code yet.

## Concept
A digital version of a magnetic face-building toy for young children. Each "card" is a character.
The child rebuilds the character's face by placing its features on a blank head.

Reference photos:
- `art/reference/gameplay-concept-clown-box.png` — the physical toy: example card (left), blank face (middle), loose pieces (right).
- `art/reference/redhead-girl-reference.png` — first character card to recreate.

## Core loop
1. Pick a character card.
2. Screen shows: small **example** of the finished face, the **blank face base**, and a **tray** of loose pieces.
3. Child drags a piece onto the face.
4. Near the correct spot → it **snaps** in with a sound/wiggle. Elsewhere → it gently floats back or stays (TBD).
5. All pieces placed → character **celebrates** (animation, sound). Next card.

## Pieces (split by whole facial feature)
Blank base (not draggable): head/face shape, ears, neck, cheeks, background.

Draggable pieces for the redhead girl (first character):
| Piece | Includes |
|---|---|
| Hair (bob) | fringe + side locks + strands (may split into left/right/fringe — TBD) |
| Left eye | white + iris + pupil + highlight |
| Right eye | white + iris + pupil + highlight |
| Nose | outline + highlight + shadow |
| Mouth | lips + interior + teeth |
| Collar/shirt | optional |

Draggable pieces for the clown (confirmed second character, from the toy box):
| Piece | Includes |
|---|---|
| Green bowler hat | green crown + golden trim + dark ribbon |
| Left orange hair tuft | orange silhouette + painted strands |
| Right orange hair tuft | orange silhouette + painted strands |
| Round eye | ivory white + black vertical pupil |
| X eye | ivory white + black X |
| Red ball nose | red circle + shaded rim + painted highlight |
| White smile | ivory smile shape + curved red line |
| Pink-and-white polka-dot bow tie | both wings + knot + dots |

Clown blank base: peach head, ears, neck and red cheeks, on sage/teal paper with a grey charcoal halo.
Each of its eight draggable features has its own Blender collection, including all decorative layers.

## Launch scope (decided)
- **v1 launches with 2 characters:** the redhead girl and the clown from the toy box (both confirmed).

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

Clown source: `art/blender/scripts/create_clown.py` (reuses the redhead script's art helpers).
Editable artwork: `art/blender/clown-portrait.blend`; example portrait: `art/renders/clown-portrait.png`.
Both characters use the same 1502×1600 front orthographic canvas and painted-paper material approach.

## Open questions
- Target age range?
- Match mode, free mode, or both for v1?
- Wrong-spot behaviour: bounce back to tray, or stay where dropped?
- Voice-over / names of features ("Where does the nose go?")?
- Monetisation: paid app, free with character packs, or free?
