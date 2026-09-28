"""Build the reference-inspired, editable cut-paper portrait in Blender.

Run with Blender --background --factory-startup --python this_file.py -- --preview
Omit --preview for the full-size artwork. No external Python packages are needed.
"""

import argparse
import math
from pathlib import Path
import random
import re
import sys

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1502, 1600
SCALE = 200.0
RNG = random.Random(27)
COLLECTIONS = {}


def position(x, y, z=0.0):
    return ((x - WIDTH / 2) / SCALE, (HEIGHT / 2 - y) / SCALE, z)


def collection(name):
    if name not in COLLECTIONS:
        group = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(group)
        COLLECTIONS[name] = group
    return COLLECTIONS[name]


def link_object(name, data, group):
    obj = bpy.data.objects.new(name, data)
    collection(group).objects.link(obj)
    return obj


def linear_channel(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def color(hex_color):
    rgb = tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (*map(linear_channel, rgb), 1.0)


def pigment(name, hex_color, grain=0.035, emission_mix=0.78):
    mat = bpy.data.materials.new(name)
    rgba = color(hex_color)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (660, 0)
    mix = nodes.new("ShaderNodeMixShader")
    mix.location = (440, 0)
    mix.inputs[0].default_value = emission_mix
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.location = (180, 50)
    diffuse.inputs["Roughness"].default_value = 0.9
    emission = nodes.new("ShaderNodeEmission")
    emission.location = (180, -110)
    emission.inputs["Strength"].default_value = 1.0
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-450, 0)
    noise.inputs["Scale"].default_value = 190.0
    noise.inputs["Detail"].default_value = 2.4
    noise.inputs["Roughness"].default_value = 0.72
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-170, 0)
    for element, multiplier in zip(ramp.color_ramp.elements, (1 - grain, 1 + grain)):
        element.color = tuple(min(c * multiplier, 1.0) for c in rgba[:3]) + (1.0,)
    links = mat.node_tree.links
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], diffuse.inputs["Color"])
    links.new(ramp.outputs["Color"], emission.inputs["Color"])
    links.new(diffuse.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])
    return mat


def finish_curve(name, curve, mat, z, group, thickness=0.016, bevel=0.0012):
    curve.dimensions = "2D"
    curve.fill_mode = "BOTH"
    curve.resolution_u = 24
    curve.render_resolution_u = 32
    curve.extrude = thickness / 2
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    curve.materials.append(mat)
    obj = link_object(name, curve, group)
    obj.location.z = z
    obj["Artwork layer"] = group
    return obj


def shape(name, path, mat, z, group, thickness=0.016, bevel=0.0012):
    """Keep traced cubic outlines as editable Bezier handles, not baked meshes."""
    tokens = re.findall(r"[MLCZmlcz]|[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?", path)
    points = []
    index = 0
    closed = False

    def pair():
        nonlocal index
        result = (float(tokens[index]), float(tokens[index + 1]))
        index += 2
        return result

    def append(co, left=None):
        points.append({"co": co, "left": left or co, "right": co})

    while index < len(tokens):
        command = tokens[index]
        index += 1
        if command == "M":
            if points:
                raise ValueError(f"{name}: multiple subpaths are not supported")
            append(pair())
        elif command == "L":
            append(pair())
        elif command == "C":
            first, second, end = pair(), pair(), pair()
            points[-1]["right"] = first
            append(end, second)
        elif command == "Z":
            closed = True
        else:
            raise ValueError(f"{name}: unsupported path command {command!r}")
    if not closed or len(points) < 3:
        raise ValueError(f"{name}: a filled shape needs a closed outline")
    if points[-1]["co"] == points[0]["co"]:
        points[0]["left"] = points[-1]["left"]
        points.pop()
    curve = bpy.data.curves.new(name, "CURVE")
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    spline.use_cyclic_u = True
    for control, data in zip(spline.bezier_points, points):
        control.handle_left_type = "FREE"
        control.handle_right_type = "FREE"
        control.co = position(*data["co"])
        control.handle_left = position(*data["left"])
        control.handle_right = position(*data["right"])
    return finish_curve(name, curve, mat, z, group, thickness, bevel)


