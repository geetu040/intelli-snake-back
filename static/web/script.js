let loaded_infos = []
interval_var_fast = 0
let start_auto = 1
let mult = 1

// WRITING IN A FILE
let file_writing = 0
let content = ''
let data_line

class Game {
	constructor () {
		// initializing constants and variables
		this.game_items = document.getElementsByClassName("game-item")
		this.info = {
			"map_type": "none",
			"map": 0,
			"parts": 2,
			"evade_bite": 0,
			"allowcollisions": 0,
			"score": 0,
			"fouls": 0,
			"interval_var": 0,
			"cache_dir": null,
			"prev_dir": null,
			"second_pref_count": 0,
			"mode": "paused",
			"steps": 0,
			"steps_limit": 60,
			"slow_time": 600,
			"fast_time": 200,
			"time": 200,
			"automated_infos_count": 50,
			"automated_time_update_freq": 1,
			"overflow_infos": 0,
		}
		// intializing the game
		this.get_map("fixed")
		btn_pause_auto.innerText = "Automate"
	}


	set_game_interval(func) {
		clearInterval(this.info.interval_var)
		this.info.interval_var = setInterval(func, this.info.time)
	}
	auto_key_move() {
		if (this.info.cache_dir != null) {
			if(game.move(this.info.cache_dir)) {this.info.prev_dir = this.info.cache_dir}
			else {game.move(this.info.prev_dir)}
		}
	}


	move(dir) {
		if (file_writing) {data_line = "\n" + JSON.stringify(this.info.map)}

		let h = this.info.map.indexOf(3)
		let n = 31*28
		if (dir == 0) { n = h - cols }
		else if (dir == 1) { n = h - 1 }
		else if (dir == 2) { n = h + cols }
		else if (dir == 3) { n = h + 1 }

		// IF FOOD IS EATEN
		if (this.info.map[n] == 2) {
			this.info.score++
			this.info.parts++
			this.info.steps = 0
			if (this.info.map_type == "random" && file_writing) {
				// LOADING NEW RANDOM MAP AFTER EATEN
				this.pause_game()
				this.get_map("random")
				return true
			}
			this.info.map[n] = this.info.parts+3
			let r = Math.floor(Math.random() * (31*28))
			while (this.info.map[r] != 0) { r = Math.floor(Math.random() * (31*28)) }
			this.info.map[r] = 2
			this.pause_game()
		}
		// CHECKING FOR FOUL WHEN HIT THE WALL
		if (this.info.map[n] == 1 && this.info.allowcollisions) { this.info.fouls++ }
		// IF SNAKE HITS THE BODY
		if (this.info.map[n] > 4 && this.info.map[n] != this.info.parts+3 && !this.info.evade_bite) {
			let parts_to_remove = (this.info.parts+3) - this.info.map[n]
			for (let i=0; i<parts_to_remove; i++) { this.info.map[this.info.map.indexOf(this.info.parts-i+3)] = 0 }
			this.info.parts -= parts_to_remove
			this.info.fouls++
		}

		// MOVING THE BODY
		if (this.can_move(n, dir)) {
			let cache_n;
			for (let part=0; part<=this.info.parts; part++) {
				cache_n = this.info.map.indexOf(3+part)
				this.info.map[this.info.map.indexOf(3+part)] = 0
				this.info.map[n] = 3+part
				n = cache_n
			}
			this.update_map()
			this.info.steps++
			if (this.info.steps > this.info.steps_limit) { btn_replace.click();this.info.steps=0;this.info.fouls++ }

			if (file_writing) {
				data_line += "," + String(dir)
				content += data_line
			}
			
			return true
		} else {return false}
	}
	can_move(next_step, dir) {
		let next_item = this.info.map[next_step]
		// IF SNAKE GOES OUT OF BOUNDARIES
		if (next_step < 0 || next_step > 31*28-1) {return false}
		if (dir == 1 && next_step % 28 == 27) {return false}
		if (dir == 3 && next_step % 28 == 0) {return false}
		// ILLEGAL STEP INSIDE THE BOUNDARIES
		switch (next_item) {
			case 0: return true
			case 1: if (this.info.allowcollisions) {return true} return false
			case 2: return true
			case 3: return false
			case 4: return false
			default: return true;
		}
	}

