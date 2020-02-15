#######################################
### Self contained DropDown widgets ###
#######################################
import kivy
import resources.emojilist
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

class EmojiBox(DropDown):
	state = 'new'
	def BuildList(self, x, card, fav_emoji):
		print('hello')
		self.box.favorites = Button(text=fav_emoji[0])
		self.box.favorites.bind(on_release=lambda x:self.Favorites(card, fav_emoji))
		self.box.add_widget(self.box.favorites)
		self.box.smilies = Button(text=emojilist.smilies[0])
		self.box.smilies.bind(on_release=lambda x:self.Smilies(card))
		self.box.add_widget(self.box.smilies)
		self.box.people = Button(text=emojilist.people[0])
		self.box.people.bind(on_release=lambda x:self.People(card))
		self.box.add_widget(self.box.people)
		self.box.travel = Button(text=emojilist.travel[0])
		self.box.travel.bind(on_release=lambda x:self.Travel(card))
		self.box.add_widget(self.box.travel)
		self.box.food = Button(text=emojilist.food[0])
		self.box.food.bind(on_release=lambda x:self.Food(card))
		self.box.add_widget(self.box.food)
		self.box.world = Button(text=emojilist.world[0])
		self.box.world.bind(on_release=lambda x:self.World(card))
		self.box.add_widget(self.box.world)
		self.box.symbols = Button(text=emojilist.symbols[0])
		self.box.symbols.bind(on_release=lambda x:self.Symbols(card))
		self.box.add_widget(self.box.symbols)
		self.box.objects = Button(text=emojilist.objects[0])
		self.box.objects.bind(on_release=lambda x:self.Objects(card))
		self.box.add_widget(self.box.objects)
		if self.state == 'new':
			self.Favorites(card, fav_emoji)

	def Favorites(self, card, fav_emoji):
		if self.state != 'favorites':
			print(fav_emoji[0])
			self.grid.clear_widgets()
			for i in fav_emoji:
				#print(i.encode('unicode-escape').decode('ASCII'))
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'favorites'
			self.scroll.scroll_y = 1

	def Smilies(self, card):
		if self.state != 'smilies':
			print(emojilist.smilies[0])
			self.grid.clear_widgets()
			for i in emojilist.smilies:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'smilies'
			self.scroll.scroll_y = 1

	def People(self, card):
		if self.state != 'people':
			print(emojilist.people[0])
			self.grid.clear_widgets()
			for i in emojilist.people:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'people'
			self.scroll.scroll_y = 1

	def Travel(self, card):
		if self.state != 'travel':
			print(emojilist.travel[0])
			self.grid.clear_widgets()
			for i in emojilist.travel:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'travel'
			self.scroll.scroll_y = 1

	def Food(self, card):
		if self.state != 'food':
			print(emojilist.food[0])
			self.grid.clear_widgets()
			for i in emojilist.food:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'food'
			self.scroll.scroll_y = 1

	def World(self, card):
		if self.state != 'world':
			print(emojilist.world[0])
			self.grid.clear_widgets()
			for i in emojilist.world:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'world'
			self.scroll.scroll_y = 1

	def Symbols(self, card):
		if self.state != 'symbols':
			print(emojilist.symbols[0])
			self.grid.clear_widgets()
			for i in emojilist.symbols:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'symbols'
			self.scroll.scroll_y = 1

	def Objects(self, card):
		if self.state != 'objects':
			print(emojilist.objects[0])
			self.grid.clear_widgets()
			for i in emojilist.objects:
				self.grid.emoji = Button(text=i, size_hint_y=None, height=30, color=(0,0,0,1), background_color=(1,0.7,1,0), font_size=20)
				self.grid.emoji.bind(on_release=card.insert_emoji)
				self.grid.add_widget(self.grid.emoji)
			self.state = 'objects'
			self.scroll.scroll_y = 1

class Options(DropDown):
	def BuildList(self, scroll):
		self.clear_widgets()
		self.contacts = Button(text='Contact Books', size_hint_y = None, height=44)
		self.contacts.bind(on_release=lambda x:scroll.open_contacts())
		self.contacts.bind(on_release= self.dismiss)
		self.add_widget(self.contacts)

		self.refresh = Button(text='Refresh', size_hint_y = None, height=44)
		self.refresh.bind(on_release=lambda x:scroll.clear())
		self.refresh.bind(on_release= self.dismiss)
		self.add_widget(self.refresh)

		self.logout = Button(text='Log Out', size_hint_y = None, height=44)
		self.logout.bind(on_release=lambda x:scroll.log_out())
		self.logout.bind(on_release= self.dismiss)
		self.add_widget(self.logout)
