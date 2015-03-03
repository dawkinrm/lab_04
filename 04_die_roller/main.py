import random
import math
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.cache import Cache
from kivy.core.image import ImageLoader
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.utils import platform

__version__ = '0.1'

Cache.register('dieroller', limit=200)

roll_sound = SoundLoader.load('data/rolling.ogg')

class DieResult(Widget):

    texture = ObjectProperty()

    def __init__(self, **kwargs):
        self.texture = ImageLoader.load('data/d_blank.png').texture
        super(DieResult, self).__init__(**kwargs)

    def update_image(self, new_image):
        texture = Cache.get('dieroller', new_image)
        if texture is None:
            img = ImageLoader.load(new_image)
            texture = img.texture
            Cache.append('dieroller', new_image, img.texture)
        self.texture = texture


class DieRoller(Widget):

    roll = NumericProperty()
    animcount = NumericProperty()
    die = StringProperty('D6')

    dice = {
           'D6': (1, 6),
           'D8': (1, 8),
           'D10': (1, 10),
           'D12': (1, 12),
           }

    def on_roll(self, instance, value):
        imgname = 'data/%s_%d.png' % (self.die.lower(), self.roll)
        self.result.update_image(imgname)

    def animate_roll(self, dt):
        self.roll = random.randint(*self.dice[self.die])
        self.animcount -= 1
        if self.animcount == 0:
            Clock.unschedule(self.animate_roll)

    def do_roll(self, name=None):
        if name:
            self.die = name
        if App.get_running_app().config.getboolean('die_roller', 'sound'):
            roll_sound.play()
        self.animcount = 15
        Clock.schedule_interval(self.animate_roll, 0.05)


class DieRollerApp(App):

    title = 'A Die roller'

    def __init__(self, **kwargs):
        super(DieRollerApp, self).__init__(**kwargs)
        if platform() == 'android':
            from jnius import autoclass
            Hardware = autoclass('org.renpy.android.Hardware')
            self.hw = Hardware()
            self.hw.accelerometerEnable(True)
            self.last = None
            self.last_shake = 0
        else:
            self.hw = None

    def build(self):
        Clock.schedule_interval(self.check_shake, 0.1)
        return DieRoller()

    def check_shake(self, dt):
        """We're not actually detecting a shake, but it's close enough for now"""
        if self.hw is None:
            return
        cur = self.hw.accelerometerReading()
        if self.last is None:
            self.last = cur
            return
        if self.last_shake > 0:
            self.last_shake -= 1
        delta = (cur[0] - self.last[0],
                 cur[1] - self.last[1],
                 cur[2] - self.last[2])
        # Kinda 10x speed, since we assume that dt is approximately constant,
        # ignore the required scaling and approximate the norm with abs
        speed = math.fabs(delta[0]) + math.fabs(delta[1]) + math.fabs(delta[2])
        if speed > 4 and self.last_shake == 0:
            self.root.do_roll()
            self.last_shake = 11
        self.last = cur

    def on_pause(self):
        # Don't quit if we're paused
        return True

    def build_config(self, config):
        config.setdefaults('die_roller', {'sound': True})

    def build_settings(self, settings):
        config_json = """[
            { "type": "title",
              "title": "A Die Roller"
            },
            { "type": "bool",
              "title": "Enable sound",
              "desc": "Enable the rolling sound",
              "section": "die_roller",
              "key": "sound"
            }
            ]"""
        settings.add_json_panel("A Die Roller", self.config, data=config_json)


if __name__ == "__main__":
    DieRollerApp().run()
