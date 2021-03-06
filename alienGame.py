'''
Alien Game
Made by Justin Stitt and Amanda Acaba
2/8/2022
'''
from landingPage import LandingPage
from explosion import Explosion
import pygame
import sys
import os
import math
from random import randrange, choice


class Game:
    def __init__(self):
        self.width, self.height = (800, 800)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Alien Game")
        self.background_color = (42,42,42)
        self.player = None
        self.score = 0
        self.entities = set()
        self.clock = pygame.time.Clock()
        self.frame_rate = 30
        self.frame = 0
        self.keys = self.define_keys()
        self.border_buffer = 4 # buffer around edges of screen to stop sprites melting
        self.to_add = []
        pygame.font.init()
        self.font = pygame.font.SysFont('Impact', (self.width+self.height)//90)
        self.background_img = pygame.image.load('./assets/background.jpg')
        self.background_img = pygame.transform.scale(self.background_img, (self.width, self.height))
        self.running = True
        self.landing_page = None
        self.on_landing = True
        self.laser_sound = pygame.mixer.Sound('assets/lasersound.mp3')
        self.explosion_sound = pygame.mixer.Sound('assets/explosionsound.wav')
        self.highscore_file = open('./assets/highscores.txt', 'a+')
        self.aliens = [['alien', 'alien2', 'alien3', 'alien4', 'alien5'], ['GreenAlien', 'RedAlien'], ['zombie-alien', 'zombie2'], ['ufo', 'ufo1']]

    def set_player(self, player):
        self.player = player
    
    def damage_player(self, amount=1):
        self.player.lives -= amount
        if(self.player.lives <= 0):
            self.draw_text(f'YOU LOST!', 
                            pos=(self.width//7, self.height//4), font_size=(self.width+self.height)//10)
            if not self.highscore_file.closed:
                self.highscore_file.write(f'{self.score}\n')
                self.highscore_file.close()
            pygame.display.flip()
            self.running = False

    def add_object(self, obj):
        #self.entities.add(obj)
        self.to_add.append(obj)
        obj.assign_game_instance(self)

    def draw_text(self, message, pos=(0,0), color=(244,199,244), font_size=40):
        font = pygame.font.SysFont('Impact', font_size)
        text_surface = font.render(message, False, color)
        self.screen.blit(text_surface, pos)

    def define_keys(self):
        keys = dict()
        keys['up'] = set([pygame.K_UP, pygame.K_w])
        keys['down'] = set([pygame.K_DOWN, pygame.K_s])
        keys['left'] = set([pygame.K_LEFT, pygame.K_a])
        keys['right'] = set([pygame.K_RIGHT, pygame.K_d])
        keys['shoot'] = set([pygame.K_SPACE])
        return keys

    def update(self):
        self.frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.player.parse_keyboard_input(pygame.key.get_pressed())
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.on_landing: continue
                self.landing_page.parse_mouse_down(event.pos)
            if event.type == pygame.MOUSEMOTION:
                if not self.on_landing: continue
                self.landing_page.parse_mouse_movement(event.pos)

        if self.on_landing: return
        to_clean = []
        for entity in self.entities:
            if entity.cleanup: to_clean.append(entity)
            entity.update()

        for obj in to_clean:
            self.entities.remove(obj)
            del obj

        for obj in self.to_add:
            self.entities.add(obj)
        self.to_add = []
        self.clock.tick(self.frame_rate)
    
    def assign_landing_page(self, lp):
        self.landing_page = lp

    def render(self):
        #self.screen.fill(self.background_color)
        self.screen.blit(self.background_img, (0,0))
        for entity in self.entities:
            entity.render(self.screen)
            if isinstance(entity, Explosion): print(entity)
        self.draw_text(f'score = {self.score}', 
                            pos=(self.width//30, self.height-self.height//10))
        self.draw_text(f'lives = {self.player.lives}', 
                pos=(self.width//30, self.height-self.height//16))
        #print(f'{self.entities=}')
        pygame.display.flip()

    def play(self):
        if self.on_landing:
            self.update()
            self.landing_page.update()
            self.landing_page.render()
            pygame.display.flip()
            return
        self.update()
        if not self.running: return
        self.render()

class Entity:
    def __init__(self, pos=[0,0], velocity=[0,0], size=[0,0], 
                        color=(255,0,255), sprite=None, scale=0., speed=0., shoot_cd=5):
        self.pos = pos 
        self.velocity = velocity 
        self.size = size 
        self.color = color
        self.scale = scale
        self.game = None
        self.sprite = sprite
        self.speed = speed
        self.rect = None
        self.cleanup = False
        self.shoot_cd = shoot_cd
        self.current_cd = self.shoot_cd

    def move(self):
        if self.velocity == [0, 0]: return
        self.rect.centerx += self.velocity[0]
        self.rect.centery += self.velocity[1]

    def update(self):
        self.collision_logic()
        self.move()
        if self.current_cd > 0:
            self.current_cd -= 1
    
    def update_pos(self, npos):
        self.rect.centerx = npos[0]
        self.rect.centery = npos[1]

    def render(self, screen):
        if self.sprite is None:
            pygame.draw.rect(screen, self.color, self.rect)
            return
        screen.blit(self.sprite, self.rect)
        # draw center
        #pygame.draw.rect(screen, (0,0,255), (self.rect.centerx, self.rect.centery, 50, 50))
        #pygame.draw.rect(screen, (0,0,255), self.rect, width = 2)
  
    def assign_game_instance(self, game):
        self.game = game
        self.sprite = self.load_sprite(self.sprite)
        rect = self.sprite.get_rect() 
        self.rect = pygame.Rect(*self.pos, *rect[2:])

    def load_sprite(self, sprite, ext='png'):
        if sprite is None: sprite = 'default'
        sp = pygame.image.load(f'assets/{sprite}.{ext}')
        sp = pygame.transform.scale(sp, (self.game.width*self.scale, self.game.height*self.scale))
        return sp
    
    def shoot(self, dir=-1, acceleration=.15, speed=1):
        if self.current_cd > 0: return
        self.current_cd = self.shoot_cd
        laser = Laser(velocity=[0,dir], acceleration=acceleration, speed=speed)
        if self is self.game.player:
            laser.is_player_owned = True
            laser.color = (0,255,5)
        self.game.add_object(laser)
        npos = [self.rect.centerx, self.rect.centery - self.rect[3]/3]
        laser.update_pos(npos)
        self.game.laser_sound.play()

    def collision_logic(self):
        pass

    def collides(self):
        '''
        return list of objects that self collides with
        '''
        g = self.game
        collisions = []
        for obj in g.entities:
            if obj is self: continue
            if isinstance(obj, Explosion): continue
            collide = self.rect.colliderect(obj.rect)
            if collide: collisions.append(obj)
        return collisions

class Player:
    def __init__(self):
        self.lives = 3

    def parse_keyboard_input(self, keys):
        velo = [0, 0]
        for k, v in self.game.keys.items():
            go = False
            for key in v:
                if keys[key] != False:
                    go = True
            if not go: continue
            
            if k == 'up' and not self.stuck_to_bottom:
                velo[1] = -self.speed
            elif k == 'down':
                velo[1] = self.speed
            elif k == 'right':
                velo[0] = self.speed
            elif k == 'left':
                velo[0] = -self.speed
            elif k == 'shoot':
                self.shoot()

        self.velocity = velo

class Ship(Entity, Player):
    def __init__(self, pos=[200,1000], sprite=None, scale=.2, speed=8.):
        super().__init__(pos=pos, sprite=sprite, scale=scale, speed=speed)
        Player.__init__(self)
        self.stuck_to_bottom = True # can't move from the bottom
    
    def keep_in_bounds(self):
        x, y, w, h = (self.rect.centerx, self.rect.centery, *self.rect[2:])
        g = self.game
        ah = g.height - g.border_buffer
        aw = g.width - g.border_buffer
        if y + h/2 > ah:
            self.rect.centery = ah - h//2
        elif y - h/2 <= g.border_buffer:
            self.rect.centery = g.border_buffer + h//2
        if x + w/2 > aw:
            self.rect.centerx = aw - w//2
        elif x - w/2 <= g.border_buffer:
            self.rect.centerx = g.border_buffer + w//2

    def update(self):
        super().update()
        self.keep_in_bounds()

class Laser(Entity):
    def __init__(self, pos=[0,0], speed=1.5, velocity=[0,1], size=[30,40], scale=.05, ratio=.15, 
                                                        acceleration=.3, dir=1, is_player_owned=False, color=(255,0,0)):
        super().__init__(pos=pos, speed=speed, velocity=velocity[:], size=size, scale=scale)
        self.acceleration = acceleration
        self.velocity[0] *= speed
        self.velocity[1] *= speed
        self.ratio = ratio
        self.is_player_owned = is_player_owned
        self.color = color
        self.can_damage = True

    def update(self):
        super().update()
        self.velocity[0] *= 1.+self.acceleration
        self.velocity[1] *= 1.+self.acceleration
        self.check_remove()

    def load_sprite(self, sprite):
        sp = super().load_sprite(sprite=sprite)
        sp_rect = sp.get_rect()
        sp = pygame.transform.scale(sp, (sp_rect[2]*self.ratio, sp_rect[3]*1.)) 
        sp.fill((*self.color, 100), special_flags=pygame.BLEND_ADD)
        return sp

    def check_remove(self):
        if self.rect[1] < 0: self.cleanup = True
        elif self.rect[1] + self.rect.height > self.game.height: self.cleanup = True

    def collision_logic(self):
        collisions = self.collides()
        if not self.can_damage: return
        for cobj in collisions:
            if isinstance(cobj, Entity):
                pass
                #print(f'{type(self)} hit {type(cobj)}')
            if isinstance(cobj, Alien) and self.is_player_owned == True:
                cobj.beat()
            elif self.is_player_owned == False and isinstance(cobj, Player):
                self.game.damage_player(1)
                self.can_damage = False
                self.cleanup = True
                return
            if isinstance(cobj, BarrierPiece):
                cobj.beat()
                self.cleanup = True
class Spawner(Entity):
    def __init__(self, to_spawn = None, spawn_timer=50, do_spawn=True, game=None, **kwargs):
        super().__init__()
        self.spawn_timer = spawn_timer
        self.do_spawn = do_spawn
        self.ctime = spawn_timer
        self.game = game
        self.to_spawn = to_spawn
        self.kwargs = kwargs

    def update(self):
        if self.game is None: return
        self.ctime -= 1
        if self.ctime <= 0:
            self.spawn()

    def spawn(self):
        #randx = randrange(self.game.width//5, self.game.width-self.game.width//5)
        #randy = randrange(self.game.height//15, self.game.height//2)
        new = self.to_spawn(**self.kwargs)
        self.game.add_object(new)
        if isinstance(new, AlienFleet):
            new.spawn_fleet()
        self.ctime = self.spawn_timer
   
class Alien(Entity):
    def __init__(self, pos=[0,0], scale=0.1, sprite='alien', velocity=[0., 0.], \
                    fleet=[], is_laser=False, shoot_cd=300, value=100):
        super().__init__(pos=pos, scale=scale, sprite=sprite, velocity=velocity)
        self.fleet = fleet
        self.can_damage = True
        self.is_laser = is_laser
        self.shoot_cd = shoot_cd
        self.value = value
        self.anim_timer = randrange(10, 125)
        self.do_anim = True
        self.anim_state = 0
        self.frame = 0
        self.explosion = Explosion(game=self.game, pos=[self.pos[0],self.pos[1]], alien=self)
        self.is_exploding = False
        self.pos_time_of_death = [0 ,0]
        self.do_anim = True
        self.anim_state = 0
        self.anim_timer = randrange(5, 25)
        self.sprite_idx = 0

    def beat(self):
        self.is_exploding = True
        self.pos_time_of_death = [self.rect[0], self.rect[1]]
        self.game.score += self.value
        self.game.explosion_sound.play()
        
    def update(self, able=False):
        if not able: return
        super().update()
        self.check_damage()
        if self.is_laser:
            self.shoot(dir=1, acceleration = 0., speed=10)
        if self.is_exploding:
            self.explosion.game=self.game
            self.explosion.update()
        if self.cleanup:
            self.is_exploding = False
            #del self.explosion
            if self in self.fleet:
                self.fleet.remove(self)
        if self.game.frame % self.anim_timer == 0 and self.do_anim:
            if self.sprite_idx == 0:
                self.sprite = self.load_sprite('alien' if self.anim_state%5 == 0 else f'alien{self.anim_state%5+1}')
            elif self.sprite_idx == 1:
                self.sprite = self.load_sprite('zombie-alien' if self.anim_state%2 == 0 else 'zombie2')
            elif self.sprite_idx == 2:
                self.sprite = self.load_sprite('RedAlien' if self.anim_state%2 == 0 else 'GreenAlien')
            elif self.sprite_idx == 3:
                self.sprite = self.load_sprite('ufo' if self.anim_state%2 == 0 else 'ufo1')
            self.anim_state += 1
    
    def render(self, screen):
        super().render(screen)
        if self.is_exploding:
            self.explosion.game = self.game
            self.explosion.pos=[self.pos_time_of_death[0], self.pos_time_of_death[1]]
            self.explosion.render()

    def bounce(self):
        self.velocity[0] *= -1;

    def collides_with_player(self):
        player = self.game.player
        if player is None: return
        collides = self.collides()
        for collide in collides:
            if isinstance(collide, BarrierPiece):
                self.beat()
                collide.beat()
        if player in collides:
            self.game.damage_player()
            self.can_damage = False
            self.cleanup = True
            return True
        return False

    def check_damage(self):
        if not self.can_damage: return
        if self.collides_with_player(): return
        if self.rect[1] + self.rect.height >= self.game.height:
            for _alien in self.fleet:
                _alien.cleanup = True
                _alien.can_damage = False
            self.game.damage_player(1)

class AlienFleet(Entity):
    def __init__(self, pos=[0,0], velocity=[-7.,0.], n=5, laser_chance=.15, variance=0):
        super().__init__(pos=pos[:], velocity=velocity[:])
        self.n = n
        self.fleet = []
        self.laser_chance = laser_chance * 100.
        self.variance = variance
    
    def spawn_fleet(self, velocity=[-10., 0.], pos=[0.,0.]):
        v = 0 if self.variance <= 0 else randrange(self.variance)
        for x in range(self.n+v):
            new_alien = Alien(velocity=velocity[:])
            new_alien.scale = (new_alien.scale / (self.n+v)) * 7
            r = randrange(100)
            if r < self.laser_chance:
                new_alien.sprite_idx = 1
                new_alien.is_laser = True
                new_alien.value = 300
            elif r < self.laser_chance*2:
                new_alien.sprite_idx = 2
                new_alien.value = 200
            elif r < self.laser_chance*2.2:
                new_alien.sprite_idx = 3
                new_alien.value = choice([100, 200, 300, 400, 500])
            self.game.add_object(new_alien)
            p = new_alien.pos
            new_alien.rect.center = [new_alien.rect.width * x + new_alien.rect.width, p[1] + new_alien.rect.height + 5]
            self.fleet.append(new_alien)
            new_alien.fleet = self.fleet

    def update(self):
        super().update()
        for _alien in self.fleet: _alien.update(able=True)        
        self.check_empty_fleet()
        self.check_bounce()

    def check_empty_fleet(self):
        if len(self.fleet) == 0:
            self.cleanup = True

    def bounce(self):
        for _alien in self.fleet:
            _alien.bounce()
        self.down()
    
    def down(self, levels=1):
        for _alien in self.fleet:
            _alien.rect[1] += _alien.rect.height//2

    def check_bounce(self):
        if self.cleanup == True: return
        lm, rm = (self.fleet[0], self.fleet[-1])
        if lm.rect[0] < 0: self.bounce()
        elif rm.rect[0] + rm.rect.width > self.game.width - 1: self.bounce()


class Barrier(Entity):
    '''
    Barriers can be hit by lasers and their model deteriorates
    '''
    def __init__(self, width=200, height = 100, cell_size = 8, game=None, pos=[100, 550]):
        super().__init__(pos=pos[:])
        self.pieces = []
        self.game = game
        self.make_conglomerate(width, height, cell_size)

    def render(self, screen):
        super().render(screen)
        for piece in self.pieces:
            piece.render(screen)
    
    def make_conglomerate(self, width, height, cell_size):
        r = width // cell_size
        c = height // cell_size
        (x, y) = (self.pos[0], self.pos[1])
        for i in range(r):
            for j in range(c):
                new_piece = (BarrierPiece(color=self.color, cell_size=cell_size,
                                                scale=.5, game=self.game,
                                                  pos=[x+i*cell_size, y+j*cell_size], barrier=self))
                self.game.add_object(new_piece)
                self.pieces.append(new_piece)
                
class BarrierPiece(Entity):
    def __init__(self, cell_size, scale, game, color, pos, barrier=None):
        super().__init__(scale=scale, pos=pos[:])
        self.game = game
        self.color = (randrange(1,255), randrange(1,255), 40)
        self.cell_size = cell_size
        self.rect = None
        self.barrier = barrier
    
    def beat(self):
        if self in self.barrier.pieces:
            self.barrier.pieces.remove(self)
        self.cleanup = True

    def render(self, screen):
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.cell_size, self.cell_size)
        pygame.draw.rect(screen, self.color, (self.rect[0], self.rect[1], self.cell_size, self.cell_size))
        

def main():
    g = Game()
    ls = LandingPage(game=g)
    g.assign_landing_page(ls)
    s = Ship(sprite='ship',scale=.1)
    g.add_object(s)    
    g.set_player(s)
    spawner = Spawner(to_spawn=AlienFleet, velocity=[-2.0,0.], n = 10, variance=0)
    g.add_object(spawner)

    b = Barrier(game=g, width = 100, height = 75, pos=[100, 570])
    b = Barrier(game=g, width = 100, height = 75, pos=[350, 570])
    b = Barrier(game=g, width = 100, height = 75, pos=[600, 570])
    g.add_object(b)


    while True:
        g.play()

if __name__ == '__main__':
    main()
