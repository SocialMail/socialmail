from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class AboutPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.cols = 1
		self.message = Label(halign="center", valign="middle", font_size=30)
		self.add_widget(self.message)
