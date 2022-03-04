import pygame
import glob
import re

class Button:
    def __init__(self, game=None, pos=(0,0), text='', color=(255,0,0), action=None, 
                                width=100, height = 33):
        self.pos = pos
        self.text = text
        self.color = color
        self.hovered_color = (42, 17, 231)
        self.action = action
        self.game = game
        self.width = width
        self.height = height
        self.hovered = False
    
    def render(self):
        pygame.draw.rect(self.game.screen, self.color if not self.hovered else self.hovered_color, (*self.pos, self.width, self.height))
        # draw text inside button
        self.game.draw_text(self.text, self.pos, color=(0,0,0), font_size=20)

class LandingPage:
    def __init__(self, game=None):
        self.game = game
        self.color = (42, 42, 42)
        self.buttons = []
        self.setup_buttons()
        self.do_show_highscores = False
        self.sprites = self.load_alien_images()
        self.anim_state = 0
        self.frame = 0
        self.anim_timer = 100

    def start_game(self):
        print('Starting Game!', flush=True)
        self.game.on_landing = False

    def toggle_do_show_highscores(self):
        self.do_show_highscores = not self.do_show_highscores

    def show_highscores(self):
        if not self.do_show_highscores: return
        self.game.highscore_file.seek(0)
        scores = self.game.highscore_file.readlines()
        x = 0
        start = 50
        spacing = 100
        scores = sorted(scores, key=lambda x : int(x), reverse=True)[:5] # show top 5 highscores
        for line in scores:
            self.game.draw_text(f'{x+1}. {line.rstrip()}', (start + x * spacing, 750), color=(242,199,244), font_size=20)
            x += 1

    def setup_buttons(self):
        start_game = Button(self.game, pos=(275,600), text='Start Game',
                                        color=(14,199,16), action=self.start_game)
        highscores = Button(self.game, pos=(275, 700), text='Highscores', color = (199, 14, 14), action=self.toggle_do_show_highscores)
        self.buttons.append(start_game)
        self.buttons.append(highscores)


    def render(self):
        if not self.game.on_landing: return
        pygame.draw.rect(self.game.screen, self.color, (0,0, self.game.width, self.game.height))
        self.game.draw_text('SPACE INVADERS', pos=(80, 100), font_size=100)
        for button in self.buttons:
            button.render()
        self.draw_alien_images()
        self.show_highscores()
        self.frame += 1
        if self.frame % self.anim_timer == 0:
            self.anim_state += 1

    def buttons_clicked(self, mpos, lim=1):
        clicked = [] # list of buttons clicked (usually just one, det by lim)
        (mx, my) = mpos
        for button in self.buttons:
            (bx, by) = button.pos
            (bw, bh) = (button.width, button.height)
            if mx < bx or mx > bx + bw: continue
            if my < by or my > by + bh: continue
            clicked.append(button)
        return clicked[:lim]

    def parse_mouse_down(self, mpos):
        for button in self.buttons_clicked(mpos):
            button.action()
    
    def parse_mouse_movement(self, mpos):
        (mx, my) = mpos
        for button in self.buttons:
            (bx, by) = button.pos
            (bw, bh) = (button.width, button.height)
            if mx < bx or mx > bx + bw: button.hovered = False; continue
            if my < by or my > by + bh: button.hovered = False; continue
            button.hovered = True
        
    
    def draw_alien_images(self):
        spacing = (self.game.height/len(self.game.aliens)) // 3
        x = 0
        for chunk in self.sprites:
            self.game.screen.blit(chunk[self.anim_state%len(chunk)], (250, 300+ x*spacing, 25, 25))
            self.game.draw_text(f'      = {(x+1)*100} points' if x < len(self.sprites) -1 else '      = ???', pos=(300, 300+x*spacing))
            x += 1

    def load_alien_images(self):        
        sprites = []
        for chunk in self.game.aliens:
            alien_anims = []
            for img in chunk:
                sp = pygame.image.load(f'./assets/{img}.png')
                sp = pygame.transform.scale(sp, (self.game.width*.1, self.game.height*.1))
                alien_anims.append(sp)
            sprites.append(alien_anims)
        return sprites

    def update(self):
        pass