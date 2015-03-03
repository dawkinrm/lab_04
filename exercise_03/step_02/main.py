import random
import math
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.core.image import ImageLoader
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.cache import Cache

roll_sound = SoundLoader.load("../data/rolling.ogg")
Cache.register("dieroller", limit = 100)

class DieRollerApp(App):
  def build(self):
    return DieRoller()

class DieRoller(Widget):
  roll = NumericProperty()
  animcount = NumericProperty()
  die = StringProperty("D6")
  dice = {
           "D6": (1, 6),
           "D8": (1, 8),
           "D10": (1, 10),
           "D12": (1, 12),
           }
  result_texture = ObjectProperty()

  def do_roll(self, name = None):
    self.die = name
    self.animcount = 15
    Clock.schedule_interval(self.animate_roll, 0.05)
#    roll_sound.play()

  def animate_roll(self, dt):
    self.roll = random.randint(*self.dice[self.die])
    self.animcount -= 1
    if self.animcount == 0:
      Clock.unschedule(self.animate_roll)
#      roll_sound.stop()

  def on_roll(self, instance, value):
    imgname = "../data/%s_%d.png" % (self.die.lower(), self.roll)
    self.result.update_image(imgname)

  def update_image(self, new_image):
    result_texture = Cache.get("dieroller", new_image)
    if result_texture is None:
      img = ImageLoader.load(new_image)
      result_texture = img.texture
      Cache.append("dieroller", new_image, img.texture)
    self.texture = result_texture

  def __init__(self, **kwargs):
    self.result_texture = ImageLoader.load("../data/d_blank.png").texture
    super(DieRoller, self).__init__(**kwargs)

if __name__ == "__main__":
  DieRollerApp().run()
