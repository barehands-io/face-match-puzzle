"""Export aligned, transparent flat illustrations for the Godot prototype."""

from array import array
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[3]
CHARACTERS = {
    "boy": ("CHR_M_001_COILS_YELLOW", "Coils and sunshine"),
    "girl": ("CHR_F_001_PUFFS_OVERALLS", "Puffs and flowers"),
}


def render(scene, destination):
    scene.render.filepath = str(destination)
    bpy.ops.render.render(write_still=True)


def crop_piece(source, destination):
    image = bpy.data.images.load(str(source), check_existing=False)
    width, height = image.size
    pixels = array("f", [0]) * (width * height * 4)
    image.pixels.foreach_get(pixels)
    xs, ys = [], []
    for y in range(height):
        for x in range(width):
            if pixels[(y * width + x) * 4 + 3] > 0.01:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise ValueError(f"Empty exported piece: {source}")
    left, right = max(0, min(xs) - 2), min(width, max(xs) + 3)
    bottom, top = max(0, min(ys) - 2), min(height, max(ys) + 3)
    cropped = array("f")
    for y in range(bottom, top):
        cropped.extend(pixels[(y * width + left) * 4:(y * width + right) * 4])
    output = bpy.data.images.new("Cropped puzzle piece", right - left, top - bottom, alpha=True)
    output.pixels.foreach_set(cropped)
    output.filepath_raw = str(destination)
    output.file_format = "PNG"
    output.save()
    bpy.data.images.remove(output)
    bpy.data.images.remove(image)
    source.unlink()
    return left, height - top, right - left, top - bottom


def main():
    for short, (identifier, title) in CHARACTERS.items():
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/blender/gbam-{short}-portrait-flat.blend"))
        scene = bpy.context.scene
        output = ROOT / "game/assets/characters" / identifier
        output.mkdir(parents=True, exist_ok=True)
        groups = [group for group in bpy.data.collections if group.get("draggable")]
        scene.render.film_transparent = True
        render(scene, output / "example.png")
        for group in groups:
            group.hide_render = True
        render(scene, output / "base.png")
        for obj in scene.objects:
            if obj.type != "CAMERA":
                obj.hide_render = True
        pieces = []
        for group in groups:
            group.hide_render = False
            for obj in group.objects:
                obj.hide_render = False
            identifier_piece = group["piece_id"]
            temp = output / "_uncropped.png"
            render(scene, temp)
            x, y, width, height = crop_piece(temp, output / f"{identifier_piece}.png")
            pieces.append({
                "id": identifier_piece, "file": f"{identifier_piece}.png",
                "target_x": x + width / 2, "target_y": y + height / 2,
                "width": width, "height": height,
                "z_order": round(min(obj.location.z for obj in group.objects) * 1000),
            })
            for obj in group.objects:
                obj.hide_render = True
            group.hide_render = True
        manifest = {
            "id": identifier, "title": title, "canvas_width": 1502, "canvas_height": 1600,
            "base": "base.png", "example": "example.png", "snap_radius": 100,
            "pieces": sorted(pieces, key=lambda piece: (piece["z_order"], piece["id"])),
        }
        (output / "pieces.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"EXPORTED {identifier}: {len(pieces)} complete pieces", flush=True)


if __name__ == "__main__":
    main()
