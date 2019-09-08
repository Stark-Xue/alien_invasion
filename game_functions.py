import sys
import pygame
from time import sleep

from Bullet import Bullet
from alien import Alien

def check_keydown_events(event, ai_settings, screen, ship, bullets):
	if event.key == pygame.K_RIGHT:
		#向右移动飞船
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		fire_bullet(ai_settings, screen, ship, bullets)
	elif event.key == pygame.K_q:
		sys.exit()	
		
def check_keyup_events(event, ship):
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False		

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
	"""监视键盘事件和鼠标事件"""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen, ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens,
				bullets, mouse_x, mouse_y)
	
def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens,
		bullets, mouse_x, mouse_y):
	"""玩家单击按钮开始游戏"""
	botton_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if botton_clicked and not stats.game_active:
		#重置游戏设置
		ai_settings.initialize_dynamic_settings()
		
		#隐藏光标
		pygame.mouse.set_visible(False)
		
		#重置游戏统计信息
		stats.reset_stats()
		stats.game_active = True 	
		
		#重置计分牌信息
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()
		sb.prep_ships()
		
		#子弹和外星人清空
		aliens.empty()
		bullets.empty()
		
		#新建一群外星人，新建一艘飞船放置于底部中间
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()			
				
def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets,
		play_button):
	"""更新屏幕上的图像，并切换到新屏幕"""
	#每次循环时都重绘屏幕
	screen.fill(ai_settings.bg_color)	
	for bullet in bullets:
		bullet.draw_bullet()
	ship.blitme()	
	#alien.blitme()
	aliens.draw(screen)
	
	#显示得分
	sb.show_score()
				
	if not stats.game_active:
		play_button.draw_button()
				
	#让最近绘制的屏幕可见
	pygame.display.flip()

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
	"""更新子弹的位置，删除已消失的子弹"""
	#更新子弹的位置
	bullets.update()
		
	#删除已消失的子弹
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
		#print(len(bullets))
		
	check_bullets_aliens_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)	

def check_bullets_aliens_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
	#检查是否有子弹击中类外星人
	#如果是这样，就删除对应的子弹和外星人
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	
	if collisions:
		for alien in collisions.values():
			stats.score += ai_settings.alien_points * len(alien)
			sb.prep_score()
		check_high_score(stats, sb)	
	
	if len(aliens) == 0:
		#删除现有的子弹，并新建一群外星人
		bullets.empty()
		ai_settings.increase_speed()
		stats.level += 1
		sb.prep_level()
		create_fleet(ai_settings, screen, ship, aliens)	

def fire_bullet(ai_settings, screen, ship, bullets):
	"""如果还没有达到限制，就发射一颗子弹"""
	if len(bullets) < ai_settings.bullet_allowed:
		#创建一颗子弹，并将其加入到编组bullets中
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)	

def get_number_alien_x(ai_settings, alien_width):
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_alien_x = int(available_space_x / (2 * alien_width))
	return number_alien_x
	
def get_number_rows(ai_settings, ship_height, alien_height):
	"""计算屏幕可以容耐多少行外星人"""
	available_space_y = ai_settings.screen_height - 3 * alien_height - ship_height
	number_alien_rows = int(available_space_y / (2 * alien_height))
	return number_alien_rows		

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)	

def create_fleet(ai_settings, screen, ship, aliens):
	"""创建外星人群"""
	#创建一个外星人，并计算一行可以容耐多少个外星人
	#外星人之间的间距就是外星人的宽度
	alien = Alien(ai_settings, screen)
	#alien_width = alien.rect.width
	number_alien_x = get_number_alien_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height,
		alien.rect.height)
	
	#创建外星人群
	for number_row in range(number_rows):
		#创建第一行外星人
		for alien_number in range(number_alien_x):
			create_alien(ai_settings, screen, aliens, alien_number,
				number_row)

def check_fleet_edges(ai_settings, aliens):
	"""有外行人到达边缘时采取相应的措施"""
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break
	
def change_fleet_direction(ai_settings, aliens):
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1	
	
def update_aliens(ai_settings, stats, screen, sb, ship, aliens, bullets):
	"""更新外星人群中所有外星人的位置"""
	"""检查是否有外星人位于屏幕边缘"""
	check_fleet_edges(ai_settings, aliens)
	aliens.update()

	#检测外星人和飞船碰撞
	if pygame.sprite.spritecollideany(ship, aliens):
		#print("ship hut!!!")
		ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
		
	#检查是否有外星人到达底部	
	check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)

def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
	#检查是否有外星人到达底部
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			#像处理外星人和飞船相撞一样处理
			ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
			break

def ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets):
	#响应被外星人撞到的飞船
	#将ship_left减1
	if stats.ship_left > 1:
		stats.ship_left -= 1
		
		#更新计分牌
		sb.prep_ships()
		
		#子弹和外星人清空
		aliens.empty()
		bullets.empty()
		
		#新建一群外星人，新建一艘飞船放置于底部中间
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
		
		#暂停0.5秒
		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)

def check_high_score(stats, sb):
	"""检查是否诞生类最高分"""
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()
