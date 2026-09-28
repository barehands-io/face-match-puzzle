"""Render the GBAM launch pair as flat painted illustrations, not 3D portraits.

Blender --background --factory-startup --python this_file.py -- --character all
Use --verify-only to check saved flat scenes. Historical 3D outputs are untouched.
"""

import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import create_character as art


ROOT = HERE.parents[2]
KIT = ROOT / "art/gbam_kit"
REFERENCE = KIT / "01_REFERENCE_IMAGES/OWN_STYLE_PRIMARY/gbam_flat_style_reference_sheet.png"
PALETTE = dict(line.split() for line in
               (KIT / "07_MATERIALS/palette.hex.txt").read_text().splitlines() if line.strip())
CHARACTERS = {
    "boy": ("CHR_M_001_COILS_YELLOW", "SKIN_WARM_MEDIUM", "YELLOW"),
    "girl": ("CHR_F_001_PUFFS_OVERALLS", "SKIN_WARM_BROWN", "CORAL"),
}
BASE = "01 - Head ears neck"
CHEEKS = "02 - Flat cheek blush"
OUTFIT = "03 - Fixed portrait outfit"


def piece(name, identifier):
    group = art.collection(name)
    group["piece_id"] = identifier
    group["draggable"] = True
    return name


def paint(key, grain=0.18, hex_color=None):
    mat = art.pigment("PAINT_" + key, (hex_color or PALETTE[key]).lstrip("#"),
                      grain=grain, emission_mix=1.0)
    # Fully emission-driven pigment: grain, but no lighting gradients or specular.
    nodes = mat.node_tree.nodes
    output = next(node for node in nodes if node.type == "OUTPUT_MATERIAL")
    emission = next(node for node in nodes if node.type == "EMISSION")
    mat.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    for node in list(nodes):
        if node.type in ("MIX_SHADER", "BSDF_DIFFUSE"):
            nodes.remove(node)
    next(node for node in nodes if node.type == "TEX_NOISE").inputs["Scale"].default_value = 110
    return mat


def outlined(name, path, mat, z, group, ink, center, expansion=1.025):
    edge = art.shape(name + " - dark painted edge", path, ink, z, group, thickness=0.005)
    pivot = Vector(art.position(*center))
    for spline in edge.data.splines:
        for control in spline.bezier_points:
            control.co = pivot + (control.co - pivot) * expansion
            control.handle_left = pivot + (control.handle_left - pivot) * expansion
            control.handle_right = pivot + (control.handle_right - pivot) * expansion
    return art.shape(name, path, mat, z + 0.012, group, thickness=0.005)


def curl(name, x, y, radius, mat, z, group):
    art.brush(name, (x - radius, y + radius * 0.25),
              [((x - radius * 1.2, y - radius), (x + radius, y - radius),
                (x + radius * 0.8, y + radius * 0.2)),
               ((x + radius * 0.6, y + radius * 0.8), (x, y + radius * 0.7),
                (x, y + radius * 0.2))],
              7, mat, z, group, roughness=1.4)


