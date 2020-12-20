import pygame
from pygame.locals import *
import random
import os.path
import sys

#see if we can load more than standard BMP
if not pygame.image.get_extended():
	raise SystemExit("Sorry, extended image module required")

# Path 
main_dir = os.path.split(os.path.abspath(__file__))[0]

# Color code 
WHITE = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 128, 
BLUE = 40, 116, 166
LIGHT_BLUE = 174, 214, 241
RED = 176, 58, 46
LIGHT_RED = 245, 183, 177
PICK_GREEN = 131, 216, 165
LEFT = 1
RIGHT = 3

#game constants
VIRUS_ODDS     = 22     #chances a new alien appears
VIRUS_RELOAD   = [1000,30,10,7,5]     #frames between new aliens
# MONEY          = 3000
DAY_RELOAD     = 10     #frames for Day 
END            = 5
row = 6
col = 10

global GAME_OVER
global virusreload

# Initialize game engine 
pygame.init()

#Loop 
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 30)

def load_image(file):
	"loads an image, prepares it for play"
	file = os.path.join(main_dir, 'data', file)
	try:
		surface = pygame.image.load(file)
	except pygame.error:
		raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
	if surface.get_alpha():
		surface = surface.convert_alpha()
	else:
		surface = surface.convert()
	surface.set_colorkey(WHITE)
	return surface

def load_images(*files):
	imgs = []
	for file in files:
		imgs.append(load_image(file))
	return imgs


class dummysound:
	def play(self): pass

def load_sound(file):
	if not pygame.mixer: return dummysound()
	file = os.path.join(main_dir, 'data', file)
	try:
		sound = pygame.mixer.Sound(file)
		return sound
	except pygame.error:
		print ('Warning, unable to load, %s' % file)
	return dummysound()


