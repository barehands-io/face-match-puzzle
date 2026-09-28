"""Build the toy-inspired clown as eight editable painted-paper features.

Run with Blender --background --factory-startup --python this_file.py.
Use --preview for a half-size draft or --no-render to only save the scene.
The adjacent create_character.py supplies the shared paper-art primitives.
"""

import argparse
import math
from pathlib import Path
import sys

import bpy


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import create_character as art


ROOT = SCRIPT_DIR.parent
WIDTH, HEIGHT = art.WIDTH, art.HEIGHT
PIECES = {
    "hat": "04 - Green bowler hat",
    "hair_left": "05 - Left orange hair tuft",
    "hair_right": "06 - Right orange hair tuft",
    "eye_round": "07 - Round eye",
    "eye_x": "08 - X eye",
    "nose": "09 - Red ball nose",
    "smile": "10 - White smile",
    "bow_tie": "11 - Polka dot bow tie",
}


def build():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for group in list(bpy.data.collections):
        bpy.data.collections.remove(group)
    art.COLLECTIONS.clear()
    art.RNG.seed(42)

    m = {
        "frame": art.pigment("Paper / warm worn border", "876B5D", 0.08),
        "paper": art.pigment("Paper / sage teal", "ACC5B5", 0.075),
        "halo": art.pigment("Charcoal / soft grey underpainting", "91988D", 0.12),
        "chalk": art.pigment("Charcoal / rubbed light marks", "ABB2A1", 0.08),
        "pencil": art.pigment("Charcoal / graphite", "70776D", 0.08),
        "pencil_light": art.pigment("Charcoal / graphite light", "939B89", 0.08),
        "shadow": art.pigment("Paint / warm cutout shadow", "705046"),
        "skin": art.pigment("Paint / peach face", "FF9875"),
        "ear": art.pigment("Paint / warm ear", "F68D69"),
        "red": art.pigment("Paint / red cheeks and nose", "FA4648", 0.08),
        "red_dark": art.pigment("Paint / red nose rim and smile", "BE3E35", 0.07),
        "red_light": art.pigment("Paint / coral nose highlight", "FF8070", 0.06),
        "hair": art.pigment("Paint / vermilion orange hair", "FA663D", 0.07),
        "hair_light": art.pigment("Paint / apricot hair streaks", "FFBD79", 0.08),
        "hair_ink": art.pigment("Paint / burnt sienna strands", "A94631", 0.12),
        "ivory": art.pigment("Paint / warm ivory", "FFF1DC", 0.025),
        "black": art.pigment("Paint / warm charcoal black", "302729", 0.025),
        "green": art.pigment("Paint / moss green bowler", "718E49", 0.065),
        "green_dark": art.pigment("Paint / deep green brim", "4B6741", 0.08),
        "yellow": art.pigment("Paint / golden hat trim", "F2CF65", 0.065),
        "pink": art.pigment("Paint / raspberry bow tie dots", "D8567F", 0.07),
        "pink_dark": art.pigment("Paint / shaded pink bow tie", "AC506B", 0.08),
        "pink_light": art.pigment("Paint / pale pink knot", "FFD6CC", 0.04),
    }
    paper = "00 - Paper and border"
    sketch = "01 - Charcoal sketch halo"
    base = "02 - Head ears and neck"
    cheeks = "03 - Red cheeks"

    art.shape("Board - rounded umber edge",
              "M -14 -16 L 1517 -16 L 1517 1620 L -14 1620 Z",
              m["frame"], -0.39, paper, thickness=0.11, bevel=0.018)
    art.shape("Sage teal paper - softly rounded corners",
              """M 67 30 C 330 14 1182 10 1427 18
              C 1455 20 1466 42 1466 73 L 1471 1509
              C 1472 1550 1453 1569 1415 1573
              C 1100 1590 356 1596 76 1607
              C 50 1607 35 1589 35 1558 L 19 86
              C 18 51 33 32 67 30 Z""",
              m["paper"], -0.29, paper, thickness=0.045, bevel=0.004)
    art.shape("Grey wash behind the clown",
              """M 740 279 C 468 272 282 386 199 566
              C 126 727 151 963 215 1110
              C 291 1283 456 1350 575 1400
              C 681 1446 861 1464 1017 1398
              C 1237 1306 1342 1125 1350 926
              C 1375 681 1271 453 1096 351
              C 999 295 867 268 740 279 Z""",
              m["halo"], -0.20, sketch, thickness=0.009)
    for i in range(15):
        points = []
        phase = art.RNG.uniform(0, math.tau)
        for j in range(330):
            angle = j / 330 * math.tau
            waviness = (5.5 * math.sin(11 * angle + phase)
                        + 3 * math.cos(27 * angle + phase)
                        + 1.4 * math.sin(73 * angle + i))
            rx = 578 + (i - 7) * 2.2 + waviness
            ry = 557 + (i - 7) * 2.3 + waviness
            points.append((751 + rx * math.cos(angle) + 15 * math.sin(2 * angle),
                           857 + ry * math.sin(angle) + 11 * math.cos(3 * angle)))
        art.pencil(f"Loose charcoal contour {i + 1:02d}", points,
                   m["pencil" if i % 3 == 0 else "pencil_light"],
                   -0.184 + i * 0.0006, sketch,
                   width=art.RNG.uniform(0.6, 1.8), cyclic=True)
    for i in range(9):
        art.brush(f"Rubbed charcoal lower arc {i + 1:02d}",
                  (261 + i * 11, 1180 + i * 9),
                  [((382, 1347 + i * 3), (539, 1412 + i * 4),
                    (659, 1410 + i * 2))],
                  art.RNG.uniform(2, 5), m["chalk"], -0.155, sketch, roughness=3.5)
    for i in range(6):
        art.brush(f"Charcoal right sweep {i + 1:02d}",
                  (1130 + i * 8, 1280 - i * 5),
                  [((1299, 1150), (1340 + i * 2, 1050), (1325 + i * 2, 873))],
                  art.RNG.uniform(1, 3), m["pencil"], -0.154, sketch, roughness=3)

    head_path = """M 462 475 C 554 423 928 420 1032 477
        C 1103 516 1135 618 1136 765
        L 1145 984 C 1148 1100 1093 1151 988 1199
        C 912 1232 845 1271 821 1333
        C 810 1363 813 1401 789 1420
        C 771 1436 731 1436 709 1421
        C 686 1405 692 1366 678 1335
        C 654 1279 600 1245 517 1210
        C 403 1162 355 1117 355 1013
        L 357 771 C 357 621 389 520 462 475 Z"""
    shadow = art.shape("Offset head and neck silhouette", head_path,
                       m["shadow"], 0.035, base, thickness=0.021)
    shadow.location.x += 5 / art.SCALE
    shadow.location.y -= 11 / art.SCALE
    for side, x in (("Left", 343), ("Right", 1156)):
        art.oval(f"{side} ear - umber edge", x, 899, 77, 86,
                 m["shadow"], 0.045, base, organic=0.025)
        art.oval(f"{side} peach ear", x, 893, 66, 74,
                 m["ear"], 0.075, base, organic=0.022)
        art.oval(f"{side} red inner ear", x, 895, 36, 42,
                 m["red"], 0.096, base, organic=0.04, thickness=0.004)
    head = art.shape("Peach head and tapered neck", head_path,
                     m["skin"], 0.14, base, thickness=0.048, bevel=0.002)
    for side, x, y in (("Left", 514, 1010), ("Right", 991, 998)):
        art.oval(f"{side} painted red cheek", x, y, 64, 61,
                 m["red"], 0.173, cheeks, organic=0.024, thickness=0.004)

    hair_path = """M 401 722 C 345 706 265 667 230 626
        C 216 608 204 582 214 578
        C 224 574 240 581 253 585
        C 224 551 217 524 231 522
        C 242 520 255 529 266 533
        C 249 503 240 470 255 467
        C 269 465 292 486 311 498
        C 294 459 288 428 306 430
        C 326 434 343 458 367 478
        C 355 443 349 407 365 410
        C 388 416 407 449 425 472
        C 422 449 424 429 437 437
        C 470 457 485 508 490 545
        C 455 597 426 658 401 722 Z"""
    for side, piece_id in (("Left", "hair_left"), ("Right", "hair_right")):
        group = PIECES[piece_id]
        art.shape(f"{side} tuft - orange cut paper", hair_path,
                  m["hair"], 0.20, group, thickness=0.032, bevel=0.002)
        strokes = (
            ((232, 592), ((272, 609), (327, 644), (373, 678))),
            ((246, 543), ((287, 566), (341, 611), (390, 652))),
            ((275, 496), ((310, 523), (357, 574), (403, 623))),
            ((314, 457), ((348, 488), (389, 546), (418, 597))),
            ((371, 444), ((394, 476), (419, 519), (438, 559))),
        )
        for i, (start, segment) in enumerate(strokes, 1):
            art.brush(f"{side} tuft - sienna stroke {i}", start, [segment],
                      10, m["hair_ink"], 0.224, group, roughness=0.8)
            art.brush(f"{side} tuft - apricot streak {i}",
                      (start[0] + 8, start[1] - 3),
                      [tuple((x + 8, y - 3) for x, y in segment)],
                      6, m["hair_light"], 0.23, group, roughness=0.65)
        if side == "Right":
            for obj in art.collection(group).objects:
                obj.scale.x = -1
                obj.location.y += 8 / art.SCALE

    hat = PIECES["hat"]
    art.shape("Bowler - green dome",
              """M 602 411 C 595 358 600 288 636 234
              C 668 185 723 169 772 181
              C 850 195 884 266 887 335
              L 891 406 C 808 443 676 451 602 411 Z""",
              m["green"], 0.249, hat, thickness=0.031)
    art.shape("Bowler - golden painted patch",
              """M 635 248 C 650 220 681 207 701 218
              C 717 231 706 265 687 286
              C 668 309 641 320 630 304
              C 619 291 625 266 635 248 Z""",
              m["yellow"], 0.271, hat, thickness=0.004)
    art.shape("Bowler - charcoal ribbon",
              """M 600 351 C 676 369 804 367 885 345
              L 889 397 C 805 426 677 429 602 405 Z""",
              m["black"], 0.278, hat, thickness=0.008)
    art.brush("Bowler - ribbon dry edge", (623, 389),
              [((691, 405), (806, 397), (868, 379))],
              4, m["shadow"], 0.288, hat, roughness=1.2)
    art.shape("Bowler - green brim silhouette",
              """M 544 394 C 548 375 566 378 587 398
              C 650 451 841 448 909 396
              C 932 377 956 380 957 402
              C 963 451 916 473 846 482
              C 744 496 610 483 563 455
              C 546 445 537 416 544 394 Z""",
              m["green_dark"], 0.294, hat, thickness=0.026)
    art.shape("Bowler - golden upturned brim",
              """M 545 389 C 552 371 569 382 589 401
              C 650 452 842 447 910 395
              C 933 376 952 378 953 397
              C 954 430 913 453 845 463
              C 742 479 616 466 570 443
              C 550 433 538 407 545 389 Z""",
              m["yellow"], 0.311, hat, thickness=0.011)

    eye = PIECES["eye_round"]
    art.oval("Round eye - ivory white", 601, 783, 99, 109,
             m["ivory"], 0.201, eye, organic=0.018, thickness=0.018)
    art.oval("Round eye - vertical black pupil", 603, 783, 29, 77,
             m["black"], 0.219, eye, organic=0.028, thickness=0.008)
    eye = PIECES["eye_x"]
    art.oval("X eye - ivory white", 895, 777, 99, 104,
             m["ivory"], 0.201, eye, organic=0.021, thickness=0.018)
    art.shape("X eye - single charcoal cross",
              """M 831 720 C 845 717 877 740 895 750
              C 918 733 945 709 956 717
              C 966 727 942 759 924 779
              C 943 799 965 829 953 837
              C 942 845 912 821 894 807
              C 875 824 845 850 835 839
              C 824 829 847 799 864 780
              C 846 759 821 729 831 720 Z""",
              m["black"], 0.22, eye, thickness=0.008)

    nose = PIECES["nose"]
    art.oval("Ball nose - dark red rim", 753, 933, 103, 102,
             m["red_dark"], 0.236, nose, organic=0.018, thickness=0.019)
    art.oval("Ball nose - vermilion center", 750, 929, 94, 94,
             m["red"], 0.253, nose, organic=0.018, thickness=0.015)
    art.brush("Ball nose - soft painted glint", (689, 912),
              [((689, 884), (710, 867), (737, 867))],
              14, m["red_light"], 0.267, nose, roughness=0.5)
    art.brush("Ball nose - lower crescent", (734, 1010),
              [((772, 1023), (823, 993), (835, 961))],
              6, m["red_dark"], 0.267, nose, roughness=0.45)

    smile = PIECES["smile"]
    art.shape("Smile - ivory painted cutout",
              """M 549 1025 C 578 1005 611 1010 644 1031
              C 700 1063 801 1066 858 1030
              C 888 1009 924 1000 950 1023
              C 988 1056 962 1120 922 1153
              C 874 1194 807 1214 742 1212
              C 663 1210 597 1185 555 1146
              C 516 1110 512 1051 549 1025 Z""",
              m["ivory"], 0.204, smile, thickness=0.021)
    art.brush("Smile - sweeping red line", (568, 1070),
              [((588, 1120), (650, 1154), (741, 1155)),
               ((826, 1160), (901, 1126), (923, 1057))],
              15, m["red_dark"], 0.222, smile, taper=False, roughness=0.55)
    art.brush("Smile - vermilion dry brush", (581, 1085),
              [((618, 1131), (677, 1144), (724, 1146))],
              4, m["red"], 0.226, smile, roughness=0.85)

    bow = PIECES["bow_tie"]
    left_bow = """M 718 1383 C 672 1360 610 1329 553 1335
        C 510 1340 507 1386 513 1431
        C 519 1487 544 1511 590 1500
        C 642 1487 681 1462 722 1458 Z"""
    right_bow = """M 781 1381 C 830 1355 889 1328 942 1335
        C 981 1341 991 1383 985 1430
        C 979 1481 958 1504 913 1494
        C 866 1484 822 1459 780 1455 Z"""
    for side, path in (("Left", left_bow), ("Right", right_bow)):
        art.shape(f"Bow tie - {side.lower()} pink backing", path,
                  m["pink_dark"], 0.192, bow, thickness=0.022)
        wing = art.shape(f"Bow tie - {side.lower()} ivory wing", path,
                         m["ivory"], 0.215, bow, thickness=0.013)
        wing.location.y += 13 / art.SCALE
    for i, (x, y, radius) in enumerate((
            (552, 1358, 18), (609, 1381, 22), (662, 1407, 16),
            (541, 1420, 20), (593, 1454, 22), (651, 1443, 17),
            (838, 1391, 17), (895, 1363, 22), (946, 1387, 18),
            (848, 1441, 20), (906, 1454, 22), (959, 1437, 15)), 1):
        art.oval(f"Bow tie - raspberry polka dot {i:02d}", x, y, radius, radius,
                 m["pink"], 0.23, bow, organic=0.035, thickness=0.003)
    art.shape("Bow tie - rounded center knot",
              """M 718 1369 C 735 1359 764 1360 782 1370
              C 798 1391 798 1440 785 1463
              C 770 1479 736 1479 717 1467
              C 702 1446 703 1391 718 1369 Z""",
              m["pink_light"], 0.249, bow, thickness=0.022)
    art.oval("Bow tie - knot upper dot", 738, 1393, 16, 17,
             m["pink"], 0.266, bow, organic=0.025, thickness=0.003)
    art.oval("Bow tie - knot lower dot", 761, 1441, 17, 16,
             m["pink"], 0.266, bow, organic=0.025, thickness=0.003)

    for piece_id, group_name in PIECES.items():
        group = art.collection(group_name)
        group["piece_id"] = piece_id
        group["draggable"] = True
    for group_name in (paper, sketch, base, cheeks):
        art.collection(group_name)["draggable"] = False

    reference_path = ROOT.parent / "reference" / "gameplay-concept-clown-box.png"
    if not reference_path.is_file():
        raise FileNotFoundError(f"Required reference image is missing: {reference_path}")
    reference = bpy.data.images.load(str(reference_path), check_existing=True)
    reference.pack()
    reference_obj = art.link_object("Toy box reference - packed into blend", None,
                                    "90 - Original reference (hidden)")
    reference_obj.empty_display_type = "IMAGE"
    reference_obj.data = reference
    reference_obj.empty_display_size = 8
    reference_obj.location = (-10, 0, 0)
    reference_obj.hide_render = True
    art.collection("90 - Original reference (hidden)").hide_viewport = True
    art.collection("90 - Original reference (hidden)").hide_render = True

    scene = bpy.context.scene
    scene.name = "Clown - layered paper portrait"
    scene["Artwork type"] = "Editable 2.5D painted-paper relief"
    scene["Reference"] = "User-supplied toy box reference, packed into this file."
    scene["Editing"] = "Eight draggable collections; all decorations stay with their feature."
    scene["Blank base"] = "00 + 01 + 02 + 03: paper, halo, peach head, ears, neck, red cheeks."
    scene["Camera usage"] = "Front portrait for aligned exports; angled camera for paper relief."
    front = art.camera("CAMERA - front portrait", (0, 0, 18), (0, 0, 0), 8.0)
    art.camera("CAMERA - angled paper relief", (8, -4, 13), (0, 0, 0), 9.4)
    art.light("Large softbox - upper left", (-3.5, 4.5, 8), 350, 5.0)
    art.light("Soft fill - right", (4, -0.5, 7), 100, 5.0)
    scene.camera = front
    world = bpy.data.worlds.new("Neutral studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.use_file_extension = True
    scene.render.fps = 24

    bpy.context.view_layer.objects.active = head
    head.select_set(True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                space.region_3d.view_perspective = "CAMERA"
                space.region_3d.view_camera_zoom = 0
                space.shading.type = "MATERIAL"
                space.overlay.show_overlays = False
                space.clip_end = 100
    for script in (Path(__file__), SCRIPT_DIR / "create_character.py"):
        bpy.data.texts.new(script.name).write(script.read_text())
    bpy.data.texts.new("ABOUT THE ARTWORK").write(
        "CLOWN - LAYERED PAPER PORTRAIT\n\n"
        "Eight features, each in one collection: bowler hat, left tuft, right\n"
        "tuft, round eye, X eye, red nose, white smile, polka-dot bow tie.\n"
        "Hide collections 04 through 11 for the blank face. Do not separate\n"
        "pupils, ribbon, smile line or dots from their owning collection.\n\n"
        "Front camera: 1502 x 1600. All features share that framing for export.\n"
        "Large silhouettes retain editable Bezier handles. Pigment materials\n"
        "and tapered brush strokes use the same helpers as the redhead girl.\n"
        "The reference and both Python sources are packed into this file.\n"
        "To regenerate, save both scripts together and run create_clown.py\n"
        "from art/blender/scripts/ in the repository.\n"
    )
    return scene


def main():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args(arguments)
    scene = build()
    destination = ROOT.parent / "renders" / "clown-portrait.png"
    scene.render.filepath = str(destination)
    bpy.context.preferences.filepaths.save_version = 0
    blend_path = ROOT / "clown-portrait.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    if args.preview:
        scene.render.resolution_percentage = 50
        scene.cycles.samples = 24
        destination = ROOT.parent / "renders" / "clown-preview.png"
        scene.render.filepath = str(destination)
    if not args.no_render:
        bpy.ops.render.render(write_still=True)
    print(f"ARTWORK_BLEND={blend_path}", flush=True)
    print(f"ARTWORK_RENDER={destination}", flush=True)
    print(f"ARTWORK_OBJECTS={len(bpy.data.objects)}", flush=True)
    print(f"ARTWORK_COLLECTIONS={len(bpy.data.collections)}", flush=True)


if __name__ == "__main__":
    main()
