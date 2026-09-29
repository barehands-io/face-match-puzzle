"""Separate flat-painted braided-boy review; never overwrites launch artwork.

Blender --background --factory-startup --python this_file.py
"""

import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import create_character as art
import create_gbam_character as flat

ROOT = HERE.parents[2]
STEM = "gbam-braided-boy-review-flat"
REFERENCE = flat.KIT / "01_REFERENCE_IMAGES/OWN_STYLE_PRIMARY/braided_male_primary.png"


def braid(name, start, segments, width, z, group, m):
    art.brush(name + " dark ribbon", start, segments, width, m["ink"],
              z, group, taper=False, roughness=1.5)
    centers = art.cubic_points(start, segments, steps=100)
    distance = 0
    index = 0
    for i in range(1, len(centers) - 1):
        distance += (centers[i] - centers[i - 1]).length
        if distance < width * 0.45:
            continue
        distance = 0
        center = centers[i]
        tangent = (centers[i + 1] - centers[i - 1]).normalized()
        normal = Vector((-tangent.y, tangent.x))
        sign = 1 if index % 2 else -1
        tip = center + tangent * width * 0.52
        left = center - tangent * width * 0.39 + normal * width * 0.46 * sign
        middle = center + normal * width * 0.18 * sign
        right = center - normal * width * 0.30 * sign
        back = center - tangent * width * 0.39
        upper = middle + tangent * width * 0.22
        def xy(point):
            return f"{point.x:.3f} {point.y:.3f}"
        art.shape(f"{name} alternating plait {index:02d}",
                  f"M {xy(left)} C {xy(left + normal * sign * width * 0.12)} "
                  f"{xy(upper)} {xy(tip)} C {xy(right + tangent * width * 0.35)} "
                  f"{xy(right)} {xy(back)} C {xy(back - tangent * width * 0.12)} "
                  f"{xy(left - tangent * width * 0.1)} {xy(left)} Z",
                  m["hair_stroke"] if index % 3 == 0 else m["hair"],
                  z + 0.015, group, thickness=0.003)
        index += 1


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    art.COLLECTIONS.clear()
    art.RNG.seed(103)
    m = {key: flat.paint(key, 0.23) for key in
         ("EYE_WHITE", "MOUTH_DARK", "CHEEK_CORAL", "CREAM", "OLIVE", "MINT")}
    m.update({
        "skin": flat.paint("SKIN_WARM_BROWN", 0.28),
        "ink": flat.paint("HAIR_NEAR_BLACK", 0.27),
        "shade": flat.paint("SKIN_DEEP_BROWN", 0.25),
        "hair": flat.paint("BRAID_FILL", 0.35, "#352017"),
        "hair_stroke": flat.paint("BRAID_STROKE", 0.40, "#4B2B1D"),
        "skin_grain": flat.paint("SKIN_GRAIN", 0.30, "#A34E29"),
        "nose_light": flat.paint("NOSE_OCHRE", 0.26, "#CB7D41"),
    })
    m["YELLOW"] = m["OLIVE"]
    art.shape("Mint painted panel", "M -5 -5 L 1510 -5 L 1510 1610 L -5 1610 Z",
              m["MINT"], -0.25, "00 - Mint background")
    head = flat.build_base("boy", m)
    # Replace only the freshly generated review outfit with the reference's open hood.
    for obj in list(art.collection(flat.OUTFIT).objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    flat.outlined("Olive hoodie shoulders",
                  """M 613 1341 C 464 1344 275 1432 176 1610
                  L 1339 1610 C 1223 1440 1056 1351 875 1340
                  C 810 1400 696 1401 613 1341 Z""",
                  m["OLIVE"], 0.17, flat.OUTFIT, m["ink"], (751, 1460))
    art.shape("Dark shirt in open hoodie",
              """M 622 1357 C 699 1422 799 1418 879 1358
              L 1059 1464 L 943 1610 L 554 1610 L 439 1459 Z""",
              m["ink"], 0.19, flat.OUTFIT)
    art.shape("Cream hood lining",
              """M 635 1316 C 498 1288 328 1337 304 1411
              C 329 1480 477 1532 582 1606 L 664 1606
              C 606 1495 561 1444 497 1409
              C 540 1398 584 1390 628 1405 Z""",
              m["CREAM"], 0.22, flat.OUTFIT)
    art.shape("Cream hood right fold",
              """M 864 1320 C 1000 1288 1139 1333 1191 1418
              C 1090 1460 1039 1531 992 1608 L 898 1608
              C 932 1499 973 1443 1018 1400
              C 966 1386 915 1386 875 1405 Z""",
              m["CREAM"], 0.22, flat.OUTFIT)
    lining = flat.paint("HOOD_LINING_OCHRE", 0.25, "#D8B982")
    art.shape("Left lining flat shadow",
              "M 335 1394 C 409 1337 523 1324 623 1336 L 626 1390 C 511 1364 456 1396 423 1430 Z",
              lining, 0.235, flat.OUTFIT)
    art.shape("Right lining flat shadow",
              "M 879 1339 C 993 1321 1109 1354 1158 1405 L 1052 1449 C 1014 1399 937 1376 883 1394 Z",
              lining, 0.235, flat.OUTFIT)
    for x in (554, 991):
        art.oval("Dark drawstring eyelet " + str(x), x, 1516, 15, 15,
                 m["ink"], 0.25, flat.OUTFIT)
        art.brush("Drawstring " + str(x), (x, 1516),
                  [((x + 3, 1543), (x - 3, 1580), (x - 2, 1605))],
                  11, m["ink"], 0.255, flat.OUTFIT, taper=False)
    for sign in (-1, 1):
        for i in range(6):
            x = 340 + i * 27 if sign < 0 else 1130 + i * 19
            art.brush(f"Olive cloth brush {sign}_{i}", (x, 1498),
                      [((x + 8, 1527), (x + 23, 1568), (x + 28, 1596))],
                      9, lining if i == 0 else m["shade"], 0.181, flat.OUTFIT)

    flat.build_face(m)
    for side, x, y in (("L", 592, 816), ("R", 916, 800)):
        group = "10 - Eye " + side
        for obj in list(art.collection(group).objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        path = f"""M {x-99} {y+55} C {x-157} {y-19} {x-92} {y-128} {x-7} {y-123}
            C {x+79} {y-125} {x+132} {y-29} {x+99} {y+54}
            C {x+37} {y+39} {x-41} {y+39} {x-99} {y+55} Z"""
        flat.outlined("Rounded bright eye " + side, path, m["EYE_WHITE"], 0.20,
                      group, m["shade"], (x, y), expansion=1.022)
        art.oval("Flat dark pupil " + side, x + 4, y - 16, 53, 60,
                 m["ink"], 0.225, group, organic=0.014)
    for obj in list(art.collection("12 - Nose").objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    art.shape("Broad rounded nose - warm painted plane",
              """M 728 814 C 782 881 767 934 718 980
              C 687 1016 769 1061 847 1033
              C 883 1019 890 1004 868 980
              C 845 951 831 959 813 985
              C 796 1005 764 1011 739 1006
              C 796 949 791 878 728 814 Z""",
              m["nose_light"], 0.236, "12 - Nose")
    art.brush("Broad nose - dark hooked contour", (728, 814),
              [((784, 904), (739, 948), (708, 989)),
               ((679, 1033), (801, 1064), (869, 1016))],
              15, m["ink"], 0.252, "12 - Nose", roughness=1.3)
    art.shape("Nose - flat warm side accent",
              """M 750 1033 C 798 1015 816 1000 832 975
              C 847 953 867 976 876 996 C 851 1029 806 1047 750 1033 Z""",
              m["shade"], 0.249, "12 - Nose")

    scalp = flat.piece("20 - Geometric cornrow scalp", "hair_scalp")
    flat.outlined("Cornrow scalp silhouette",
                  """M 363 725 C 324 538 426 328 597 288
                  C 688 252 714 279 751 278 C 834 245 951 285 1030 355
                  C 1150 450 1184 597 1136 739
                  L 1049 571 C 957 512 850 487 752 492
                  C 609 481 479 558 414 633 Z""",
                  m["hair"], 0.27, scalp, m["ink"], (751, 470))
    art.brush("Center exposed scalp part", (751, 282),
              [((749, 346), (756, 425), (751, 496))],
              23, m["skin"], 0.295, scalp, taper=False, roughness=2.0)
    for side, sign in (("L", -1), ("R", 1)):
        for row in range(3):
            start = (751 + sign * 7, 343 + row * 69)
            end = (751 + sign * (263 + row * 30), 402 + row * 91)
            art.brush(f"Geometric scalp part {side}_{row}", start,
                      [((751 + sign * 90, 294 + row * 77),
                        (751 + sign * 208, 302 + row * 92), end)],
                      21, m["skin"], 0.295, scalp, taper=False, roughness=2.2)
        for row in range(4):
            start = (751 + sign * 25, 302 + row * 64)
            end = (751 + sign * (272 + row * 23), 372 + row * 91)
            braid(f"Scalp cornrow {side}_{row}", start,
                  [((751 + sign * 113, 252 + row * 74),
                    (751 + sign * 208, 294 + row * 77), end)],
                  37, 0.305, scalp, m)
        rear = flat.piece("21 - Rear hanging braids " + side, "braids_rear_" + side.lower())
        for i in range(4):
            x = 751 + sign * (287 + i * 36)
            end_y = 1216 + (i % 3) * 38 + (17 if sign > 0 else 0)
            braid(f"Rear plait {side}_{i}", (x, 532 + i * 11),
                  [((x + sign * 75, 768), (x + sign * 21, 1055),
                    (x + sign * (35 + i * 4), end_y))],
                  35 - i * 2, 0.10, rear, m)
        front = flat.piece("22 - Face framing braids " + side, "braids_front_" + side.lower())
        for i in range(2):
            x = 751 + sign * (267 + i * 83)
            end = (751 + sign * (333 + i * 142), 988 - i * 41 + (28 if sign < 0 else 0))
            braid(f"Front plait {side}_{i}", (x, 410 + i * 52),
                  [((x + sign * 64, 554), (end[0] - sign * 23, 804), end)],
                  39 - i * 3, 0.33, front, m)
            art.brush(f"Loose braid tip {side}_{i}", end,
                      [((end[0] + 7, end[1] + 12), (end[0] - 5, end[1] + 29),
                        (end[0] + 4, end[1] + 43))],
                      26, m["ink"], 0.348, front, taper=True, roughness=3)

    scene = bpy.context.scene
    scene.name = "GBAM braided boy - FLAT VISUAL REVIEW"
    scene["review_only"] = True
    scene["reference"] = str(REFERENCE.relative_to(ROOT))
    scene["blank_base"] = "Hide collections with draggable=True; ears, cheeks and hoodie stay."
    scene.camera = art.camera("CAMERA - flat front review", (0, 0, 18), (0, 0, 0), 8)
    reference = bpy.data.images.load(str(REFERENCE))
    reference.pack()
    obj = art.link_object("Packed braided boy reference", None, "90 - Reference")
    obj.empty_display_type = "IMAGE"
    obj.data = reference
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
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.filepath = str(ROOT / "art/renders" / f"{STEM}-portrait.png")
    for script in (Path(__file__), HERE / "create_gbam_character.py", HERE / "create_character.py"):
        bpy.data.texts.new(script.name).write(script.read_text())
    bpy.context.view_layer.objects.active = head
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                space.region_3d.view_perspective = "CAMERA"
                space.region_3d.view_camera_zoom = 0
                space.shading.type = "MATERIAL"
                space.overlay.show_overlays = False
    return scene


def verify():
    assert not any(obj.type in ("MESH", "LIGHT") for obj in bpy.context.scene.objects)
    pieces = [coll for coll in bpy.data.collections if coll.get("draggable")]
    assert len(pieces) == 11
    assert bpy.data.objects["Packed braided boy reference"].data.packed_file
    for coll in pieces:
        assert coll.objects and all(len(obj.users_collection) == 1 for obj in coll.objects)
    for mat in bpy.data.materials:
        if mat.name.startswith("PAINT_"):
            output = next(node for node in mat.node_tree.nodes if node.type == "OUTPUT_MATERIAL")
            assert output.inputs["Surface"].links[0].from_node.type == "EMISSION"
    print("VERIFIED: flat braided review, 11 grouped features, packed reference, no 3D lighting.", flush=True)


def main():
    scene = build()
    verify()
    path = ROOT / "art/blender" / f"{STEM}.blend"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path))
    verify()
    bpy.ops.render.render(write_still=True)
    for coll in bpy.data.collections:
        if coll.get("draggable"):
            coll.hide_render = True
    scene = bpy.context.scene
    scene.render.filepath = str(ROOT / "art/renders" / f"{STEM}-blank.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "art/blender" / f"{STEM}-blank.blend"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