class Virus(pygame.sprite.Sprite):
	speed = 10
	animcycle = 12
	images = []
	display = None
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		self.random_seed = 10 * random.randint(0, 7)
		self.rect = self.image.get_rect(topleft = (0, 400 + self.random_seed))
		self.row_facing = Virus.speed
		self.col_facing = 0
		self.frame = 0

	def update(self):
		x, y = self.rect.topleft 	
		if 400 > x >= 300 + self.random_seed and y >= 400:
			self.row_facing, self.col_facing = 0, -Virus.speed
		elif 400 > x >= 300 and y <= 270 - self.random_seed:
			self.row_facing, self.col_facing = Virus.speed, 0
		elif x >= 800 + self.random_seed and y <= 270 - self.random_seed:
			self.row_facing, self.col_facing = 0, Virus.speed
		elif x >= 800 + self.random_seed and y >= 570:
			text_surf = pygame.font.Font(None, 115).render("GAME OVER", True, RED)
			text_rect = text_surf.get_rect(center = (500, 300))
			self.display.blit(text_surf, text_rect)
			pygame.display.update()
			pygame.time.wait(2000)
			pygame.quit()
			sys.exit()

			self.kill()
			# game over

		self.rect.move_ip(self.row_facing, self.col_facing)
		self.frame = self.frame + 1
		self.image = self.images[self.frame//self.animcycle%4] # direction을 90도씩 네번 돌려서 구성

class Explosion(pygame.sprite.Sprite):
    defaultlife = 8
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0: self.kill()

class Boom(pygame.sprite.Sprite):
	defaultlife = 12
	images = []
	def __init__(self, actor):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		self.rect = self.image.get_rect(center = actor.rect.center)
		self.life = self.defaultlife

	def update(self):
		self.life = self.life - 1
		if self.life <= 0: self.kill() 

class Shot(pygame.sprite.Sprite):
	speed = 10
	images = []
	def __init__(self, start_rect, x, y):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		self.rect = self.image.get_rect(center=start_rect.center)
		self.row_facing = x  # 얘랑
		self.col_facing = y # 얘를 매번 잘 구성해야함 타워 알고리즘 고민
		self.start_rect = start_rect
		self.temp_x, self.temp_y = self.start_rect.topleft
		self.target_rect = pygame.Rect(self.temp_x + 100 * self.row_facing, self.temp_y + 100 * self.col_facing, 100, 100)
	
	def update(self):
		self.rect.move_ip(self.speed * self.row_facing, self.speed * self.col_facing)
		if not self.start_rect.contains(self.rect) and not self.target_rect.contains(self.rect) \
		and not (self.start_rect.colliderect(self.rect) and self.target_rect.colliderect(self.rect)):
			self.kill()

class Virus_Data(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.Surface((100, 100))
		self.rect = self.image.get_rect(topleft = (x, y))
	


class Cure_Tower(pygame.sprite.Sprite):
	images = []
	display = None
	def __init__(self, level = 0, x = 2, y = 3, viruses = None, virus_data = None):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.level = level
		self.image = self.images[self.level]
		self.attack_speed = 3 - self.level
		self.rect = self.image.get_rect(topleft = (x * 100, y * 100))
		self.frame = 0
		self.virus_data = virus_data
		self.viruses = viruses

	def update(self):
		def f1(x):
			return x[0]
		self.frame += 1
		shoot = self.frame % (self.attack_speed * 5)
		if shoot == 0:
			for virus_exist_place in list(pygame.sprite.groupcollide(self.virus_data, self.viruses, 0, 0).keys())[::-1]:
				x, y = virus_exist_place.rect.topleft 
				if abs(x - self.rect.x) <= 100 and abs(y - self.rect.y) <= 100:
					Shot(self.rect, (x - self.rect.x)/100 , (y - self.rect.y)/100)	# 총알 발사
					break


class Hospital(pygame.sprite.Sprite):
	def __init__(self):
		pass

class Date(pygame.sprite.Sprite):	
	Month = ["January", 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 
	'November', 'December']
	pandemic_day = [(0, 20), (1, 18), (7, 3), (10, 14), (11, 30)] # 최초 감염 : 1월 20일, 1차 유행 : 2월 18일, 2차 유행: 8월 3일, 3차 유행: 11월 unknown
	message = ['Corona Outbreak(January)', '1st Pandemic(Febuary)', '2st Pandemic(August)', 
	'3rd Pandemic(November)', 'Corona is defeated!!']
	phase = 0
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.font = FONT
		self.color = RED
		self.month = 0
		self.day = 1
		self.count = 0
		self.msg = 'READY'
		self.update()
		self.rect = self.image.get_rect(center = (500, 30))
	
	def update(self):
		self.count += 1
		if self.count > DAY_RELOAD:
			self.day += 1
			self.count = 0 
		if self.day > 31:
			self.month += 1
			self.day = 1

		# self.msg = self.Month[self.month] + " " + str(self.day)
		if (self.month, self.day) == self.pandemic_day[self.phase]:
			Date.phase += 1 # stage up
			global virusreload
			virusreload = VIRUS_RELOAD[self.phase]
			self.msg = 'Phase ' + str(self.phase) + ': ' + self.message[self.phase - 1]  
				# alarm!!!
		elif self.day == 1:
			self.msg = self.Month[self.month]
		self.image = self.font.render(self.msg, 0, self.color) 


class Button(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height, callback = None, output = None,
		font = FONT, text = '', text_color = WHITE, image_color = BLUE, 
		image_hover_color = LIGHT_BLUE, image_down_color = PICK_GREEN):
		super().__init__()
		self.image_normal = pygame.Surface((width, height))
		self.image_normal.fill(image_color)
		self.image_hover = pygame.Surface((width, height))
		self.image_hover.fill(image_hover_color)
		self.image_down = pygame.Surface((width, height))
		self.image_down.fill(image_down_color)

		self.image = self.image_normal
		self.rect = self.image.get_rect(topleft = (x, y))
		image_center = self.image.get_rect().center
		text_surf = font.render(text, True, text_color)
		text_rect = text_surf.get_rect(center = image_center)

		self.image_normal.blit(text_surf, text_rect)
		self.image_hover.blit(text_surf, text_rect)
		self.image_down.blit(text_surf, text_rect)

		self.callback = callback
		self.button_down = False
		self.output = output

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(pygame.mouse.get_pos()):
				self.image = self.image_normal
				return self.output
	
		elif event.type == pygame.MOUSEMOTION:
			collided = self.rect.collidepoint(pygame.mouse.get_pos())
			if collided:
				self.image = self.image_hover
			elif not collided:
				self.image = self.image_normal

class Scene:
	# disply : (1000, 600)
	def __init__(self, display = None):
		self.display = display

	def set_display(self, display):
		self.display = display

	def handle_event(self, event):
		pass
	def draw(self):
		pass
	def update(self):
		pass

class MainScene(Scene):	
	def __init__(self, display = None, width = 300, height = 80):
		super().__init__(display)
		self.width = width
		self.height = height
		self.buttons = pygame.sprite.Group()
		self.play_button = Button(
			x = 100, y = 400, width = self.width, height = self.height,
			output = 'Game', text = 'Play' 
			)
		self.howtoplay_button = Button(
			x = 600, y = 400, width = self.width, height = self.height, 
			output = 'HowToPlay', text = 'HowToPlay', image_color = RED,
			image_hover_color = LIGHT_RED
			)
		self.buttons.add(self.play_button, self.howtoplay_button)

	def handle_event(self, event):
		for button in self.buttons:
			output = button.handle_event(event)
			if output is not None:
				return output

	def draw(self):
		self.display.fill(BLACK)
		# Write title
		TitleText = pygame.font.Font(None, 115)
		TitleSurf = TitleText.render('Corona Defense', True, WHITE)
		TitleRect = TitleSurf.get_rect(center = (500, 250))
		self.display.blit(TitleSurf, TitleRect)
		self.buttons.draw(self.display)

class GameScene(Scene):
	def __init__(self, display = None, virus_path = None, tower_available = None, n_rows = 6, n_cols = 10, CELL_SIZE = 100):
		super().__init__(display)
		self.n_rows = n_rows
		self.n_cols = n_cols
		self.CELL_SIZE = CELL_SIZE
		
		# Initialize Game Groups
		self.viruses = pygame.sprite.Group()
		self.shots = pygame.sprite.Group()
		self.towers = pygame.sprite.Group()
		self.virus_data = pygame.sprite.Group()
		self.all = pygame.sprite.RenderUpdates()
		self.background = pygame.Surface((1000, 600))
		self.background.blit(pygame.transform.scale(load_image('background_small.png'), (1000, 600)) ,(0, 0))
		self.virus_path = virus_path
		self.tower_available = tower_available
		self.money = 3000
		self.cost = [300, 1000, 2500]
		self.hospital_icon = [pygame.transform.scale(load_image('hospital1.png'), (50, 50)), 
		pygame.transform.scale(load_image('hospital2.png'), (50, 50)),
		pygame.transform.scale(load_image('hospital3.png'), (50, 50))]
		self.hospital_state = 0
		# Assign default groups to each sprite class
		Virus.display = display
		Virus.containers = self.viruses, self.all
		Shot.containers = self.shots, self.all
		Cure_Tower.containers = self.towers, self.all
		Virus_Data.containers = self.virus_data
		Explosion.containers = self.all
		Date.containers = self.all
		
		for column_index in range(self.n_cols):
			for row_index in range(self.n_rows):
				if(self.virus_path[column_index][row_index]):
					Virus_Data(column_index * CELL_SIZE, row_index * CELL_SIZE)  

		# Virus() # note, this 'lives' because it goes into a sprite group
		# Cure_Tower(viruses = self.viruses, virus_data = self.virus_data)

		if pygame.font:
			self.all.add(Date())
	

	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if self.hospital_state >= 1:
				self.hospital_icon[self.hospital_state - 1].set_alpha(255)
			if event.key == pygame.K_SPACE:
				return 'Main'
			elif event.key == pygame.K_1:
				if self.money >= self.cost[0]:
					self.hospital_state = 1
			elif event.key == pygame.K_2:
				if self.money >= self.cost[1]:
					self.hospital_state = 2
			elif event.key == pygame.K_3:
				if self.money >= self.cost[2]:
					self.hospital_state = 3
			else:
				self.hospital_state = 0
		elif event.type == pygame.MOUSEBUTTONDOWN:
			x, y = pygame.mouse.get_pos()
			if self.hospital_state >= 1:
				self.hospital_icon[self.hospital_state - 1].set_alpha(255)
				if self.tower_available[x//100][y//100] and self.money >= self.cost[self.hospital_state - 1]:
					self.money -= self.cost[self.hospital_state - 1]
					Cure_Tower(level = self.hospital_state - 1, x = x//100, y = y//100,
						viruses = self.viruses, virus_data = self.virus_data)
			self.hospital_state = 0


	def draw(self):
		self.display.blit(self.background, (0, 0))
		for column_index in range(self.n_cols):
			for row_index in range(self.n_rows):
				if(self.virus_path[column_index][row_index]):
					continue  
				pygame.draw.rect(self.display, WHITE, 
	            	pygame.Rect(column_index * self.CELL_SIZE, 
	            		row_index * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE), width = 1)
		subText = pygame.font.Font(None, 20)
		subSurf = subText.render('Money: ' + str(self.money), True, RED)
		subRect = subSurf.get_rect(topleft = (20, 10))
		self.display.blit(subSurf, subRect)
		self.display.blit(self.hospital_icon[0], (0, 50))
		subText = pygame.font.Font(None, 20)
		subSurf = subText.render('300 (Press ’1’ & Click)', True, RED)
		subRect = subSurf.get_rect(topleft = (50, 70))
		self.display.blit(subSurf, subRect)
		self.display.blit(self.hospital_icon[1], (0, 110))
		subText = pygame.font.Font(None, 20)
		subSurf = subText.render('1000 (Press ’2’ & Click)', True, RED)
		subRect = subSurf.get_rect(topleft = (50, 130))
		self.display.blit(subSurf, subRect)
		self.display.blit(self.hospital_icon[2], (0, 170))
		subText = pygame.font.Font(None, 20)
		subSurf = subText.render('2500 (Press ’3’ & Click)', True, RED)
		subRect = subSurf.get_rect(topleft = (50, 190))
		self.display.blit(subSurf, subRect)
		
		x, y = pygame.mouse.get_pos()
		if self.hospital_state >= 1 and self.tower_available[x//100][y//100]:
			self.hospital_icon[self.hospital_state - 1].set_alpha(150)
			self.display.blit(pygame.transform.scale(self.hospital_icon[self.hospital_state - 1], (100, 100)),
			 (x//100 * 100, y//100 * 100))

		self.all.clear(self.display, self.background)
		
		#update all the sprites
		self.all.update()

		# Create new virus
		global virusreload
		if virusreload:
			virusreload = virusreload - 1
		else:
			# elif not int(random.random() * VIRUS_ODDS): # random.random = 0.0 ~ 1.0
			Virus()
			virusreload = VIRUS_RELOAD[Date.phase]

		# Detect collisions
		for virus in pygame.sprite.groupcollide(self.viruses, self.shots, 1, 1).keys():
			# boom_sound.play()
			Explosion(virus)
			self.money += 100
			# Explosion(shots)


		#draw the scene

		dirty = self.all.draw(self.display)
		return dirty

class HowToPlayScene(Scene):
	def __init__(self, display, img):
		super().__init__(display)
		self.img = img

	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				return 'Main'

	def draw(self):
		self.display.fill(BLACK)
		self.display.blit(self.img, (0, 0))


def main(n_rows = 6, n_cols = 10, block_size = 100):
	display = pygame.display.set_mode((1000, 600))

	if pygame.mixer and not pygame.mixer.get_init():
		print ('Warning, no sound')
		pygame.mixer = None
	#Load images, assign to sprite classes
	#(do this before the classes are used, after screen setup)
	img = pygame.transform.scale(load_image('virus.png'), (30, 30))
	Virus.images = [img, pygame.transform.rotate(img, 90), pygame.transform.rotate(img, 180),pygame.transform.rotate(img, 270)]
	img = pygame.transform.scale(load_image('explosion.png'), (30, 30))
	Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
	Boom.images = [pygame.transform.scale(load_image('explosion.png'), (80, 60))]
	Shot.images = [pygame.transform.scale(load_image('bulletcircle.png'), (50, 50))]
	Cure_Tower.images = [pygame.transform.scale(load_image('hospital1.png'), (100, 100)), 
	pygame.transform.scale(load_image('hospital2.png'), (100, 100)),
	pygame.transform.scale(load_image('hospital3.png'), (100, 100))]

	# Set basic display property
	pygame.display.set_caption('Corona Defense')        
	howtoplay_img = pygame.transform.scale(load_image('howtoplay.jpg'), (1000, 600))
	# Logic map
	virus_path = [[True if(row_index == 4 and column_index <= 2 or 
				column_index == 3 and 2 <= row_index <= 4 or 
				4 <= column_index <= 8 and row_index == 2 or
				column_index == 8 and 3 <= row_index <= 5) else False for row_index in range(row)] for column_index in range(col)]

	tower_available = [[True if((row_index == 3 and column_index <= 1 or 
				column_index == 2 and 1 <= row_index <= 3or 
				3 <= column_index <= 9 and row_index == 1 or
				column_index == 9 and 2 <= row_index <= 5) or 
				(row_index == 5 and column_index <= 3 or 
					column_index == 4 and 3 <= row_index <= 5 or 
					5 <= column_index <= 7 and row_index == 3 or
					column_index == 7 and 4 <= row_index <= 5))

					else False for row_index in range(row)] for column_index in range(col)]
	scenes = {'Main': MainScene(display), 'Game': GameScene(display = display, virus_path = virus_path, tower_available = tower_available), 
	'HowToPlay': HowToPlayScene(display, howtoplay_img)}
	scene = scenes['Main']

	GAME_OVER = True
	global virusreload
	virusreload = VIRUS_RELOAD[0]

	while True:
		dirty = None
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			
			conversion = scene.handle_event(event)
			
			# If not None, change scene
			if conversion is not None:
				scene = scenes[conversion]

		dirty = scene.draw()
		if type(scene) == GameScene and dirty is not None:
			pygame.display.update()
			pygame.display.update(dirty)
		else:
			pygame.display.update()

		clock.tick(10)


	pygame.time.wait(1000)
	pygame.quit()


if __name__ == '__main__':
	main()