def build_base(character, m):
    outlined("Warm brown neck",
             """M 637 1165 C 695 1191 808 1197 867 1174
             L 891 1458 C 833 1520 666 1507 616 1440 Z""",
             m["skin"], 0.02, BASE, m["ink"], (751, 1330))
    art.shape("Neck - single painted shadow",
              """M 638 1205 C 695 1260 805 1281 872 1225
              L 879 1309 C 804 1370 711 1361 632 1327 Z""",
              m["shade"], 0.04, BASE, thickness=0.003)
    for side, x, y in (("L", 370, 863), ("R", 1136, 850)):
        art.oval("Ear " + side + " outline", x, y, 92, 113, m["ink"], 0.05, BASE, organic=0.025)
        art.oval("Ear " + side, x, y, 84, 104, m["skin"], 0.07, BASE, organic=0.025)
        sign = -1 if side == "L" else 1
        art.brush("Ear " + side + " painted C", (x + sign * 24, y + 52),
                  [((x + sign * 67, y + 7), (x + sign * 34, y - 71), (x - sign * 24, y - 38))],
                  23, m["shade"], 0.09, BASE, roughness=1.4)
    head = outlined("Shared rounded face",
                     """M 448 491 C 566 428 909 420 1034 490
                     C 1120 536 1140 691 1125 891
                     C 1113 1097 1015 1227 809 1280
                     C 706 1314 506 1228 430 1105
                     C 370 1008 369 849 379 704
                     C 382 608 399 531 448 491 Z""",
                     m["skin"], 0.12, BASE, m["ink"], (750, 850), expansion=1.018)
    for side, x, y in (("L", 484, 985), ("R", 1030, 969)):
        art.oval("Flat coral cheek " + side, x, y, 68, 61, m["CHEEK_CORAL"],
                 0.15, CHEEKS, organic=0.025, thickness=0.003)
    # Short, low-contrast pigment marks give a painted surface without sculpted shading.
    for i in range(55):
        x = art.RNG.uniform(459, 1038)
        y = art.RNG.uniform(545, 1110)
        art.brush(f"Skin dry brush {i:02d}", (x, y),
                  [((x + 4, y + 2), (x + 10, y - 1), (x + 18, y + 3))],
                  art.RNG.uniform(1, 3), m["skin_grain"], 0.141, BASE, roughness=1.5)
    if character == "boy":
        outlined("Yellow hoodie shoulders",
                 """M 638 1355 C 466 1369 376 1435 298 1614
                 L 1240 1614 C 1181 1435 1040 1362 869 1351
                 C 813 1412 699 1415 638 1355 Z""",
                 m["YELLOW"], 0.18, OUTFIT, m["ink"], (751, 1480))
        outlined("Hood - flat cream lining",
                 """M 641 1353 C 571 1327 494 1359 493 1400
                 C 501 1463 625 1493 748 1495
                 C 878 1497 1001 1459 1017 1403
                 C 1014 1355 933 1321 871 1347
                 C 880 1417 643 1420 641 1353 Z""",
                 m["CREAM"], 0.205, OUTFIT, m["ink"], (751, 1414))
        for x in (662, 846):
            art.brush("Hood drawstring " + str(x), (x, 1470),
                      [((x - 3, 1510), (x + 4, 1560), (x - 1, 1590))],
                      12, m["CREAM"], 0.235, OUTFIT, taper=False)
    else:
        outlined("Coral shirt shoulders",
                 """M 636 1355 C 454 1359 377 1430 305 1610
                 L 1215 1610 C 1165 1439 1039 1363 871 1351
                 C 824 1408 704 1419 636 1355 Z""",
                 m["CORAL"], 0.18, OUTFIT, m["ink"], (751, 1480))
        outlined("Green overall bib",
                 "M 524 1467 L 987 1467 L 1010 1610 L 507 1610 Z",
                 m["OLIVE"], 0.20, OUTFIT, m["ink"], (751, 1550))
        for side, x in (("L", 548), ("R", 944)):
            outlined("Overall strap " + side,
                     f"M {x - 28} 1368 L {x + 22} 1380 L {x + 12} 1545 L {x - 41} 1542 Z",
                     m["OLIVE"], 0.22, OUTFIT, m["ink"], (x, 1460))
            art.oval("Overall button " + side, x - 12, 1522, 23, 23,
                     m["YELLOW"], 0.245, OUTFIT, thickness=0.003)
    return head


