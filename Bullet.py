import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
	"""管理飞船发射的子弹的类"""
	
	def __init__(self, ai_settings, screen, ship):
		"""在飞船所处的位置创建一个子弹对象"""
		super().__init__()
		self.screen = screen
		
		#在(0, 0)处创建一个表示子弹的矩形，再设置子弹的正确位置
		self.rect = pygame.Rect(0, 0, ai_settings.bullet_width,
			ai_settings.bullet_height)
		self.rect.centerx = ship.rect.centerx
		self.rect.top = ship.rect.top
		
		#将子弹的位置存储为小数
		self.y = float(self.rect.y)
		
		self.color = ai_settings.bullet_color
		self.speed_factor = ai_settings.bullet_speed_factor
		
	def update(self):
		"""向上移动子弹"""
		#更新表示子弹位置的小数值
		self.y -= self.speed_factor
		#更新表示子弹的rect的值
		self.rect.y = self.y
		
	def draw_bullet(self):	
		pygame.draw.rect(self.screen, self.color, self.rect)