def polygon(name, points, mat, z, group, thickness=0.002):
    curve = bpy.data.curves.new(name, "CURVE")
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    spline.use_cyclic_u = True
    for control, (x, y) in zip(spline.points, points):
        control.co = (*position(x, y), 1.0)
    return finish_curve(name, curve, mat, z, group, thickness, bevel=0.00025)


def oval(name, cx, cy, rx, ry, mat, z, group, organic=0.0, thickness=0.012):
    count = 12
    phase = RNG.uniform(0, math.tau)
    curve = bpy.data.curves.new(name, "CURVE")
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(count - 1)
    spline.use_cyclic_u = True
    for i, control in enumerate(spline.bezier_points):
        angle = i / count * math.tau
        scale = 1 + organic * (math.sin(3 * angle + phase) + 0.4 * math.cos(5 * angle))
        control.co = position(cx + rx * scale * math.cos(angle),
                              cy + ry * scale * math.sin(angle))
        control.handle_left_type = "AUTO"
        control.handle_right_type = "AUTO"
    return finish_curve(name, curve, mat, z, group, thickness)


def cubic_points(start, segments, steps=38):
    result = []
    p0 = Vector(start)
    for first, second, end in segments:
        p1, p2, p3 = Vector(first), Vector(second), Vector(end)
        for step in range(steps):
            t = step / steps
            point = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
            point += 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
            result.append(point)
        p0 = p3
    result.append(p0)
    return result


def brush(name, start, segments, width, mat, z, group, taper=True, roughness=0.8):
    centers = cubic_points(start, segments)
    left, right = [], []
    phase = RNG.uniform(0, math.tau)
    for i, center in enumerate(centers):
        t = i / (len(centers) - 1)
        tangent = centers[min(i + 1, len(centers) - 1)] - centers[max(i - 1, 0)]
        if tangent.length < 1e-8:
            raise ValueError(f"{name}: degenerate brush tangent")
        normal = Vector((-tangent.y, tangent.x)).normalized()
        weight = 0.07 + 0.93 * math.sin(math.pi * t) ** 0.60 if taper else 1.0
        half_width = width * 0.5 * weight * (1 + 0.13 * math.sin(19 * t + phase))
        offset = roughness * (math.sin(t * 23 + phase) + 0.35 * math.sin(t * 61))
        center = center + normal * offset * math.sin(math.pi * t)
        left.append(tuple(center + normal * half_width))
        right.append(tuple(center - normal * half_width))
    return polygon(name, left + right[::-1], mat, z, group)


