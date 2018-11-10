
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import ListProperty, ObjectProperty
from kivy.graphics import *
from kivy.animation import Animation#, AnimationTransition
from kivy.config import Config#, ConfigParser
from kivy.clock import Clock
import copy
import random

# random comment



class RootWidget(FloatLayout):

    def __init__(self, basex, basey, height, width, pixel, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(1, 1, 1)
            self.background = Rectangle(pos = (basex-1, basey-1),
                                        size = (width * pixel + 2, height * pixel + 2))

        field = self.add_widget(FieldWidget(basex, basey, height, width, pixel))
        keyboard = self.add_widget(MyKeyboardListener())



class FieldWidget(FloatLayout):

    kbContainer = ObjectProperty()

    def __init__(self, basex, basey, height, width, pixel, **kwargs):
        super(FieldWidget, self).__init__(**kwargs)

        self.grid_height = height
        self.grid_width = width
        self.grid_size = pixel
        self.grid_x = basex
        self.grid_y = basey

        self.colors = [(.95, .95, .95), (.9, .5, .5), (.5, .5, .9), (.5, .9, .5), (.9, .9, .5), (.9, .5, .9), (.5, .9, .9)]

        self.blocks = []
        self.blocks_iscurrent = []
        for i in range(self.grid_height):
            self.blocks.append([])
            self.blocks_iscurrent.append([])
            for j in range(self.grid_width):
                self.blocks[i].append(0)
                self.blocks_iscurrent[i].append([False])

        self.score = 0
        self._init_graphics()

        self.next_block = Block(int(self.grid_width / 2), self.grid_height - 1, random.randrange(1, 6), random.randrange(1, len(self.colors)))
        self.new_block()

        MyKeyboardListener()._keyboard.bind(on_key_down = self.on_keyboard_down)


    def _init_graphics(self):
        with self.canvas.before:
            for i in range(self.grid_height):
                for j in range(self.grid_width):
                    Color(*self.colors[0])
                    Rectangle(pos = (self.grid_x + self.grid_size * j + 1,
                                     self.grid_y + self.grid_size * i + 1),
                              size = (self.grid_size - 2, self.grid_size - 2))

        self.blocks_rect = []
        self.blocks_col = []
        with self.canvas:
            for i in range(self.grid_height):
                self.blocks_rect.append([])
                self.blocks_col.append([])
                for j in range(self.grid_width):
                    self.blocks_col[i].append(Color(*self.colors[self.blocks[i][j]]))
                    self.blocks_rect[i].append(Rectangle(pos = (self.grid_x + self.grid_size * j + 1,
                                                                self.grid_y + self.grid_size * i + 1),
                                                         size = (self.grid_size - 2, self.grid_size - 2)))

        self.next_block_x = self.grid_x + (self.grid_width + 1) * self.grid_size
        self.next_block_y = self.grid_y + self.grid_height * self.grid_size - 100
        with self.canvas.before:
            Color(0.2, 0.2, 0.2)
            Rectangle(pos = (self.next_block_x, self.next_block_y), size = (self.grid_size * 4, self.grid_size * 4))
        self.next_block_rect = []
        with self.canvas:
            self.next_block_col = Color(0,0,0)
            for i in range(4):
                self.next_block_rect.append([])
                for j in range(4):
                    self.next_block_rect[i].append(0)

        self.score_x = self.next_block_x
        self.score_y = self.next_block_y - 20
        self.score_label = Label(text = 'score: 0', pos_hint = {'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.score_label)


    def completed_lines(self, dur):
        """ returns the number of completed lines """
        stack = 0
        for y in range(self.grid_height):
            completed = True
            for x in range(self.grid_width):
                if(self.blocks[y][x] == 0):
                    completed = False

            if completed:
                for j in range(self.grid_width):
                    self.blocks[y][j] = 0
                    anim = Animation(a = 0, duration = dur, t = 'out_cubic')
                    anim.start(self.blocks_col[y][j])
                stack += 1
            elif stack:
                for j in range(self.grid_width):
                    self.blocks[y - stack][j] = self.blocks[y][j]
                    if self.blocks[y][j]:
                        anim = Animation(pos = (self.grid_x + self.grid_size * j + 1,
                                                self.grid_y + self.grid_size * (y - stack) + j),
                                         duration = dur,
                                         t = 'out_bounce')
                        anim.start(self.blocks_rect[y][j])
        self.score += stack
        self.score_label.text = 'score: {0}'.format(self.score)
        return stack


    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.current_block:
            if keycode[1] == 'up':
                self.rotate(self.current_block)
            elif keycode[1] == 'right':
                self.move(self.current_block, dx=1)
            elif keycode[1] == 'left':
                self.move(self.current_block, dx=-1)
            elif keycode[1] == 'down':
                self.move(self.current_block, dy=-1)
            '''
            elif keycode[1] == 'c':
                self.next_block = Block(int(self.grid_width / 2), self.grid_height - 1, 2, random.randrange(1, len(self.colors)))
                self._update_graphics_next_block(self.next_block)
            '''


    def new_block(self):
        self.current_block = self.next_block
        if self.collide_check(self.current_block):
            popup = Popup(title = 'game over', content = Label(text = 'score: {0}'.format(self.score)), size_hint = (None, None), size = (400, 400))
            popup.open()
        self._update_current_block(Block(0, 0, 0, 0), self.current_block)
        self.next_block = Block(int(self.grid_width / 2), self.grid_height - 1, random.randrange(1, 6), random.randrange(1, len(self.colors)))
        self._update_graphics_next_block(self.next_block)
        self.current_block_moveschedule = Clock.schedule_interval(lambda dt: self.move(self.current_block, dy=-1), 0.5)


    def rotate(self, block):
        old = copy.deepcopy(block)
        for y in range(4):
            for x in range(4):
                block.current[x][3-y] = old.current[y][x]
        if self.collide_check(block):
            for y in range(4):
                for x in range(4):
                    block.current[y][x] = old.current[y][x]
        else:
            self._update_current_block(old, block)


    def move(self, block, dx=0, dy=0):
        old = copy.deepcopy(block)
        block.x += dx
        block.y += dy
        if not self.collide_check(block):
            self._update_current_block(old, block)
            return True
        else:
            block.x -= dx
            block.y -= dy
            if dx == 0 and dy == -1:
                self.solidify(block)
                self.current_block = None
                self.current_block_moveschedule.cancel()
                if self.completed_lines(1):
                    Clock.schedule_once(lambda dt: self.new_block(), 1)
                else:
                    self.new_block()
            return False


    def solidify(self, block):
        for i in range(4):
            for j in range(4):
                ry = block.y+1-i
                rx = block.x-1+j
                if block.current[i][j] and 0 <= rx < self.grid_width and 0 <= ry < self.grid_height:
                    self.blocks[ry][rx] = block.color
                    self.blocks_iscurrent[ry][rx] = False
        self._update_graphics_field()


    def collide_check(self, block):
        for i in range(4):
            for j in range(4):
                ry = block.y+1-i
                rx = block.x-1+j
                if block.current[i][j]:
                    if ry < 0 or ry >= self.grid_height or rx < 0 or rx >= self.grid_width:
                        return True
                    if self.blocks[ry][rx] and not self.blocks_iscurrent[ry][rx]:
                        return True
        return False


    def _update_current_block(self, old, new):
        """ old, new : before and after block changed """
        for i in range(4):
            for j in range(4):
                ry = old.y+1-i
                rx = old.x-1+j
                if 0 <= ry < self.grid_height and 0 <= rx < self.grid_width:
                    if old.current[i][j]:
                        self.blocks[ry][rx] = 0
                        self.blocks_iscurrent[ry][rx] = False
        for i in range(4):
            for j in range(4):
                ry = new.y+1-i
                rx = new.x-1+j
                if 0 <= ry < self.grid_height and 0 <= rx < self.grid_width:
                    if new.current[i][j]:
                        self.blocks[ry][rx] = new.color
                        self.blocks_iscurrent[ry][rx] = True
        self._update_graphics_field()


    def _update_graphics_field(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                self.canvas.remove(self.blocks_col[i][j])
                self.canvas.remove(self.blocks_rect[i][j])
                self.blocks_col[i][j] = Color(*self.colors[self.blocks[i][j]])
                self.blocks_rect[i][j] = Rectangle(pos = (self.grid_x + self.grid_size * j + 1,
                                                          self.grid_y + self.grid_size * i + 1),
                                                   size = (self.grid_size - 2, self.grid_size - 2))
                self.canvas.add(self.blocks_col[i][j])
                self.canvas.add(self.blocks_rect[i][j])

    def _update_graphics_next_block(self, block):
        self.canvas.remove(self.next_block_col)
        self.next_block_col = Color(*self.colors[block.color])
        self.canvas.add(self.next_block_col)
        for i in range(4):
            for j in range(4):
                if self.next_block_rect[i][j]:
                    self.canvas.remove(self.next_block_rect[i][j])
                    self.next_block_rect[i][j] = 0
                if block.current[i][j]:
                    self.next_block_rect[i][j] = Rectangle(pos = (self.next_block_x + self.grid_size * j + 1,
                                                                   self.next_block_y + self.grid_size * (3 - i) + 1),
                                                           size = (self.grid_size - 2, self.grid_size - 2))
                    self.canvas.add(self.next_block_rect[i][j])



class Block:

    shapes = [[[0,0,0,0],
               [0,0,0,0],
               [0,0,0,0],
               [0,0,0,0]],
              [[0,0,0,0],
               [1,1,1,0],
               [0,0,1,0],
               [0,0,0,0]],
              [[0,0,0,0],
               [1,1,1,1],
               [0,0,0,0],
               [0,0,0,0]],
              [[0,0,0,0],
               [1,1,1,0],
               [0,1,0,0],
               [0,0,0,0]],
              [[0,0,0,0],
               [1,1,0,0],
               [0,1,1,0],
               [0,0,0,0]],
              [[0,0,0,0],
               [0,1,1,0],
               [0,1,1,0],
               [0,0,0,0]]]

    def __init__(self, x, y, type, color):
        self.x, self.y = x, y
        self.current = copy.deepcopy(self.shapes[type])
        self.color = color



class MyKeyboardListener(Widget):

    def __init__(self, **kwargs):
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        #return True


class TetrisApp(App):
    def build(self):
        random.seed()
        self.title = 'My Tetris Game'
        return RootWidget(basex = 50, basey = 50, height = 20, width = 8, pixel = 25)



if __name__ == '__main__':
    TetrisApp().run()