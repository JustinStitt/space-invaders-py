import sys
import pygame
import glob
import re

class Explosion:
    def __init__(self, name='explosion', path='explosion/', game=None, speed = 5, pos = (10,10), alien=None):
        self.game = game
        self.alien = alien
        self.name = name # name of sprties ex: explosion0 -> explosion 1 -> etc.
        self.path = path # folder that sprites are in
        self.sprites = self.load_sprites()
        self.speed = speed
        self.state = 0 # starting anim state
        self.num_states = len(self.sprites)
        self.pos = pos
        self.frame = 0

    def load_sprites(self):
        sprites = []
        for filename in glob.glob(f'./assets/explosion/*.png'):
            sp = pygame.image.load(f'{filename}')
            sprites.append(sp)
        return sprites

    def render(self):
        sprite = self.sprites[self.state]
        self.game.screen.blit(sprite, (*self.pos, 25, 25))
    
    def update(self):
        if self.frame % self.speed == 0:
            self.state += 1
            if self.state == self.num_states - 1: 
                self.alien.cleanup=True
                self.state = 0
        self.frame += 1