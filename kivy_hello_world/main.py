
from kivy.app import App
from kivy.uix.label import Label


__version__ = "0.1"


class HelloWorldApp(App):
    def build(self):
        return Label(text='Hello world')


if __name__ == '__main__':
    HelloWorldApp().run()