def build_face(m):
    for side, x, y in (("L", 592, 817), ("R", 916, 800)):
        group = piece("10 - Eye " + side, "eye_" + side.lower())
        path = f"""M {x - 107} {y + 48}
            C {x - 133} {y - 65} {x - 63} {y - 131} {x + 12} {y - 116}
            C {x + 79} {y - 108} {x + 117} {y - 37} {x + 102} {y + 49}
            C {x + 30} {y + 40} {x - 31} {y + 38} {x - 107} {y + 48} Z"""
        outlined("Flat almond eye " + side, path, m["EYE_WHITE"], 0.20, group,
                 m["ink"], (x, y - 25), expansion=1.047)
        art.oval("Single dark pupil " + side, x + 29, y - 16, 49, 62,
                 m["ink"], 0.224, group, organic=0.013, thickness=0.003)
        brow = piece("11 - Brow " + side, "brow_" + side.lower())
        art.shape("Painted eyebrow " + side,
                  f"""M {x - 99} {y - 180} C {x - 61} {y - 208} {x + 33} {y - 226} {x + 71} {y - 193}
                  L {x + 78} {y - 161} C {x + 10} {y - 180} {x - 52} {y - 160} {x - 100} {y - 154} Z""",
                  m["ink"], 0.21, brow, thickness=0.003)
    nose = piece("12 - Nose", "nose")
    art.shape("Rounded flat nose",
              """M 751 817 C 776 859 778 907 752 944
              C 727 978 692 993 715 1020
              C 752 1057 840 1026 851 991
              C 859 964 831 942 810 929
              C 789 914 781 851 751 817 Z""",
              m["skin"], 0.235, nose, thickness=0.004)
    art.brush("Nose - curved dark contour", (750, 816),
              [((792, 901), (741, 950), (714, 979)),
               ((677, 1028), (787, 1051), (846, 1000))],
              12, m["shade"], 0.25, nose, roughness=1.1)
    art.brush("Nose - one ochre paint stroke", (758, 918),
              [((748, 950), (718, 977), (736, 1007))],
              21, m["nose_light"], 0.253, nose, roughness=1.7)
    mouth = piece("13 - Mouth", "mouth")
    outlined("Wide open smile",
             """M 626 1100 C 695 1078 849 1078 924 1062
             C 951 1099 899 1183 821 1206
             C 741 1230 648 1179 626 1100 Z""",
             m["MOUTH_DARK"], 0.21, mouth, m["shade"], (778, 1137), expansion=1.07)
    art.shape("Single ivory teeth block",
              """M 644 1104 C 725 1092 839 1093 908 1079
              C 910 1100 903 1114 889 1123
              C 825 1140 717 1143 662 1129 Z""",
              m["EYE_WHITE"], 0.236, mouth, thickness=0.003)
    for x in (699, 753, 811, 867):
        art.brush("Tooth division " + str(x), (x, 1101),
                  [((x, 1110), (x + 1, 1123), (x + 2, 1134))],
                  3, m["shade"], 0.244, mouth, taper=False, roughness=0.25)
    art.shape("Flat warm tongue",
              """M 735 1180 C 764 1149 817 1155 850 1179
              C 814 1204 771 1205 735 1180 Z""",
              m["CHEEK_CORAL"], 0.239, mouth, thickness=0.003)


def hair_mass(name, cx, cy, rx, ry, group, m):
    state = art.RNG.getstate()
    art.oval(name + " dark outline", cx, cy, rx + 7, ry + 7,
             m["ink"], 0.27, group, organic=0.05)
    art.RNG.setstate(state)
    art.oval(name + " flat mass", cx, cy, rx, ry,
             m["hair"], 0.285, group, organic=0.05)
    for i in range(65):
        angle = art.RNG.uniform(0, math.tau)
        radius = math.sqrt(art.RNG.uniform(0.02, 0.82))
        x, y = cx + rx * radius * math.cos(angle), cy + ry * radius * math.sin(angle)
        curl(f"{name} painted coil {i:02d}", x, y, art.RNG.uniform(9, 18),
             m["ink"] if i % 3 else m["hair_stroke"], 0.31, group)


