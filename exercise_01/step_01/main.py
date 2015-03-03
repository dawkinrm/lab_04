from kivy.app import App
from kivy.uix.widget import Widget

class DieRollerApp(App):
  def build(self):
    return DieRoller()

class DieRoller(Widget):
  pass

if __name__ == "__main__":
  DieRollerApp().run()
