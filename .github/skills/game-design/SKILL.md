---
name: game-design
description: Context and rules for designing or implementing gameplay in the Face Match Puzzle Godot game. Use when building scenes, drag-and-drop, snapping, levels, or discussing features with the owner.
---

# Face Match Puzzle — gameplay skill

Always read `docs/GAME_DESIGN.md` first and update its "Open questions" when the owner decides something.

## Gameplay rules
- Screen: example thumbnail + blank face base + tray of loose pieces.
- Drag with finger/mouse (Godot `InputEventScreenTouch`/`ScreenDrag` + mouse for web/desktop).
- Snap when released within a generous radius (start ~12% of face width) of the piece's target.
- Correct placement: snap tween + sound + small squash. Completion: celebration.
- Never punish. No timers or scores unless the owner asks.
- Pieces load from `game/assets/characters/<id>/pieces.json` so new characters need no code.

## Godot conventions
- Godot 4.x, GDScript only (web export requires it).
- Compatibility renderer so the same project works on web and mobile.
- Stretch mode `canvas_items`, aspect `expand`; design for tablet landscape first.
- Keep touch targets ≥ 48 dp.

## Talking to the owner
The owner is the game designer, not technical. Plain language, short answers, offer choices
(recommended first), don't implement big features without agreement.
