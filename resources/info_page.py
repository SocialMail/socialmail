from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


# Simple information/error page
class InfoPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		# Just one column
		self.cols = 1
		# And one label with bigger font and centered text
		self.message = Label(halign="center", valign="middle", font_size=30)
		# By default every widget returns it's side as [100, 100], it gets finally resized,
		# but we have to listen for size change to get a new one
		# more: https://github.com/kivy/kivy/issues/1044
		self.message.bind(width=self.update_text_width)
		# Add text widget to the layout
		self.add_widget(self.message)

	# Called with a message, to update message text in widget
	def update_info(self, message):
		self.message.text = message
	# Called on label width update, so we can set text width properly - to 90% of label width
	def update_text_width(self, *_):
		self.message.text_size = (self.message.width * 0.9, None)