	automate_faster(time) {
		clearInterval(interval_var_fast)
		interval_var_fast = setInterval(() => {
			if (loaded_infos.length > 1) {
				this.info = loaded_infos[0]
				this.update_map()
				loaded_infos.shift()
			} else { console.log('\n ==== OUT OF INFOS ==== \n') }
		}, time);
	}
	load_automated_infos() {
		let time_i = Date.now()
		$.ajax({
			url: '/automate_faster',
			dataType: 'json',
			async: true,
			data: {"data": JSON.stringify(loaded_infos[loaded_infos.length-1])},
			success: (returned_infos)=>{
				if (btn_fast_automation.innerText == "Fast Automation") {if(btn_guide.innerText == "Guide"){btn_fast_automation.disabled = false};return}
				loading.style.setProperty("visibility", "hidden")
				// adding more infos
				if (loaded_infos.length < 200 || this.info['overflow_infos']) {loaded_infos = loaded_infos.concat(returned_infos)}
				console.log("ADDED NEW INFOS")
				console.table(`infos count: ${loaded_infos.length}`)

				// Finding optimal time for interval
				let time_f = Date.now()
				let fast_time = (time_f - time_i)/(this.info.automated_infos_count*mult)
				if (this.info.automated_time_update_freq) { game.automate_faster(fast_time) }
				else {if (start_auto == 1) {game.automate_faster(fast_time); start_auto=0;}}
				console.log(`FAST TIME: ${fast_time}`)

				console.log("\n")
				this.load_automated_infos()
			}
		});

	}
	automate() {
		let returned = $.ajax({
			url: '/automate',
			dataType: 'json',
			async: false,
			data: {"data": JSON.stringify(this.info)},
		});
		let pred_dirs = JSON.parse(returned['responseText'])  // predicted directions sorted by preference
		for (let i=0; i<4; i++) { if (this.move(pred_dirs[i])) { this.info.second_pref_count += i; break } }
	}



	get_map(map_type) {
		// getting the maps
		this.info.map_type = map_type
		this.info.steps = 0
		let returned = $.ajax({
			url: '/map',
			dataType: 'json',
			async: false,
			data: {"data": JSON.stringify(this.info)},
		});
		this.info = JSON.parse(returned['responseText'])
		this.update_map()
	}
	update_map() {
		// APPLYING LIST TO VISUAL GRID
		for (let i=0; i<rows*cols; i++) {
			this.game_items[i].classList.remove('wall')
			this.game_items[i].classList.remove('empty')
			this.game_items[i].classList.remove('food')
			this.game_items[i].classList.remove('head')
			this.game_items[i].classList.remove('body')
			switch (this.info.map[i]) {
				case 0: this.game_items[i].classList.add("empty"); break
				case 1: this.game_items[i].classList.add("wall"); break
				case 2: this.game_items[i].classList.add("food"); break
				case 3: this.game_items[i].classList.add("head"); break
				default: this.game_items[i].classList.add("body"); break
			}
		}
		// UPDATING THE BOARD
		score_span.innerText = this.info.score
		fouls_span.innerText = this.info.fouls
		steps_span.innerText = this.info.steps
	}
	pause_game() {
		clearInterval(this.info.interval_var)
		clearInterval(interval_var_fast)
		btn_fast_automation.innerText = "Fast Automation"
		btn_pause_auto.innerText = "Automate"
		this.info.mode = "paused"
		loaded_infos = []
		start_auto = 1
		this.info.cache_dir = null
		btn_next_map.disabled = false
		btn_speeder.disabled = false
		if (this.info.map_type == "fixed") {btn_collide.disabled = false}
		btn_replace.disabled = false
		// btn_fast_automation.disabled = false
		btn_pause_auto.disabled = false
		loading.style.setProperty("visibility", "hidden")

	}
}
let game = new Game()
// KEYBOARD EVENTS
document.onkeydown = (event)=> {
	// writing in a file
	if (event.key == 'Backspace' && file_writing) {
		content = ''
	}
	if (event.key == 'Enter' && file_writing) {
		$.ajax({
			url: '/write',
			dataType: 'json',
			async: true,
			data: {"content": content},
		});
		content = ''
		return
	}
	// controls
	if (event.key == 'ArrowRight') { game.info.cache_dir = 3 }
	if (event.key == 'ArrowLeft') { game.info.cache_dir = 1 }
	if (event.key == 'ArrowUp') { game.info.cache_dir = 0 }
	if (event.key == 'ArrowDown') { game.info.cache_dir = 2 }
	if (event.key == ' ') { game.pause_game(); return }
	if (game.info.mode == "paused") {
		// PLAY THE GAME WITH KEYS
		game.set_game_interval(()=>{ game.auto_key_move() })
		game.info.mode = "key"
	}
}
// SWIPE EVENTS
document.addEventListener('swiped-up', function(e) { document.onkeydown({key: 'ArrowUp'})} );
document.addEventListener('swiped-left', function(e) { document.onkeydown({key: 'ArrowLeft'})} );
document.addEventListener('swiped-down', function(e) { document.onkeydown({key: 'ArrowDown'})} );
document.addEventListener('swiped-right', function(e) { document.onkeydown({key: 'ArrowRight'})} );


