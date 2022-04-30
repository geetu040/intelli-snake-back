class Map {
	constructor() {
		this.game_items = document.getElementsByClassName("game-item")
		this.info = {
			"message": 0,
			"map": 0,
			"map_type": "fixed",
			"score": 0,
			"fouls": 0,
			"parts": 2,
			"allowcollisions": 0,
			"automated": 0,
			"int_var": 0,
			"time": 100,
			"slow_time": 500,
			"fast_time": 100,
			"fast": 1,
			"allow_second_preference": 1,
			"steps": 0,
			"allow_writing": 0,
		}
		this.do("fixed_map")
	}
	do (method) {
		this.info.message = method
		this.report_ajax()
		this.update_map()
		this.update_board()
		this.guide('close')
	}
	report_ajax() {
		let returned = $.ajax({
			url: '/remap',
			dataType: 'json',
			async: false,
			data: {"data": JSON.stringify(this.info)},
		});
		this.info = JSON.parse(returned['responseText'])
		
	}
	update_map() {
		for (let i=0; i<rows*cols; i++) {
			this.game_items[i].classList.remove('wall')
			this.game_items[i].classList.remove('empty')
			this.game_items[i].classList.remove('food')
			this.game_items[i].classList.remove('head')
			this.game_items[i].classList.remove('body')
			switch (this.info.map[i]) {
				case 0:
					this.game_items[i].classList.add("empty")
					break;
				case 1:
					this.game_items[i].classList.add("wall")
					break;
				case 2:
					this.game_items[i].classList.add("food")
					break;
				case 3:
					this.game_items[i].classList.add("head")
					break;
				default:
					this.game_items[i].classList.add("body")
					break;
			}
		}
	}
	update_board() {
		score_span.innerText = this.info.score
		fouls_span.innerText = this.info.fouls
		steps_span.innerText = this.info.steps
	}
	// GUIDE BUTTON
	guide(msg=null) {
		if (msg === 'close'){ ins.style.setProperty('display', 'none')}
		else if (msg == null) {
			if (getComputedStyle(ins).getPropertyValue('display') == 'block') {
				ins.style.setProperty('display', 'none')
			} else {
				ins.style.setProperty('display', 'block')
				this.pause_auto(msg='pause')
			}
		}
	}
	// MAP BUTTON
	next_map() {
		this.guide('close')
		this.pause_auto('pause')
		if (this.info.map_type == "fixed") {
			btn_next_map.innerText = "Fixed Map"
			this.info.map_type = "random"
			map.do("random_map")
			// disabling collision random map
			map.info.allowcollisions = 1
			map.collide()
			btn_collide.disabled = true
		} else {
			this.info.map_type = "fixed"
			btn_next_map.innerText = "Random Map"
			map.do("fixed_map")
			// allowing collision button on fixed map
			btn_collide.disabled = false
		}
	}
	// SPEED BUTTON
	speeder() {
		this.guide('close')
		if (this.info.fast == 1) {
			this.info.fast = 0
			this.info.time = this.info.slow_time
			btn_speeder.innerText = "Faster"
		} else {
			this.info.fast = 1
			this.info.time = this.info.fast_time
			btn_speeder.innerText = "Slower"
		}
		this.pause_auto("pause")
		this.pause_auto("automate")
	}
	// COLLISION BUTTON
	collide() {
		this.guide('close')
		if (this.info.allowcollisions == 1) {
			this.info.allowcollisions = 0
			btn_collide.innerText = "Enable Collision"
		} else {
			this.info.allowcollisions = 1
			btn_collide.innerText = "Disable Collision"
		}
	}
	// AUTOMATE BUTTON
	pause_auto(msg=NaN) {
		if (msg == 'automate') {
			this.info.automated = 0
		} else if (msg == 'pause') {
			this.info.automated = 1
		}
		if (this.info.automated == 0) {
			btn_pause_auto.innerText = "Pause"
			this.info.automated = 1
			this.info.int_var = setInterval(
				()=>{this.do("move_model")},
				this.info.time
			)
		} else {
			btn_pause_auto.innerText = "Automate"
			this.info.automated = 0
			clearInterval(this.info.int_var)
		}
	}
}

let map = new Map()

document.onkeydown = (key)=>{
	if (key.key == 'Enter' && map.info.allow_writing) {
		map.do('write')
	} else if (key.key == " " && map.info.allow_writing) {
		map.do('clean')
	} else if (key.key == "0") {
		map.do('move_model')
	} else if (key.key.slice(0, 5) == 'Arrow') {
		map.do('keyboard_move_' + key.key.slice(5, 6).toLowerCase())
	} else {
		switch (key.key.toLowerCase()) {
			case 'w':
				map.do("food_move_" + "u")
				break;
			case 'a':
				map.do("food_move_" + "l")
				break;
			case 's':
				map.do("food_move_" + "d")
				break;
			case 'd':
				map.do("food_move_" + "r")
				break;
			default:
				break;
		}
	}
}