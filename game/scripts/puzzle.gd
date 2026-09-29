extends Node2D

const CHARACTERS: Array[String] = [
	"CHR_M_001_COILS_YELLOW", "CHR_F_001_PUFFS_OVERALLS"
]
const BOARD := Rect2(352, 170, 450, 479.36)
const EXAMPLE := Rect2(40, 214, 244, 259.92)
const REPLAY := Rect2(40, 690, 200, 64)
const SWITCH := Rect2(264, 690, 230, 64)
const SOUND := Rect2(518, 690, 200, 64)
const INK := Color("#30291f")
const GREEN := Color("#397962")

class Piece:
	var id: String
	var texture: Texture2D
	var target: Vector2
	var position: Vector2
	var home: Vector2
	var draw_scale: float
	var tray_scale: float
	var z_order: int
	var placed := false
	var moving := false

var pieces: Array[Piece] = []
var character_index := 0
var example: Texture2D
var base: Texture2D
var title := ""
var error_message := ""
var board_scale := 1.0
var snap_radius := 1.0
var dragged: Piece
var pointer_id := -2
var grab_offset := Vector2.ZERO
var placed_count := 0
var completed := false
var sound_enabled := true
var celebration_time := 0.0
var animations: Array[Tween] = []
var player := AudioStreamPlayer.new()
var font: Font = ThemeDB.fallback_font
var button_textures: Dictionary = {}
var press_time: Dictionary = {}
const PRESS_DURATION := 0.15

func _ready() -> void:
	add_child(player)
	for key in ["replay", "switch", "sound"]:
		button_textures[key] = load("res://assets/ui/button_%s.png" % key) as Texture2D
	load_character(0)
	get_viewport().size_changed.connect(update_layout)
	get_window().focus_exited.connect(cancel_drag)
	update_layout()

func update_layout() -> void:
	var available := get_viewport_rect().size
	var factor := minf(available.x / 1280.0, available.y / 800.0)
	scale = Vector2.ONE * factor
	position = (available - Vector2(1280, 800) * factor) / 2
	queue_redraw()

func fail_loading(message: String) -> void:
	push_error(message)
	error_message = message
	pieces.clear()
	queue_redraw()

func load_character(index: int) -> void:
	for animation in animations:
		if animation.is_valid():
			animation.kill()
	animations.clear()
	dragged = null
	pointer_id = -2
	pieces.clear()
	placed_count = 0
	completed = false
	celebration_time = 0
	error_message = ""
	character_index = index % CHARACTERS.size()
	var folder := "res://assets/characters/" + CHARACTERS[character_index] + "/"
	var file := FileAccess.open(folder + "pieces.json", FileAccess.READ)
	if file == null:
		fail_loading("Cannot open this character's pieces.json.")
		return
	var parser := JSON.new()
	if parser.parse(file.get_as_text()) != OK or not parser.data is Dictionary:
		fail_loading("The character's pieces.json is not valid JSON.")
		return
	var data: Dictionary = parser.data
	for key in ["title", "canvas_width", "canvas_height", "base", "example", "snap_radius", "pieces"]:
		if not data.has(key):
			fail_loading("The character is missing: " + key)
			return
	if float(data.canvas_width) <= 0 or float(data.canvas_height) <= 0:
		fail_loading("The character canvas must have a positive size.")
		return
	base = load(folder + str(data.base)) as Texture2D
	example = load(folder + str(data.example)) as Texture2D
	if base == null or example == null:
		fail_loading("A character picture could not be loaded.")
		return
	title = str(data.title)
	board_scale = BOARD.size.x / float(data.canvas_width)
	snap_radius = maxf(38.0, float(data.snap_radius) * board_scale)
	if not data.pieces is Array or data.pieces.is_empty() or data.pieces.size() > 9:
		fail_loading("This prototype needs between one and nine pieces.")
		return
	var ids: Dictionary = {}
	for entry in data.pieces:
		if not entry is Dictionary:
			fail_loading("A piece entry must be an object.")
			return
		for key in ["id", "file", "target_x", "target_y", "z_order"]:
			if not entry.has(key):
				fail_loading("A piece is missing: " + key)
				return
		var item := Piece.new()
		item.id = str(entry.id)
		item.z_order = int(entry.z_order)
		if ids.has(item.id):
			fail_loading("Duplicate piece ID: " + item.id)
			return
		ids[item.id] = true
		item.texture = load(folder + str(entry.file)) as Texture2D
		if item.texture == null:
			fail_loading("Cannot load the piece: " + item.id)
			return
		item.target = BOARD.position + Vector2(float(entry.target_x), float(entry.target_y)) * board_scale
		item.home = Vector2(906 + (pieces.size() % 3) * 134, 277 + (pieces.size() / 3) * 136)
		item.tray_scale = minf(108.0 / item.texture.get_width(), 98.0 / item.texture.get_height())
		item.draw_scale = item.tray_scale
		item.position = item.home
		pieces.append(item)
	pieces.sort_custom(func(a: Piece, b: Piece) -> bool: return a.z_order < b.z_order)
	queue_redraw()

