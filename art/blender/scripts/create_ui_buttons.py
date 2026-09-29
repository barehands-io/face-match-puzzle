"""Build the flat painted "toy button" UI kit for Face Match Puzzle.

Same technique as the GBAM characters: flat emission-only pigment, dark ink
outlines, procedural paint grain, no gradients/lighting/shading. Each button
is authored on its own small canvas (in source pixels) and rendered at 3x
supersampling for a crisp look on retina screens.

Run with:
  Blender --background --factory-startup --python-exit-code 1 \
    --python art/blender/scripts/create_ui_buttons.py -- --verify-only
Omit --verify-only to rebuild and re-render.
"""

import argparse
from pathlib import Path
import sys

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import create_character as art  # noqa: E402  (reuses shape/pigment/camera helpers)

ROOT = HERE.parents[2]
SUPERSAMPLE = 3
INK = "30291F"  # Matches puzzle.gd's INK ink/text colour.
RING = 4          # Thin ink border visible all around the button.
LIP = 8           # Darker "shade" strip left showing at the bottom.
RADIUS = 24

# id, width, height, fill hex (all in source pixels, matching puzzle.gd's Rect2 sizes).
BUTTONS = [
    ("button_replay", 200, 64, "77CDB2"),  # MINT — "Start again".
    ("button_switch", 230, 64, "E8833B"),  # ORANGE — "Other character".
    ("button_sound", 200, 64, "7965A7"),   # PURPLE — "Sound: on/off".
]


def darken(hex_color, factor=0.72):
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return "".join(f"{max(0, min(255, round(c * factor))):02X}" for c in rgb)


def flat_paint(name, hex_color, grain=0.05):
    """Fully emission-driven pigment: flat colour + grain, no lighting response."""
    mat = art.pigment(name, hex_color, grain=grain, emission_mix=1.0)
    nodes = mat.node_tree.nodes
    output = next(node for node in nodes if node.type == "OUTPUT_MATERIAL")
    emission = next(node for node in nodes if node.type == "EMISSION")
    mat.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    for node in list(nodes):
        if node.type in ("MIX_SHADER", "BSDF_DIFFUSE"):
            nodes.remove(node)
    next(node for node in nodes if node.type == "TEX_NOISE").inputs["Scale"].default_value = 140
    return mat


def rounded_rect_path(x0, y0, x1, y1, r):
    k = r * 0.5522847498
    return (
        f"M {x0 + r} {y0} "
        f"L {x1 - r} {y0} "
        f"C {x1 - r + k} {y0} {x1} {y0 + r - k} {x1} {y0 + r} "
        f"L {x1} {y1 - r} "
        f"C {x1} {y1 - r + k} {x1 - r + k} {y1} {x1 - r} {y1} "
        f"L {x0 + r} {y1} "
        f"C {x0 + r - k} {y1} {x0} {y1 - r + k} {x0} {y1 - r} "
        f"L {x0} {y0 + r} "
        f"C {x0} {y0 + r - k} {x0 + r - k} {y0} {x0 + r} {y0} "
        f"Z"
    )


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for group in list(bpy.data.collections):
        bpy.data.collections.remove(group)
    art.COLLECTIONS.clear()
    for block_type in (bpy.data.materials, bpy.data.curves, bpy.data.cameras):
        for block in list(block_type):
            if block.users == 0:
                block_type.remove(block)
    for text in list(bpy.data.texts):
        bpy.data.texts.remove(text)


def build_button(name, width, height, fill_hex):
    reset_scene()
    art.WIDTH, art.HEIGHT = width, height
    ink = flat_paint(f"{name}_ink", INK, grain=0.03)
    shade = flat_paint(f"{name}_shade", darken(fill_hex), grain=0.05)
    fill = flat_paint(f"{name}_fill", fill_hex, grain=0.05)
    group = "01 - Button"
    art.shape(f"{name} - ink outline", rounded_rect_path(0, 0, width, height, RADIUS),
              ink, 0.0, group, thickness=0.01, bevel=0.0)
    art.shape(f"{name} - shade base",
              rounded_rect_path(RING, RING, width - RING, height - RING, RADIUS - RING),
              shade, 0.02, group, thickness=0.01, bevel=0.0)
    art.shape(f"{name} - bright fill",
              rounded_rect_path(RING, RING, width - RING, height - RING - LIP, RADIUS - RING),
              fill, 0.04, group, thickness=0.01, bevel=0.0)

    scene = bpy.context.scene
    scene.name = name
    front = art.camera(f"{name} - camera", (0, 0, 10), (0, 0, 0), width / art.SCALE)
    scene.camera = front
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8
    scene.render.resolution_x = width * SUPERSAMPLE
    scene.render.resolution_y = height * SUPERSAMPLE
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene["button_id"] = name
    scene["object_count"] = len(scene.objects)
    return scene


def verify(name, width, height):
    scene = bpy.context.scene
    assert scene["button_id"] == name
    assert len(scene.objects) == scene["object_count"] == 4  # 3 shapes + 1 camera.
    assert scene.camera.data.type == "ORTHO"
    assert scene.view_settings.view_transform == "Standard"
    assert (scene.render.resolution_x, scene.render.resolution_y) == (
        width * SUPERSAMPLE, height * SUPERSAMPLE)
    group = bpy.data.collections["01 - Button"]
    assert len(group.objects) == 3
    for mat_name in (f"{name}_ink", f"{name}_shade", f"{name}_fill"):
        mat = bpy.data.materials[mat_name]
        nodes = mat.node_tree.nodes
        output = next(node for node in nodes if node.type == "OUTPUT_MATERIAL")
        assert output.inputs["Surface"].links[0].from_node.type == "EMISSION"
        assert not any(node.type.startswith("BSDF") for node in nodes)
    print(f"VERIFIED BUTTON {name}: flat emission-only paint, ink outline + shade lip.",
          flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    destination = ROOT / "game/assets/ui"
    destination.mkdir(parents=True, exist_ok=True)
    for name, width, height, fill_hex in BUTTONS:
        path = ROOT / f"art/blender/ui-{name.replace('_', '-')}.blend"
        if not args.verify_only:
            build_button(name, width, height, fill_hex)
            verify(name, width, height)
            embedded = bpy.data.texts.new(Path(__file__).name)
            embedded.write(Path(__file__).read_text())
            bpy.context.preferences.filepaths.save_version = 0
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path))
        verify(name, width, height)
        if not args.verify_only:
            bpy.context.scene.render.filepath = str(destination / f"{name}.png")
            bpy.ops.render.render(write_still=True)
        image = bpy.data.images.load(str(destination / f"{name}.png"), check_existing=True)
        assert tuple(image.size) == (width * SUPERSAMPLE, height * SUPERSAMPLE)
        assert image.channels == 4
        print(f"UI_BLEND={path}", flush=True)
    print(f"UI_BUTTONS={destination}", flush=True)


if __name__ == "__main__":
    main()