def build_hair(character, m):
    if character == "boy":
        group = piece("20 - Short coiled hair", "hair_coils")
        path = """M 389 708 C 327 647 326 531 381 457
            C 375 395 428 321 509 315 C 559 235 650 245 714 265
            C 794 204 882 257 923 285 C 1023 253 1088 323 1100 383
            C 1181 420 1188 509 1159 555 C 1197 621 1143 687 1108 706
            C 1099 620 1070 546 1016 518 C 968 551 912 547 876 522
            C 814 571 757 555 716 527 C 646 578 578 549 541 545
            C 476 576 422 597 389 708 Z"""
        outlined("Short coils silhouette", path, m["hair"], 0.27, group,
                 m["ink"], (751, 451), expansion=1.025)
        # Hand-drawn curls stay inside the silhouette; no individually shaded balls.
        for row in range(6):
            for col in range(14):
                x = 425 + col * 47 + art.RNG.uniform(-9, 9)
                y = 351 + row * 29 + art.RNG.uniform(-8, 8)
                if row == 0 and (col < 2 or col > 11):
                    continue
                curl(f"Short painted curl {row}_{col}", x, y, art.RNG.uniform(12, 22),
                     m["ink"] if (row + col) % 3 else m["hair_stroke"], 0.305, group)
        for sign in (-1, 1):
            for i in range(10):
                curl(f"Temple curl {sign}_{i}", 751 + sign * (340 + i % 2 * 12),
                     522 + i * 12, 13, m["ink"], 0.307, group)
    else:
        cap = piece("20 - Swept hair cap", "hair_cap")
        outlined("Swept flat hair",
                 """M 380 718 C 324 559 410 365 577 333
                 C 661 312 722 341 754 368 C 811 327 901 310 972 352
                 C 1120 406 1191 550 1126 700
                 C 1082 590 1021 537 938 510
                 C 852 482 796 472 754 456
                 C 689 472 614 505 548 532 C 465 560 412 627 380 718 Z""",
                 m["hair"], 0.26, cap, m["ink"], (751, 480))
        for sign in (-1, 1):
            for i in range(8):
                art.brush(f"Swept hair paint {sign}_{i}", (754 + sign * (15 + i * 15), 370 + i * 3),
                          [((754 + sign * 130, 436), (754 + sign * (280 + i * 4), 453),
                            (754 + sign * (312 + i * 7), 598 + i * 6))],
                          6, m["hair_stroke"], 0.287, cap, roughness=2)
        for side, x, y in (("L", 393, 353), ("R", 1098, 343)):
            group = piece("21 - Puff and flower " + side, "hair_puff_" + side.lower())
            hair_mass("Puff " + side, x, y, 187, 181, group, m)
            fx = x + (87 if side == "L" else -87)
            fy = y + 111
            for petal in range(5):
                angle = math.tau * petal / 5
                art.oval(f"Flower {side} petal {petal}", fx + math.cos(angle) * 27,
                         fy + math.sin(angle) * 27, 19, 27,
                         m["PINK"], 0.34, group, organic=0.04, thickness=0.003)
            art.oval("Flower center " + side, fx, fy, 18, 18,
                     m["YELLOW"], 0.355, group, thickness=0.003)


def build(character):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    art.COLLECTIONS.clear()
    art.RNG.seed(96)
    identifier, skin_key, background_key = CHARACTERS[character]
    m = {key: paint(key) for key in ("EYE_WHITE", "MOUTH_DARK", "CHEEK_CORAL", "CREAM",
                                     "YELLOW", "CORAL", "OLIVE", "PINK")}
    m["skin"] = paint(skin_key, 0.24)
    m["ink"] = paint("HAIR_NEAR_BLACK", 0.26)
    m["shade"] = paint("SKIN_DEEP_BROWN", 0.20)
    m["hair"] = paint("HAIR_FILL", 0.30, "#352016")
    m["hair_stroke"] = paint("HAIR_STROKE", 0.32, "#573120")
    m["skin_grain"] = paint("SKIN_DRY_BRUSH", 0.30,
                             "#C16A38" if character == "boy" else "#A34E29")
    m["nose_light"] = paint("NOSE_PAINT", 0.20,
                            "#DB8544" if character == "boy" else "#BD6935")
    art.shape("Flat colour-block background", "M -5 -5 L 1510 -5 L 1510 1610 L -5 1610 Z",
              m[background_key], -0.25, "00 - Painted background")
    head = build_base(character, m)
    build_face(m)
    build_hair(character, m)
    scene = bpy.context.scene
    scene.name = identifier + "_FLAT"
    scene["character_id"] = identifier
    scene["art_style"] = "Flat painted illustration; no lighting, gradients or specular"
    scene["reference"] = str(REFERENCE.relative_to(ROOT))
    scene["piece_count"] = 7 if character == "boy" else 9
    scene["blank_base"] = "Hide every collection with draggable=True; keep base, cheeks and outfit."
    scene.camera = art.camera("CAMERA - flat front portrait", (0, 0, 18), (0, 0, 0), 8)
    image = bpy.data.images.load(str(REFERENCE))
    image.pack()
    reference = art.link_object("Packed owner flat reference", None, "90 - Reference")
    reference.empty_display_type = "IMAGE"
    reference.data = image
    art.collection("90 - Reference").hide_render = True
    art.collection("90 - Reference").hide_viewport = True
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8
    scene.render.resolution_x, scene.render.resolution_y = art.WIDTH, art.HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.filepath = str(ROOT / f"art/renders/gbam-{character}-portrait-flat.png")
    for script in (Path(__file__), HERE / "create_character.py"):
        bpy.data.texts.new(script.name).write(script.read_text())
    head.select_set(True)
    bpy.context.view_layer.objects.active = head
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
    scene["object_count"] = len(scene.objects)
    scene["collection_count"] = len(bpy.data.collections)
    return scene