func _process(delta: float) -> void:
	if completed:
		celebration_time += delta
	for key in press_time.keys():
		if press_time[key] < PRESS_DURATION:
			press_time[key] = minf(press_time[key] + delta, PRESS_DURATION)
	queue_redraw()

func card(rect: Rect2, color: Color, radius := 20) -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(radius)
	draw_style_box(style, rect)

func text_at(value: String, point: Vector2, size := 24, color := INK) -> void:
	draw_string(font, point, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func button(rect: Rect2, label: String, key: String) -> void:
	var progress := clampf(press_time.get(key, PRESS_DURATION) / PRESS_DURATION, 0.0, 1.0)
	var bounce := lerpf(0.93, 1.0, ease(progress, 0.4))
	var size := rect.size * bounce
	var offset := (rect.size - size) / 2.0 + Vector2(0, rect.size.y * (1.0 - bounce) * 0.6)
	var tint := Color(1, 1, 1) if progress >= 1.0 else Color(0.92, 0.92, 0.92)
	draw_texture_rect(button_textures[key], Rect2(rect.position + offset, size), false, tint)
	text_at(label, rect.position + offset + Vector2(18, rect.size.y * 0.64 * bounce), 23)

func _draw() -> void:
	text_at("Let's build a face!", Vector2(40, 64), 38)
	text_at("Drag a piece onto the face. Near enough? It clicks into place!", Vector2(40, 105), 23)
	if not error_message.is_empty():
		text_at("Oops - the artwork could not load.", Vector2(40, 190), 28)
		text_at(error_message, Vector2(40, 235), 20)
		return
	if base == null:
		return
	card(Rect2(24, 158, 276, 410), Color.WHITE)
	text_at("Make this face", Vector2(50, 198), 25)
	draw_texture_rect(example, EXAMPLE, false)
	text_at(title, Vector2(46, 522), 21)
	card(Rect2(336, 154, 482, 511), Color.WHITE)
	draw_texture_rect(base, BOARD, false)
	card(Rect2(834, 158, 422, 507), Color("#eee9df"))
	text_at("Your pieces", Vector2(852, 199), 25)
	for item in pieces:
		if not item.placed:
			card(Rect2(item.home - Vector2(61, 59), Vector2(122, 118)), Color("#fffdf7"), 14)
	for item in pieces:
		if item != dragged:
			draw_piece(item)
	if dragged != null:
		draw_piece(dragged)
	text_at("%d / %d pieces" % [placed_count, pieces.size()], Vector2(862, 635), 24, GREEN)
	button(REPLAY, "Start again", "replay")
	button(SWITCH, "Other character", "switch")
	button(SOUND, "Sound: on" if sound_enabled else "Sound: off", "sound")
	if completed:
		card(Rect2(757, 683, 496, 83), Color("#d8edc9"), 20)
		text_at("You made it! Lovely work!", Vector2(778, 735), 28, GREEN)
		for i in range(18):
			var x := 364.0 + fmod(float(i * 71), 435.0)
			var y := 155.0 + fmod(celebration_time * 75 + i * 37, 470)
			draw_circle(Vector2(x, y), 4, Color("#efbd46") if i % 2 else Color("#df755c"))

func draw_piece(item: Piece) -> void:
	var size := item.texture.get_size() * item.draw_scale
	draw_texture_rect(item.texture, Rect2(item.position - size / 2, size), false)

func local_pointer(point: Vector2) -> Vector2:
	return get_global_transform().affine_inverse() * point

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			press(local_pointer(event.position), event.index)
		elif event.index == pointer_id:
			move_piece(local_pointer(event.position))
			if event.canceled:
				cancel_drag()
			else:
				release_piece()
	elif event is InputEventScreenDrag and event.index == pointer_id:
		move_piece(local_pointer(event.position))
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			press(local_pointer(event.position), -1)
		elif pointer_id == -1:
			move_piece(local_pointer(event.position))
			release_piece()
	elif event is InputEventMouseMotion and pointer_id == -1:
		move_piece(local_pointer(event.position))
	elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		cancel_drag()

func press(point: Vector2, id: int) -> void:
	if pointer_id != -2 or not error_message.is_empty():
		return
	if REPLAY.has_point(point):
		press_time["replay"] = 0.0
		load_character(character_index)
		return
	if SWITCH.has_point(point):
		press_time["switch"] = 0.0
		load_character(character_index + 1)
		return
	if SOUND.has_point(point):
		press_time["sound"] = 0.0
		sound_enabled = not sound_enabled
		return
	for i in range(pieces.size() - 1, -1, -1):
		var item := pieces[i]
		if item.placed or item.moving:
			continue
		var size := item.texture.get_size() * item.draw_scale
		var target_size := Vector2(maxf(size.x, 64), maxf(size.y, 64))
		if Rect2(item.position - target_size / 2, target_size).has_point(point):
			dragged = item
			pointer_id = id
			grab_offset = (point - item.position) / item.draw_scale
			item.draw_scale = board_scale
			move_piece(point)
			return

func move_piece(point: Vector2) -> void:
	if dragged != null:
		dragged.position = point - grab_offset * board_scale

func release_piece() -> void:
	if dragged == null:
		return
	var item := dragged
	dragged = null
	pointer_id = -2
	if item.position.distance_to(item.target) <= snap_radius:
		item.placed = true
		placed_count += 1
		animate_piece(item, item.target, board_scale)
		play_note()
		if placed_count == pieces.size():
			completed = true
	else:
		animate_piece(item, item.home, item.tray_scale)

func cancel_drag() -> void:
	if dragged != null:
		var item := dragged
		dragged = null
		animate_piece(item, item.home, item.tray_scale)
	pointer_id = -2

func animate_piece(item: Piece, destination: Vector2, destination_scale: float) -> void:
	item.moving = true
	var tween := create_tween().set_parallel(true)
	animations.append(tween)
	tween.tween_property(item, "position", destination, 0.24).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if item.placed:
		tween.tween_property(item, "draw_scale", destination_scale * 1.07, 0.12)
		tween.tween_property(item, "draw_scale", destination_scale, 0.12).set_delay(0.12)
	else:
		tween.tween_property(item, "draw_scale", destination_scale, 0.24)
	tween.finished.connect(func() -> void:
		item.moving = false
		animations.erase(tween)
	)

func play_note() -> void:
	if not sound_enabled:
		return
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	var samples := PackedByteArray()
	samples.resize(6615 * 2)
	var frequency := 440.0 + placed_count * 55.0
	for i in range(6615):
		var envelope := sin(PI * float(i) / 6615) * exp(-float(i) / 1800)
		var value := int(sin(TAU * frequency * float(i) / 22050) * envelope * 6500)
		samples.encode_s16(i * 2, value)
	wav.data = samples
	player.stream = wav
	player.play()
