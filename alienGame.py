'''
Alien Game
Made by Justin Stitt and Amanda Acaba
2/8/2022
'''
import pygame
import sys
import os
import math
from random import randrange


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
        self.keys = self.define_keys()
        self.border_buffer = 4 # buffer around edges of screen to stop sprites melting
        self.to_add = []
        pygame.font.init()
        self.font = pygame.font.SysFont('Impact', (self.width+self.height)//40)
        self.background_img = pygame.image.load('./assets/background.jpg')
        self.background_img = pygame.transform.scale(self.background_img, (self.width, self.height))

    def set_player(self, player):
        self.player = player
    
    def damage_player(self, amount=1):
        print(f'dealing {amount} damage to player')

    def add_object(self, obj):
        #self.entities.add(obj)
        self.to_add.append(obj)
        obj.assign_game_instance(self)

    def draw_text(self, message, pos=(0,0)):
        text_surface = self.font.render(message, False, (244,199,244))
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.player.parse_keyboard_input(pygame.key.get_pressed())
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

    def render(self):
        #self.screen.fill(self.background_color)
        self.screen.blit(self.background_img, (0,0))
        for entity in self.entities:
            entity.render(self.screen)

        self.draw_text(f'score = {self.score}', 
                            pos=(self.width//25, self.height-self.height//15))
        #self.draw_text(f'(debug)\nTotal Objects: {len(self.entities)}', 
        #                    pos=(self.width-self.width//2, self.height-self.height//15))
        #print(f'{self.entities=}')
        pygame.display.flip()

    def play(self):
        self.update()
        self.render()

class Entity:
    def __init__(self, pos=[0,0], velocity=[0,0], size=[0,0], 
                        color=(255,0,255), sprite=None, scale=0., speed=0.):
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

    def move(self):
        if self.velocity == [0, 0]: return
        self.rect.centerx += self.velocity[0]
        self.rect.centery += self.velocity[1]

    def update(self):
        self.move()
        self.collision_logic()
    
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
    def __init__(self, pos=[0,1000], sprite=None, scale=.2, speed=8.):
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

    def shoot(self):
        laser = Laser()
        self.game.add_object(laser)
        npos = [self.rect.centerx, self.rect.centery - self.rect[3]/3]
        laser.update_pos(npos)

class Laser(Entity):
    def __init__(self, pos=[0,0], speed=1.5, velocity=[0,-1], size=[30,40], scale=.05, ratio=.15, acceleration=.15):
        super().__init__(pos=pos, speed=speed, velocity=velocity[:], size=size, scale=scale)
        self.acceleration = acceleration
        self.velocity[0] *= speed
        self.velocity[1] *= speed
        self.ratio = ratio
        self.alive = 75

    def update(self):
        super().update()
        self.velocity[0] *= 1.+self.acceleration
        self.velocity[1] *= 1.+self.acceleration
        self.alive -= 1
        if self.alive < 0: self.cleanup = True

    def load_sprite(self, sprite):
        sp = super().load_sprite(sprite=sprite)
        sp_rect = sp.get_rect()
        sp = pygame.transform.scale(sp, (sp_rect[2]*self.ratio, sp_rect[3]*1.)) 
        return sp

    def collision_logic(self):
        collisions = self.collides()
        for cobj in collisions:
            if isinstance(cobj, Entity):
                pass
                #print(f'{type(self)} hit {type(cobj)}')
            if isinstance(cobj, Alien):
                cobj.beat()

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
    def __init__(self, pos=[0,0], scale=0.1, sprite='alien', velocity=[0., 0.], fleet=[], is_laser=False):
        super().__init__(pos=pos, scale=scale, sprite=sprite, velocity=velocity)
        self.fleet = fleet
        self.can_damage = True
        self.is_laser = is_laser

    def beat(self):
        self.game.score += 1
        self.cleanup = True
        if self in self.fleet:
            self.fleet.remove(self)

    def update(self, able=False):
        if not able: return
        super().update()
        self.check_damage()

    def bounce(self):
        self.velocity[0] *= -1;

    def collides_with_player(self):
        player = self.game.player
        if player is None: return
        collides = self.collides()
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
    def __init__(self, pos=[0,0], velocity=[-7.,0.], n=5, laser_chance=.15):
        super().__init__(pos=pos[:], velocity=velocity[:])
        self.n = n
        self.fleet = []
        self.laser_chance = laser_chance * 100.
    
    def spawn_fleet(self, velocity=[-10., 0.], pos=[0.,0.]):
        for x in range(self.n):
            new_alien = Alien(velocity=velocity[:])
            new_alien.scale = new_alien.scale / self.n * 7
            r = randrange(100)
            if r < self.laser_chance:
                new_alien.sprite = "zombie-alien"
                new_alien.is_laser = True
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


def main():
    g = Game()
    s = Ship(sprite='ship',scale=.1)
    g.add_object(s)    
    g.set_player(s)
    spawner = Spawner(to_spawn=AlienFleet, velocity=[-2.0,0.], n = 10)
    g.add_object(spawner)

    while True:
        g.play()

if __name__ == '__main__':
    main()