// BUTTONS
btn_fast_automation.onclick = ()=>{
	if (btn_fast_automation.innerText == "Fast Automation") {
		game.pause_game()
		btn_fast_automation.innerText = "Pause"
		// FAST AUTOMATE
		loading.style.setProperty("visibility", "visible")
		loaded_infos = loaded_infos.concat(game.info)
		game.load_automated_infos();
		
		btn_next_map.disabled = true
		btn_speeder.disabled = true
		btn_collide.disabled = true
		btn_replace.disabled = true
	} else {
		game.pause_game();
		btn_fast_automation.disabled = true
	}
}
btn_pause_auto.onclick = () => {
	if (btn_pause_auto.innerText == "Automate") {
		if (btn_fast_automation.innerText == "Pause") {btn_fast_automation.disabled = true}
		game.pause_game()
		// AUTOMATE THE GAME
		btn_pause_auto.innerText = "Pause"
		game.set_game_interval(()=>{ game.automate() })
		game.info.mode = "automated"
		btn_speeder.disabled = true
	} else {game.pause_game()}
}
btn_next_map.onclick = ()=>{
	game.info.steps = 0
	game.info.score = 0
	game.info.fouls = 0
	if (btn_next_map.innerText == "Random Map") {
		// GETTING RANDOM MAP
		game.get_map("random")
		btn_next_map.innerText = 'Fixed Map'
		btn_collide.innerText = 'Disable Collision'
		btn_collide.click()
		btn_collide.disabled = true
	} else {
		// GETTING FIXED MAP
		game.get_map("fixed")
		btn_next_map.innerText = 'Random Map'
		btn_collide.disabled = false
	}
	game.pause_game()
}
btn_speeder.onclick = () => {
	if (btn_speeder.innerText == 'Slower') {
		// SLOW IT
		game.info.time = game.info.slow_time
		btn_speeder.innerText = 'Faster'
	} else {
		// FAST IT
		game.info.time = game.info.fast_time
		btn_speeder.innerText = 'Slower'
	}
	if (game.info.mode == "automated") {
		game.pause_game()
		btn_pause_auto.click()
	} else if (game.info.mode == "key") {
		game.pause_game()
	}
}
btn_collide.onclick = () => {
	if (btn_collide.innerText == 'Enable Collision') {
		// Enable Collision
		game.info.allowcollisions = 1
		btn_collide.innerText = 'Disable Collision'
	} else {
		// Disable Collision
		game.info.allowcollisions = 0
		btn_collide.innerText = 'Enable Collision'
	}
}
btn_replace.onclick = () => {
	game.info.map[game.info.map.indexOf(2)] = 0
	let r = Math.floor(Math.random() * (31*28))
	while (game.info.map[r] != 0) { r = Math.floor(Math.random() * (31*28)) }
	game.info.map[r] = 2
	game.update_map()
}
btn_guide.onclick = ()=>{
	game.pause_game()
	if (btn_guide.innerText == "Guide") {
		// SHOWING GUIDE
		ins.style.setProperty('display', 'block')
		btn_guide.innerText = "Close"
		btn_fast_automation.disabled = true
		btn_pause_auto.disabled = true
		btn_next_map.disabled = true
		btn_speeder.disabled = true
		btn_collide.disabled = true
		btn_replace.disabled = true
	} else {
		// CLOSING GUIDE
		ins.style.setProperty('display', 'none')
		btn_guide.innerText = "Guide"
		btn_fast_automation.disabled = false
	}
}
document.querySelector("body").style.setProperty("height", `${window.innerHeight}px`)
document.querySelector(":root").style.setProperty(
	"--win_size",
	`${(win_size/100) * ((window.innerHeight < window.innerWidth)? window.innerHeight: window.innerWidth)}px`
)

window.addEventListener("resize", () => {
	document.querySelector("body").style.setProperty("height", `${window.innerHeight}px`)
	document.querySelector(":root").style.setProperty(
		"--win_size",
		`${(win_size/100) * ((window.innerHeight < window.innerWidth)? window.innerHeight: window.innerWidth)}px`
	)
});