def verify(character):
    scene = bpy.context.scene
    assert scene["character_id"] == CHARACTERS[character][0]
    assert len(scene.objects) == scene["object_count"]
    assert len(bpy.data.collections) == scene["collection_count"]
    assert not any(obj.type in ("MESH", "LIGHT") for obj in scene.objects)
    assert (scene.render.resolution_x, scene.render.resolution_y) == (1502, 1600)
    assert scene.camera.data.type == "ORTHO"
    assert scene.view_settings.view_transform == "Standard"
    pieces = [coll for coll in bpy.data.collections if coll.get("draggable")]
    expected = {"eye_l", "eye_r", "brow_l", "brow_r", "nose", "mouth"}
    expected |= {"hair_coils"} if character == "boy" else {"hair_cap", "hair_puff_l", "hair_puff_r"}
    assert {coll["piece_id"] for coll in pieces} == expected
    for coll in pieces:
        assert not coll.hide_render and len(coll.objects) > 0
        assert all(len(obj.users_collection) == 1 for obj in coll.objects)
    for mat in bpy.data.materials:
        if not mat.name.startswith("PAINT_"):
            continue
        nodes = mat.node_tree.nodes
        output = next(node for node in nodes if node.type == "OUTPUT_MATERIAL")
        assert output.inputs["Surface"].links[0].from_node.type == "EMISSION"
        assert not any(node.type.startswith("BSDF") for node in nodes)
    for side in ("L", "R"):
        coll = bpy.data.collections["10 - Eye " + side]
        assert len(coll.objects) == 3  # Outline, white, one pupil; no iris or glint.
    assert bpy.data.objects["Packed owner flat reference"].data.packed_file
    assert bpy.data.texts[Path(__file__).name].as_string() == Path(__file__).read_text()
    print(f"VERIFIED FLAT {character}: {len(pieces)} pieces; emission-only paint, no meshes/lights.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", choices=("boy", "girl", "all"), default="all")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    for character in CHARACTERS if args.character == "all" else (args.character,):
        path = ROOT / f"art/blender/gbam-{character}-portrait-flat.blend"
        if not args.verify_only:
            build(character)
            verify(character)
            bpy.context.preferences.filepaths.save_version = 0
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path))
        verify(character)
        if not args.verify_only:
            scene = bpy.context.scene
            bpy.ops.render.render(write_still=True)
            for coll in bpy.data.collections:
                if coll.get("draggable"):
                    coll.hide_render = True
            scene.render.filepath = str(ROOT / f"art/renders/gbam-{character}-blank-flat.png")
            bpy.ops.render.render(write_still=True)
        for kind in ("portrait", "blank"):
            image = bpy.data.images.load(str(ROOT / f"art/renders/gbam-{character}-{kind}-flat.png"))
            assert tuple(image.size) == (1502, 1600) and image.channels == 4


if __name__ == "__main__":
    main()
