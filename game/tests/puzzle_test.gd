extends SceneTree

const Puzzle = preload("res://scripts/puzzle.gd")
var game: Node2D
var failures := 0

func check(condition: bool, message: String) -> void:
	if not condition:
		push_error("FAIL: " + message)
		failures += 1

func _initialize() -> void:
	call_deferred("run")

func mouse(point: Vector2, pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	event.position = game.get_global_transform() * point
	game._input(event)

func touch(point: Vector2, pressed: bool, index := 0) -> void:
	var event := InputEventScreenTouch.new()
	event.position = game.get_global_transform() * point
	event.index = index
	event.pressed = pressed
	game._input(event)

func run() -> void:
	game = Puzzle.new()
	root.add_child(game)
	await process_frame
	for index in range(2):
		game.load_character(index)
		game.sound_enabled = false
		check(game.error_message.is_empty(), "character loads")
		check(game.pieces.size() == (7 if index == 0 else 9), "complete piece count")
		check(not game.completed, "new puzzle is not complete")
		for item in game.pieces:
			check(item.tray_scale > 0, "piece thumbnail has a nonzero scale")
		var first = game.pieces[0]
		mouse(first.home, true)
		check(game.dragged == first, "mouse can pick up a piece")
		mouse(Vector2(80, 140), false)
		await create_timer(0.3).timeout
		check(first.position.is_equal_approx(first.home), "wrong drop returns to tray")
		check(not first.placed and game.placed_count == 0, "wrong drop does not count")
		touch(first.home, true, 0)
		touch(game.pieces[1].home, true, 1)
		check(game.dragged == first and game.pointer_id == 0, "second finger cannot steal drag")
		touch(first.target, false, 1)
		check(game.dragged == first, "second finger release cannot finish drag")
		game.cancel_drag()
		await create_timer(0.3).timeout
		check(first.position.is_equal_approx(first.home), "cancel/focus loss restores tray")
		touch(first.home, true)
		touch(first.target + Vector2(game.snap_radius + 2, 0), false)
		await create_timer(0.3).timeout
		check(not first.placed, "outside snap threshold rejected")
		for item in game.pieces:
			var offset := Vector2(8, 0)
			touch(item.home + offset, true)
			var grab: Vector2 = game.grab_offset * game.board_scale
			touch(item.target + grab + Vector2(game.snap_radius - 1, 0), false)
			await create_timer(0.3).timeout
			check(item.placed and item.position.is_equal_approx(item.target), "near drop snaps " + item.id)
		check(game.completed and game.placed_count == game.pieces.size(), "all pieces celebrate")
		var total: int = game.placed_count
		mouse(first.target, true)
		mouse(first.target, false)
		check(game.placed_count == total and game.dragged == null, "placed pieces cannot count twice")
		verify_composite(index)
		game.load_character(index)
		check(game.placed_count == 0 and not game.completed, "replay resets completion")
		mouse(game.pieces[0].home, true)
		mouse(Vector2(20, 20), false)
		game.load_character(1 - index)
		await create_timer(0.3).timeout
		check(game.placed_count == 0 and game.animations.is_empty(), "switch cancels old animations")
	# Input coordinates must still work with letterboxed/resized presentation.
	game.scale = Vector2(0.75, 0.75)
	game.position = Vector2(17, 25)
	mouse(game.pieces[0].home, true)
	check(game.dragged == game.pieces[0], "scaled pointer hits")
	mouse(game.pieces[0].target, false)
	await create_timer(0.3).timeout
	check(game.pieces[0].placed, "scaled pointer drops at matching target")
	game.sound_enabled = true
	game.play_note()
	check(game.player.stream is AudioStreamWAV, "placement feedback has a playable sound")
	check(game.player.stream.data.size() == 13230, "sound buffer contains expected samples")
	game.player.stop()
	await create_timer(0.1).timeout
	game.queue_free()
	await process_frame
	print("PUZZLE TESTS: ", "PASS" if failures == 0 else "%d failures" % failures)
	quit(0 if failures == 0 else 1)

func verify_composite(index: int) -> void:
	var folder := "res://assets/characters/" + Puzzle.CHARACTERS[index] + "/"
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(folder + "pieces.json"))
	var assembled := (load(folder + "base.png") as Texture2D).get_image()
	var expected := (load(folder + "example.png") as Texture2D).get_image()
	for entry in manifest.pieces:
		var piece := (load(folder + entry.file) as Texture2D).get_image()
		check(piece.get_pixel(0, 0).a < 0.01, "piece has transparent crop padding")
		var target := Vector2i(int(entry.target_x - piece.get_width() / 2.0),
			int(entry.target_y - piece.get_height() / 2.0))
		assembled.blend_rect(piece, Rect2i(Vector2i.ZERO, piece.get_size()), target)
	var total_error := 0.0
	var samples := 0
	for y in range(0, expected.get_height(), 5):
		for x in range(0, expected.get_width(), 5):
			var a := assembled.get_pixel(x, y)
			var b := expected.get_pixel(x, y)
			total_error += absf(a.r - b.r) + absf(a.g - b.g) + absf(a.b - b.b)
			samples += 3
	check(total_error / samples < 0.012, "assembled pieces match example (mean RGB error < 1.2%)")
	print("Composite mean RGB error: ", total_error / samples)