def pencil(name, points, mat, z, group, width=1.0, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = width / (2 * SCALE)
    curve.bevel_resolution = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    spline.use_cyclic_u = cyclic
    for control, (x, y) in zip(spline.points, points):
        control.co = (*position(x, y), 1.0)
    curve.materials.append(mat)
    obj = link_object(name, curve, group)
    obj.location.z = z
    return obj


def camera(name, location, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = scale
    data.lens = 50
    data.clip_end = 100
    obj = link_object(name, data, "80 - Cameras and softbox lights")
    obj.location = location
    forward = (Vector(target) - obj.location).normalized()
    right = forward.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(forward)
    obj.rotation_euler = Matrix((right, up, -forward)).transposed().to_euler()
    return obj


def light(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = link_object(name, data, "80 - Cameras and softbox lights")
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 0)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def build():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for group in list(bpy.data.collections):
        bpy.data.collections.remove(group)

    materials = {
        "frame": pigment("Paper / warm worn border", "876B5D", 0.08),
        "paper": pigment("Paper / muted sage green", "BBCBB2", 0.075),
        "halo": pigment("Charcoal / soft grey underpainting", "91988D", 0.12),
        "chalk": pigment("Charcoal / rubbed light marks", "ABB2A1", 0.08),
        "pencil": pigment("Charcoal / graphite", "70776D", 0.08),
        "pencil_light": pigment("Charcoal / graphite light", "939B89", 0.08),
        "shadow": pigment("Paint / warm cutout shadow", "705046"),
        "skin": pigment("Paint / peach face", "FF9875"),
        "ear": pigment("Paint / warm ear", "F68D69"),
        "hair": pigment("Paint / vermilion orange hair", "FA663D", 0.07),
        "hair_light": pigment("Paint / orange brush highlight", "FF8255", 0.08),
        "hair_ink": pigment("Paint / burnt sienna strands", "A94631", 0.12),
        "hair_ink_light": pigment("Paint / dry sienna strands", "BD5135", 0.14),
        "eye": pigment("Paint / warm ivory eye whites", "FFE0CF", 0.025),
        "iris": pigment("Paint / dusty blue irises", "87ADBB", 0.045),
        "iris_edge": pigment("Paint / iris dry brush", "98BBC7", 0.06),
        "pupil": pigment("Paint / deep aubergine pupils", "512D2D", 0.02),
        "glint": pigment("Paint / cream eye catchlights", "FFF1DC", 0.015),
        "blush": pigment("Paint / red circular cheeks", "FA4648", 0.08),
        "nose_line": pigment("Paint / umber nose line", "974B37", 0.08),
        "nose_light": pigment("Paint / apricot nose highlight", "FFB18A", 0.035),
        "nose_plum": pigment("Paint / muted plum nose shadow", "BD5B72", 0.06),
        "lips": pigment("Paint / rose pink lips", "F16C80", 0.07),
        "lip_shadow": pigment("Paint / upper lip mauve accent", "CC5D7A", 0.09),
        "mouth": pigment("Paint / deep warm mouth", "664239", 0.035),
        "teeth": pigment("Paint / peach ivory teeth", "FFDFCC", 0.025),
        "shirt": pigment("Paint / coral shirt", "EC584D", 0.08),
        "collar": pigment("Paint / burgundy collar", "7A3331", 0.07),
    }
    m = materials
    paper = "00 - Paper and border"
    sketch = "01 - Charcoal sketch halo"
    base = "02 - Silhouette and collar"
    face = "03 - Face and cheeks"
    eyes = "04 - Eyes and catchlights"
    nose = "05 - Painted nose"
    mouth = "06 - Mouth and four teeth"
    hair = "07 - Bob haircut"
    strands = "08 - Hand painted hair strands"

    shape("Board - rounded umber edge",
          "M -14 -16 L 1517 -16 L 1517 1620 L -14 1620 Z",
          m["frame"], -0.39, paper, thickness=0.11, bevel=0.018)
    shape("Sage paper - softly rounded corners",
          """M 67 30 C 330 14 1182 10 1427 18
          C 1455 20 1466 42 1466 73 L 1471 1509
          C 1472 1550 1453 1569 1415 1573
          C 1100 1590 356 1596 76 1607
          C 50 1607 35 1589 35 1558 L 19 86
          C 18 51 33 32 67 30 Z""",
          m["paper"], -0.29, paper, thickness=0.045, bevel=0.004)
    shape("Grey wash behind the head",
          """M 713 184 C 483 184 294 278 196 477
          C 130 606 104 751 104 840
          C 71 861 68 903 78 947 C 85 983 105 1001 127 1008
          C 131 1145 158 1286 252 1390
          C 335 1480 500 1519 640 1528
          C 760 1550 931 1484 1069 1425
          C 1267 1343 1416 1276 1451 1113
          C 1478 993 1446 793 1409 654
          C 1364 484 1254 322 1122 252
          C 1002 188 846 165 713 184 Z""",
          m["halo"], -0.20, sketch, thickness=0.009)

    for i in range(15):
        points = []
        phase = RNG.uniform(0, math.tau)
        for j in range(330):
            angle = j / 330 * math.tau
            waviness = (5.5 * math.sin(11 * angle + phase)
                        + 3 * math.cos(27 * angle + phase)
                        + 1.4 * math.sin(73 * angle + i))
            rx = 650 + (i - 7) * 2.7 + waviness
            ry = 613 + (i - 7) * 2.6 + waviness
            points.append((777 + rx * math.cos(angle) + 22 * math.sin(2 * angle),
                           857 + ry * math.sin(angle) + 11 * math.cos(3 * angle)))
        pencil(f"Loose charcoal contour {i + 1:02d}", points,
               m["pencil" if i % 3 == 0 else "pencil_light"],
               -0.184 + i * 0.0006, sketch, width=RNG.uniform(0.6, 1.8), cyclic=True)

    for i in range(10):
        x = 123 + i * 2.2
        brush(f"Rubbed charcoal left {i + 1:02d}", (x + 12, 682 + i * 14),
              [((x - 25, 850), (x + 1, 1120), (x + 84, 1264 + i * 8))],
              RNG.uniform(1.8, 4.0), m["chalk"], -0.157, sketch, roughness=3.5)
    for i in range(9):
        brush(f"Rubbed charcoal lower arc {i + 1:02d}", (243 + i * 12, 1340 + i * 8),
              [((436, 1514 + i * 2), (540, 1466 + i * 9), (636, 1471 + i * 3))],
              RNG.uniform(2, 6), m["chalk"], -0.155, sketch, roughness=4)
    for i in range(7):
        brush(f"Charcoal right sweep {i + 1:02d}", (990 + i * 14, 1455 - i * 5),
              [((1283, 1345), (1440 + i * 2, 1230), (1446 + i * 2, 993))],
              RNG.uniform(1, 3), m["pencil"], -0.154, sketch, roughness=3)

    shape("Dark offset head and neck silhouette",
          """M 338 661 C 567 615 980 613 1222 681
          C 1293 815 1241 1085 1198 1238
          C 1110 1320 1003 1345 935 1413
          C 890 1453 872 1500 852 1550
          L 608 1608 C 624 1560 667 1511 656 1466
          C 645 1411 626 1390 569 1370
          C 482 1339 389 1302 331 1262
          C 281 1087 260 826 338 661 Z""",
          m["shadow"], -0.01, base, thickness=0.021)
    shape("Coral shirt - cropped at the bottom edge",
          """M 579 1609 C 592 1574 624 1524 679 1499
          C 739 1468 829 1454 884 1473
          C 957 1485 1005 1538 1010 1609 Z""",
          m["shirt"], 0.045, base, thickness=0.025)
    shape("Burgundy collar inset",
          """M 714 1545 C 748 1480 826 1459 884 1480
          C 956 1501 994 1545 1003 1606
          L 870 1606 C 841 1581 814 1592 790 1596
          C 750 1598 721 1588 714 1545 Z""",
          m["collar"], 0.068, base, thickness=0.011)
    oval("Left ear", 146, 913, 29, 66, m["ear"], 0.09, base, organic=0.02)

    head = shape("Peach face and tapered neck",
          """M 323 669 C 539 641 812 633 1065 648
          C 1170 651 1236 677 1243 718
          C 1276 814 1239 975 1205 1173
          C 1208 1207 1187 1229 1149 1252
          C 1053 1299 971 1333 922 1401
          C 893 1440 880 1471 872 1511
          C 865 1539 861 1554 842 1567
          C 812 1580 767 1583 737 1569
          C 710 1555 702 1519 691 1482
          C 678 1432 657 1399 612 1371
          C 558 1337 477 1310 400 1277
          C 370 1264 348 1259 339 1226
          C 306 1124 293 972 288 851
          C 283 770 294 705 323 669 Z""",
          m["skin"], 0.14, face, thickness=0.048, bevel=0.002)
    oval("Left painted red cheek", 470, 1078, 86, 75,
         m["blush"], 0.173, face, organic=0.022, thickness=0.004)
    oval("Right painted red cheek", 1039, 1042, 83, 75,
         m["blush"], 0.173, face, organic=0.024, thickness=0.004)

    shape("Left eye - ivory outline",
          """M 471 957 C 438 924 435 842 468 806
          C 494 769 535 754 569 762
          C 615 764 642 788 660 826
          C 680 868 677 920 649 957
          C 597 945 522 944 471 957 Z""",
          m["eye"], 0.191, eyes, thickness=0.019)
    shape("Right eye - ivory outline",
          """M 878 945 C 846 915 840 865 856 822
          C 875 774 919 739 962 743
          C 1017 739 1058 775 1073 819
          C 1086 860 1081 908 1056 939
          C 1001 924 928 926 878 945 Z""",
          m["eye"], 0.191, eyes, thickness=0.019)
    for side, cx, cy, px, py in (
            ("Left", 557, 859, 557, 860),
            ("Right", 954, 843, 960, 842)):
        oval(f"{side} dusty blue iris", cx, cy, 61, 62,
             m["iris"], 0.214, eyes, organic=0.012, thickness=0.011)
        oval(f"{side} deep brown pupil", px, py, 29.5, 30,
             m["pupil"], 0.23, eyes, organic=0.012, thickness=0.008)
        oval(f"{side} cream eye catchlight", px + 13, py - 17, 14, 14.5,
             m["glint"], 0.241, eyes, organic=0.008, thickness=0.004)
        brush(f"{side} iris dry-brush edge", (cx + 52, cy - 25),
              [((cx + 70, cy + 3), (cx + 61, cy + 34), (cx + 24, cy + 53))],
              2.5, m["iris_edge"], 0.222, eyes, roughness=1.4)

    shape("Nose - curved umber brush contour",
          """M 713 794 C 729 800 743 844 743 881
          C 743 934 724 978 700 1007
          C 684 1026 674 1046 676 1062
          C 679 1084 698 1102 733 1111
          C 778 1121 830 1097 851 1071
          C 856 1098 850 1112 799 1121
          C 747 1134 699 1118 670 1085
          C 650 1063 647 1040 667 1013
          C 689 980 717 943 724 902
          C 733 860 720 822 710 803
          C 708 797 709 793 713 794 Z""",
          m["nose_line"], 0.193, nose, thickness=0.005)
    shape("Nose - apricot lit plane",
          """M 735 813 C 748 860 747 904 758 954
          C 770 1003 781 1047 760 1078
          C 751 1092 742 1104 733 1111
          C 703 1101 681 1082 676 1062
          C 672 1045 691 1022 707 997
          C 731 961 742 916 743 884
          C 744 852 739 833 735 813 Z""",
          m["nose_light"], 0.202, nose, thickness=0.005)
    shape("Nose - plum shadow plane",
          """M 738 1113 C 755 1098 774 1083 784 1068
          C 796 1044 787 1005 808 984
          C 814 977 823 984 837 1003
          C 858 1023 867 1058 850 1080
          C 824 1098 786 1115 738 1113 Z""",
          m["nose_plum"], 0.207, nose, thickness=0.005)
    brush("Nose - dark lower edge", (721, 1110),
          [((763, 1131), (825, 1112), (852, 1083))],
          8.0, m["nose_line"], 0.213, nose, roughness=0.25)

    shape("Rose pink lip silhouette",
          """M 648 1221 C 668 1182 734 1157 806 1152
          C 885 1145 916 1169 931 1208
          C 946 1251 894 1299 839 1320
          C 778 1349 710 1344 674 1307
          C 643 1273 638 1247 648 1221 Z""",
          m["lips"], 0.194, mouth, thickness=0.013)
    brush("Upper lip - mauve brush accent", (653, 1249),
          [((645, 1214), (693, 1177), (767, 1167))],
          14.0, m["lip_shadow"], 0.209, mouth, roughness=0.8)
    shape("Open mouth - warm dark interior",
          """M 669 1229 C 697 1191 744 1180 802 1182
          C 850 1177 891 1193 899 1226
          C 905 1260 865 1293 811 1306
          C 753 1322 706 1299 683 1275
          C 671 1261 665 1242 669 1229 Z""",
          m["mouth"], 0.214, mouth, thickness=0.006)
    tooth_paths = [
        """M 674 1232 C 685 1213 706 1198 736 1192
        L 732 1245 C 710 1243 690 1240 674 1237 Z""",
        """M 740 1191 C 754 1186 774 1183 786 1184
        L 789 1247 C 772 1249 751 1248 737 1246 Z""",
        """M 791 1184 C 809 1182 828 1184 841 1187
        L 837 1245 C 823 1247 808 1248 794 1247 Z""",
        """M 846 1189 C 872 1194 891 1207 896 1227
        C 880 1235 860 1242 842 1244 Z""",
    ]
    for i, path in enumerate(tooth_paths, 1):
        shape(f"Upper tooth {i} - separate editable shape", path,
              m["teeth"], 0.223, mouth, thickness=0.005, bevel=0.0005)

    shape("Orange bob - fringe and curved side locks",
          """M 725 125 C 590 120 462 183 363 301
          C 223 448 155 646 140 846
          C 129 940 137 1107 160 1175
          C 174 1216 239 1258 329 1276
          C 359 1281 379 1270 373 1233
          C 329 1077 278 926 290 776
          C 290 725 309 703 354 691
          C 509 668 697 664 862 653
          C 1014 640 1137 642 1193 675
          C 1252 710 1256 809 1239 929
          C 1218 1085 1182 1184 1198 1251
          C 1206 1283 1224 1301 1248 1288
          C 1317 1243 1415 1153 1428 1080
          C 1443 984 1399 798 1354 660
          C 1290 465 1202 326 1082 226
          C 967 138 847 121 725 125 Z""",
          m["hair"], 0.244, hair, thickness=0.047, bevel=0.002)
    brush("Orange left rim - dry highlight", (351, 317),
          [((210, 495), (153, 721), (159, 976))],
          6.0, m["hair_light"], 0.271, hair, roughness=0.8)
    brush("Orange lower lock - dry highlight", (291, 1048),
          [((295, 1148), (315, 1220), (342, 1259))],
          4.0, m["hair_light"], 0.271, hair, roughness=0.9)

    strand_data = [
        ((537, 197), [((438, 248), (276, 419), (231, 613)),
                      ((184, 813), (192, 983), (193, 1132))], 8),
        ((565, 185), [((450, 248), (327, 432), (292, 589)),
                      ((238, 800), (222, 1052), (277, 1218))], 10),
        ((553, 211), [((491, 286), (307, 565), (283, 739)),
                      ((247, 925), (271, 1162), (318, 1250))], 6),
        ((305, 395), [((263, 489), (212, 768), (206, 1124))], 6),
        ((720, 140), [((649, 230), (469, 352), (462, 610))], 30),
        ((706, 168), [((652, 276), (518, 416), (524, 641))], 13),
        ((695, 203), [((652, 339), (581, 428), (585, 563))], 10),
        ((687, 241), [((680, 342), (646, 492), (679, 622))], 9),
        ((715, 231), [((718, 350), (754, 493), (740, 635))], 13),
        ((657, 297), [((617, 402), (645, 523), (627, 641))], 12),
        ((556, 235), [((518, 324), (433, 487), (386, 651))], 7),
        ((609, 398), [((612, 452), (603, 507), (599, 582))], 5),
        ((767, 230), [((794, 324), (821, 441), (839, 561))], 10),
        ((758, 353), [((775, 432), (781, 517), (782, 631))], 11),
        ((820, 214), [((874, 282), (975, 413), (1045, 517))], 11),
        ((825, 258), [((915, 376), (961, 530), (969, 597))], 12),
        ((830, 341), [((882, 426), (909, 539), (897, 618))], 11),
        ((894, 230), [((1002, 371), (1061, 510), (1143, 608))], 9),
        ((851, 238), [((939, 326), (1014, 540), (1086, 630))], 8),
        ((889, 164), [((1036, 194), (1178, 449), (1336, 928))], 30),
        ((935, 174), [((1161, 337), (1300, 685), (1391, 986))], 20),
        ((975, 211), [((1193, 473), (1330, 746), (1356, 1144))], 9),
        ((1029, 320), [((1149, 572), (1266, 928), (1299, 1203))], 15),
        ((1091, 490), [((1150, 584), (1207, 748), (1238, 876))], 7),
        ((1124, 489), [((1200, 614), (1298, 913), (1318, 1089))], 6),
    ]
    for i, (start, segments, width) in enumerate(strand_data, 1):
        ink = m["hair_ink_light" if i % 5 == 0 else "hair_ink"]
        brush(f"Sienna hair stroke {i:02d}", start, segments, width,
              ink, 0.272 + (i % 3) * 0.0003, strands, roughness=1.0)
        if i in (2, 5, 6, 9, 14, 20, 21, 23):
            offset = -6 if i % 2 else 7
            shifted_start = (start[0] + offset, start[1] + 5)
            shifted = [
                tuple((point[0] + offset, point[1] + 5) for point in segment)
                for segment in segments
            ]
            brush(f"Dry edge beside hair stroke {i:02d}", shifted_start, shifted,
                  max(1.1, width * 0.12), m["hair_ink_light"],
                  0.274, strands, roughness=1.5)

    for i, (x, y) in enumerate(((396, 650), (530, 643), (541, 643), (600, 568),
                                (637, 642), (689, 613), (750, 631), (796, 624),
                                (858, 555), (911, 615), (980, 599)), 1):
        brush(f"Broken brush tip {i:02d}", (x, y),
              [((x - 0.5, y + 3), (x + 1.5, y + 8), (x + 1, y + 11))],
              2.7, m["hair_ink_light"], 0.274, strands, roughness=0.25)

    reference_path = ROOT.parent / "reference" / "redhead-girl-reference.png"
    if not reference_path.is_file():
        raise FileNotFoundError(f"Required reference image is missing: {reference_path}")
    reference = bpy.data.images.load(str(reference_path), check_existing=True)
    reference.pack()
    reference_obj = link_object("Original reference - packed into blend", None,
                                "90 - Original reference (hidden)")
    reference_obj.empty_display_type = "IMAGE"
    reference_obj.data = reference
    reference_obj.empty_display_size = 8
    reference_obj.location = (-10, 0, 0)
    reference_obj.hide_render = True
    collection("90 - Original reference (hidden)").hide_viewport = True
    collection("90 - Original reference (hidden)").hide_render = True

    scene = bpy.context.scene
    scene.name = "Orange bob - layered paper portrait"
    scene["Artwork type"] = "Editable 2.5D painted-paper relief"
    scene["Reference"] = "User-supplied character reference, packed into this file."
    scene["Editing"] = "Named collections separate face, eyes, nose, mouth and hair. Curves retain editable handles."
    scene["Camera usage"] = "Front portrait matches the reference; angled camera reveals the layered construction."
    front = camera("CAMERA - front portrait", (0, 0, 18), (0, 0, 0), 8.0)
    camera("CAMERA - angled paper relief", (8, -4, 13), (0, 0, 0), 9.4)
    light("Large softbox - upper left", (-3.5, 4.5, 8), 350, 5.0)
    light("Soft fill - right", (4, -0.5, 7), 100, 5.0)
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
    embedded_script = bpy.data.texts.new("create_character.py")
    embedded_script.write(Path(__file__).read_text())
    notes = bpy.data.texts.new("ABOUT THE ARTWORK")
    notes.write(
        "ORANGE BOB - LAYERED PAPER PORTRAIT\n\n"
        "A reference-inspired 2.5D illustration, not a rigged or closed 3D head.\n"
        "The front orthographic camera is the main artwork composition.\n"
        "Use the angled camera or orbit to inspect the shallow paper relief.\n\n"
        "Every feature is editable and organized in numbered collections.\n"
        "Large silhouettes retain Bezier handles. Hair strokes are individual\n"
        "tapered curve shapes. Teeth, eye highlights, and pupils are separate.\n"
        "Materials use subtle procedural pigment grain; no external textures\n"
        "are required. The supplied reference image is packed into this file.\n\n"
        "The regeneration script is embedded here and also supplied separately.\n"
    )
    return scene


def main():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args(arguments)
    scene = build()
    if args.preview:
        scene.render.resolution_percentage = 50
        scene.cycles.samples = 24
    destination = ROOT.parent / "renders" / ("preview.png" if args.preview else "redhead-portrait.png")
    scene.render.filepath = str(destination)
    bpy.context.preferences.filepaths.save_version = 0
    blend_path = ROOT / "redhead-portrait.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    if not args.no_render:
        bpy.ops.render.render(write_still=True)
    print(f"ARTWORK_BLEND={blend_path}", flush=True)
    print(f"ARTWORK_RENDER={destination}", flush=True)
    print(f"ARTWORK_OBJECTS={len(bpy.data.objects)}", flush=True)


if __name__ == "__main__":
    main()
