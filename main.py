# -*- coding: utf-8 -*-

import os
#os.environ['KIVY_GRAPHICS'] = 'gles'
#os.environ['USE_SDL2'] = '0'
#os.environ['KIVY_TEXT'] = 'pil' # sdl2 (works linux and android)
import sys
sys.path.append("resources/")

import re
import base64

import kivy
# disable multitouch
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy','window_icon','icon128.png')

#import socket_client #if implimenting chat client

from resources.MailFetcher import SMail
from resources.info_page import InfoPage
from resources.my_dropdowns import EmojiBox, Options
import resources.emojilist

from string import ascii_lowercase
import webbrowser

from plyer.facades import StoragePath #get_pictures_dir()
from plyer.facades import FileChooser # choose_dir(*args, **kwargs) open_file(*args, **kwargs) save_file(*args, **kwargs)
from plyer.facades import Camera # take_picture(filename, on_complete)  take_video(filename, on_complete)

from kivy.app import App
from kivy.clock import Clock
from functools import partial
Clock.max_iteration = 20
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.uix.stacklayout import StackLayout
from kivy.uix.togglebutton import ToggleButton
#from kivy.core.image import Image as CoreImage
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview.views import RecycleDataViewBehavior
# below transitions are imported for testing
from kivy.uix.screenmanager import WipeTransition, FadeTransition, SwapTransition, CardTransition, FallOutTransition

# fix for sys.ecxepthook errors on exit https://github.com/kivy/kivy/issues/5986
from kivy.uix.recycleview.views import _cached_views, _view_base_cache

# SMTP login, SMTP port, IMAP login, IMAP4_SSL port, inbox folder name, sent mail folder name
# commented servers are untested, TODO sent folders could be added here, rather than iterating through possibilities in MailFetcher
# any server listed here will be progromatically added to the list
# this dict will be replaced if custom_servers.txt exists
smtp_servers = {
	'Swiger':["mail.swiger.rocks", '587', "mail.swiger.rocks", '993', "INBOX", "INBOX.Sent"],
	'Gmail':["imap.gmail.com", '587', "imap.gmail.com", '993', "Inbox", '"[Gmail]/Sent Mail"'], #'"[Gmail]/All Mail"'
	'Outlook':["smtp-mail.outlook.com", '587', "imap-mail.outlook.com", '143', "Inbox", "Sent"],
	#Yahoo = ["smtp.mail.yahoo.com", 587, "imap.mail.yahoo.com", 993, "Inbox"],
	#Att = ["smtp.mail.att.net", 587, "imap.mail.att.net", 993, "Inbox"],
	#Comcast = ["smtp.comcast.net", 465, "imap.comcast.net", 993, "Inbox"],
	#Verison = ["smtp.verison", 465, "imap.verison", 993, "Inbox"],
	'User':["", '587', "", '993', "Inbox"],
	}


# contact books will be built from saved data
# Each sub list is a book, first entry is the name of the book,
# each following entry is another list with individual contact information
# [['Demobook', ['demo@email.com', 'First name', 'Last name']]
contact_books = [
					['Everyone'],
					['Family'],
					['Friends']
				]
# default favorites based on top 20 twitter emoji jan 2020
# favorites will be stored locally most recent first, up to 48
fav_emoji = [u'\U0001f64f',u'\U0001f49c',u'\U0001f449',u'\u2764', u'\ufe0f',
			u'\U0001f60a',u'\U0001f609',u'\U0001f605',u'\U0001f602',u'\U0001f60d',
			u'\U0001f60e',u'\U0001f612',u'\U0001f641',u'\U0001f62d',u'\U0001f440',
			u'\U0001f495',u'\U0001f44d',u'\U0001f44c',u'\U0001f4af',u'\U0001f525',
			]

imap_host = "imap.gmail.com"
imap_port = "587"
imap_hostS = "imap.gmail.com"
imap_portS = '993'
imap_user = ""
imap_pass = ""
imap_folder = ""
eNum = -1
imap_sent = ""

color_button = '[0.5, 0.3, 0.5, 0.5]'
color_text_input = '[0.9, 0.8, 0.9, 1]'
color_background = '[0.2, 0.1, 0.2, 1]'
color_about_text = '[0.18, 0.1, 0.18, 1]'
color_background_info = '[0.2, 0.1, 0.2, 0.8]'
color_scroll_bar = '[.3, .1, .3, .9]'
color_card = '[0.23, 0.1, 0.23, 1]'
color_post_card = '[0.19, 0.1, 0.19, 1]'
color_reply_card = '[0.24, 0.1, 0.24, 1]'
color_card_from_text = '[1, 0.9, 1, 1]'
color_card_sub_text = '[1, 0.7, 1, 1]'
color_card_body_background = '[0.2, 0.1, 0.2, 0.6]'

post_card_height = 200 # minimum size before adjustng for text height
post_card_max = 700 # max size after a
reply_card_height = 230
image_box_size = 400

intro_text = '''
Unlike other social networking apps,
SocialMail does not use it's own server,
Does not collect any user information,
Does not control any data you share.

It simply requires an email account.
'''


kv = f"""

#####################
### General Rules ###
#####################

<Button>:
	font_name: 'theme/fonts/megafont.ttf'
	background_color: {color_button}
	mipmap: True
	font_size: 18
<Label>:
    font_name: 'theme/fonts/megafont.ttf'
	font_size: 18
	mipmap: True
	padding: 10, 10
<TextInput>:
	font_size: 18
	mipmap: True
	font_name: 'theme/fonts/megafont.ttf'
	background_color: {color_text_input}
	unfocus_on_touch: False
<Image>:
	mipmap: True

#####################
### Display Cards ###
#####################

<PostCard>: # A dropdown on the ScrollPage for sending messages
	text_to: text_to
	text_sub: text_sub
	text_body: text_body
	current_emoji: 'body'
	emails: []
	names: ''
	padding: (0, dp(8))
	on_dismiss:
		app.send_sub = text_sub.text
		app.send_body = text_body.text
	canvas.before:
		Color:
			rgba: {color_post_card}
		RoundedRectangle:
			size: self.size
			pos: self.pos
	GridLayout:
		cols: 2
		id: headerbox
		height: dp(35)
		spacing: dp(8)
		size_hint_y: None
		height: self.minimum_height
		padding: dp(8)
		Label:
			size_hint_x: 0.2
			halign: 'right'
			text: 'Share with:'
		Button:
			id: text_to
			text: '{contact_books[0][0]}'
			on_release: root.open_dropdown(self)
			font_name: 'theme/fonts/megafont.ttf'
			color: {color_card_from_text}
			height: dp(40)
			halign: 'left'
			valign: 'middle'
			size_hint_y: None
		Label:
			size_hint_x: 0.2
			halign: 'right'
			text: 'Subject:'
		TextInput:
			id: text_sub
			hint_text: 'A short message or title here...'
			font_name: 'theme/fonts/megafontbold.ttf'
			size_hint_y: None
			halign: 'left'
			valign: 'middle'
			height: dp(40)
			multiline: False
			write_tab: False
			on_focus:
				root.current_emoji = 'sub'
		Label:
			size_hint_x: 0.2
			valign: 'top'
			halign: 'right'
			text: 'Body:'
		ScrollView: # Body
			id: scrollV
			do_scroll_x: False
			do_scroll_y: True
			bar_width: dp(10)
			bar_color: {color_scroll_bar}
			size_hint_y: None
			height: 300
			TextInput:
				id: text_body
				hint_text: 'Enter a longer message here...'
				size_hint_y: None
				halign: 'left'
				valign: 'middle'
				height: max( (len(self._lines)+1) * self.line_height, scrollV.height)
				on_focus:
					root.current_emoji = 'body'
		Button:
			text: '😃'
			on_release: root.emoji_menu(text_body, root)
			size_hint_x: 0.2
		Button:
			text: 'send'
			size_hint_y: None
			height: dp(40)
			on_release: root._send_mail()

<Card>: # generated by the RecycleView on ScrollPage
	canvas.before:
		Color:
			rgba: {color_card}
		RoundedRectangle:
			size: self.size
			pos: self.pos
	# Data fields populated by the mail fetcher #
	msg_id: ''
	_from: ''
	email: []
	bcc: []
	subject: ''
	body: ''
	nomarkup_body: ''
	_date: ''
	images: []
	replies: []
	hasreply: 0.1
	hasimage: 0.1
	# internal references #
	headerbox: headerbox
	replybox: replybox
	reply_text: reply_text
	body_label: body_label
	size_hint_y: None
	card_size: {post_card_height}
	orientation: 'vertical'
	padding: 20
	height: self.minimum_height
	BoxLayout:
		id: headerbox
		size_hint_y: None
		height: self.minimum_height
		spacing: dp(8)
		Label:
			id: head_label
			text: root._from
			font_name: 'theme/fonts/megafontbold.ttf'
			color: {color_card_from_text}
			size_hint_y: None
			text_size: (self.width, None)
			height: self.texture_size[1]
			halign: 'left'
			valign: 'middle'
		Button:
			text: '➕'
			font_size: 22
			size_hint_y: None
			size_hint_x: 0.1
			height: head_label.height
			#on_press: root.option_pressed(self, root)
			on_release: root.option_released(self, root)
	Label:
		text: root.subject
		color: {color_card_sub_text}
		size_hint_y: None
		text_size: (self.width, None)
		height: self.texture_size[1]
		halign: 'left'
		valign: 'middle'
	ImageBox: ### image box
		data: root.images
		hasimage: root.hasimage
		id: imagebox
		height: 0 if len(self.data) < 2 else {image_box_size} #root.hasimage
		size_hint_y: None

	Label:
		id: body_label
		canvas.before:
			Color:
				rgba: {color_card_body_background}
			RoundedRectangle:
				size: self.size
				pos: self.pos
		size_hint_y: None
		size_hint_x: 1
		show_all: False
		max_size: dp(400) if self.texture_size[1] > dp(399) else None
		text_size: self.width, None if self.show_all == True else self.max_size
		height: self.texture_size[1]
		text: root.body
		halign: 'left'
		valign: 'top'
		markup: True
		on_ref_press: root.open_http([args[1]][0])
	LabelButton:
		text: 'Show more...' if body_label.show_all == False else 'Show less...'
		text_size: self.size
		height: dp(40)
		halign: 'center'
		valign: 'middle'
		size_hint_y: None
		on_release:
			body_label.show_all = not body_label.show_all
			root.scroll_to_field(headerbox)

	Label:
		text: root._date
		text_size: self.size
		height: dp(40)
		halign: 'right'
		valign: 'middle'
		size_hint_y: None

	ScrollView: ### list for replies
		# data contains an empty dict that is stubborn, clear it first
		#data: []
		# now set data to the replies list (shrug)
		#data: root.replies
		scroll_type: ['bars', 'content']
		bar_width: dp(10)
		bar_color: {color_scroll_bar}
		#viewclass: 'ReplyCard'
		size_hint_y: None
		height: min(replybox.height, 700)
		BoxLayout:
			id: replybox
			padding: 45, 10
			size_hint_y: None
			height: self.minimum_height
			orientation: 'vertical'
			spacing: dp(20)

	BoxLayout: ###  reply field here
		height: self.minimum_height
		spacing: dp(8)
		size_hint_y: None
		Button:
			text: '😃'
			on_release: root.emoji_menu(reply_text, root)
			size_hint_x: 0.2
			size_hint_y: None
			height: dp(35)
		TextInput:
			id: reply_text
			hint_text: 'share these comments' if len(root.replies) > 0 else 'type reply'
			text_size: self.size
			size_hint_y: None
			height: min((len(self._lines)+1) * self.line_height, dp(300))
			on_focus: root.scroll_to_field(self)
			halign: 'left'
			valign: 'middle'
		Button:
			text: 'Reply' if len(root.replies) < 1 else 'Share'
			on_release: root.reply(reply_text.text, root)
			size_hint_x: 0.2
			size_hint_y: None
			height: dp(35)

<ReplyCard>:
	canvas.before:
		Color:
			rgba: {color_reply_card}
		RoundedRectangle:
			size: self.size
			pos: self.pos
	msg_id: ''
	_from: ''
	email: ''
	subject: ''
	body: ''
	_date: ''
	card_size: ''
	share: share
	reply_text: reply_text
	orientation: 'vertical'
	size_hint_y: None
	height: self.minimum_height
	BoxLayout:
		size_hint_y: None
		height: dp(35)
		Label:
			text: root._from
			font_name: 'theme/fonts/megafontbold.ttf'
			color: {color_card_from_text}
			text_size: self.size
			halign: 'left'
			valign: 'middle'
		CheckBox:
			id: share
			active: True
			on_active: print(self.active)
			size_hint_x: 0.1
	ScrollView:
		do_scroll_x: False
		do_scroll_y: True
		bar_color: {color_scroll_bar}
		size_hint_y: None
		height: min(reply_body_label.height, 200)
		Label:
			id: reply_body_label
			canvas.before:
				Color:
					rgba: {color_card_body_background}
				RoundedRectangle:
					size: self.size
					pos: self.pos
			size_hint_y: None
			size_hint_x: 1
			height: self.texture_size[1]
			text_size: self.width, None
			text: root.body
			halign: 'left'
			valign: 'middle'
			markup: True
			on_ref_press: root.open_http([args[1]][0])
	Label:
		text: root._date
		text_size: self.size
		size_hint_y: None
		height: dp(35)
		halign: 'right'
		valign: 'middle'

	BoxLayout: ###  reply field here
		height: self.minimum_height
		spacing: dp(8)
		size_hint_y: None
		Button:
			text: '😃'
			on_release: root.emoji_menu(reply_text, root)
			size_hint_x: 0.2
			size_hint_y: None
			height: dp(35)
		TextInput:
			id: reply_text
			hint_text: ('reply to ' + root._from)
			text_size: self.size
			size_hint_y: None
			height: min((len(self._lines)+1) * self.line_height, dp(300))
			on_focus: root.scroll_to_field(self)
			halign: 'left'
			valign: 'middle'
		Button:
			text: 'Reply'
			on_release: root.reply(reply_text.text, root)
			size_hint_x: 0.2
			size_hint_y: None
			height: dp(35)

<ImageBox>:
	data: None
	pic1: None
	name: ''
	main: main
	picbox: picbox
	begin: root.load_images(root.data)
	Image:
		id: main
		opacity: 0
		allow_stretch: False
		keep_ratio: True
	BoxLayout:
		id: picbox
		default_size_hint: 1, 1
		size_hint_y: 1
		size_hint_x: None
		width: 0
		height: self.minimum_height
		orientation: 'vertical'
		spacing: dp(20)

#################
### App Pages ###
#################

<ScrollPage>:
	canvas:
		Color:
			rgba: {color_background}
		Rectangle:
			size: self.size
			pos: self.pos
	rv: rv
	openhere: openhere
	cardgrid: cardgrid
	send_label: send_label
	orientation: 'vertical'
	GridLayout: ### top buttons
		canvas:
			Color:
				rgba: {color_card}
			Rectangle:
				size: self.size
				pos: self.pos
		cols: 4
		rows: 1
		size_hint_y: None
		height: dp(50)
		Button:
			text: ' ⬆️'
			halign: 'center'
			on_release: root.rv.scroll_y = 1
			size_hint_x: None
			width: dp(40)
		Image:
			id: openhere
			source: 'Banner64.png'
		Button:
			text: '...'
			halign: 'center'
			on_release: root.option_menu(openhere)
			size_hint_x: None
			width: dp(40)
	GridLayout: ### second Row
		canvas:
			Color:
				rgba: {color_card}
			Rectangle:
				size: self.size
				pos: self.pos
		id: cardgrid
		cols: 3
		rows: 1
		size_hint_y: None
		height: dp(50)
		padding: dp(8)
		spacing: dp(16)
		Image:
	    	source: 'icon128.png'
	    	size: self.texture_size
			size_hint_x: 0.4
			size_hint_y: 0.1
		LabelButton:
			canvas.before:
				Color:
					rgba: 1,1,1,1
				Rectangle:
					pos: self.pos
					size: self.size
			id: send_label
			color: 0,0,0,0.2
			text: 'Share something...'
			on_release:
				root.post_card(openhere)
		Label:
			text: ''
			size_hint_x: 0.4

	ScrollView: ### infinite list
		id: rv
		data: []
		box: box
		do_scroll_y: True
		do_scroll_x: False
		# change scroll_type in innit for desktop systems
		scroll_type: ['content']
		bar_width: dp(10)
		bar_color: {color_scroll_bar}
		viewclass: 'Card'
		BoxLayout:
			id: box
			default_size: None, None
			default_size_hint: 1, None
			padding: (45, -10)
			size_hint_y: None
			height: self.minimum_height
			orientation: 'vertical'
			spacing: dp(20)

<InfoPage>:
	canvas.before:
		Color:
			rgba: {color_background_info}
		Rectangle:
			pos: self.pos
			size: self.size
	Label:
		size_hint_y: 0.5
	Image:
    	source: 'icon128.png'
    	size: self.texture_size
		size_hint_y: 0.5
		valign: 'middle'

<AboutPage>:
	cols: 2
	padding: 40
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size
	Image:
		source: 'icon128.png'
		size: self.texture_size
		height: 70
		size_hint_y: None
		size_hint_x: 0.3
		valign: 'middle'
	Label:
		font_size: 20
		text: 'A new kind of Social Media, for a new kind of internet.'
		text_size: self.width, None
		size_hint_y: None
	Label:
		size_hint_x: 0.3
	ScrollView:
		do_scroll_x: False
		do_scroll_y: True
		bar_width: dp(8)
		bar_color: {color_scroll_bar}
		size_hint_y: 1
		Label:
			canvas.before:
				Color:
					rgba: {color_about_text}
				RoundedRectangle:
					size: self.size
					pos: self.pos
			size_hint_y: None
			size_hint_x: 1
			height: self.texture_size[1]
			text_size: self.width, None
			markup: True
			text: "[size=30]What is SocialMail?[/size]\\n\\nA social media network, where [size=20]you[/size] are the network.\\n\\nSocialMail aims to replicate all the popular features of other social media networks, without a centralized server manipulating the content you see, or selling your information to the highest bidder.\\n\\nMessages are sent and recieved via a standard email account, everything else is handled locally by the app. No information is sent to a third party at any time.\\n\\n'Posts' are displayed in an endless scrolling page, with pictures, sharing, and comments. While messages you send can be shared with your entire network, or a select group.\\n\\n[size=30]Why SocialMail?[/size]\\n\\nSocialMail contains:\\n * No advertising.\\n * No Data collection.\\n * No 'Algorythims' deciding what you do or don't see.\\n\\nThe beauty of SocialMail is that it does not require a third party 'network.'\\n\\nYou can send and recieve messages to and from anyone you have an email address for, without requiring them to use the app.\\n\\nSocialMail may be the first social media app that is truely decentralized.\\n\\n[size=30]Who is SocialMail?[/size]\\n\\nYou are.\\n\\nWhen SocialMail is running on your device, You are SocialMail.\\n\\nLogin information for your email server is stored locally, as is your contact book, everything else is stored on your email server.\\n\\nThat server can be a popular free server, like gmail or outlook, or it can be a private email server hosted online or in your own home.\\n\\nYour privacy is exactly where it should be, in your own hands.\\n\\n[size=30]How, is SocialMail?[/size]\\n\\nOn it's surface, SocialMail works like any other Social Network.\\n\\nAt it's heart, SocialMail works by reading messages directly from your email inbox, and displaying them as posts on a wall. It identifies replies, and displays them as comments, and allows you full control over who sees those comments if you choose to reply again.\\n\\nIt also displays images and memes, vacation pictures or family photos, in a familiar share friendly format, with full confidence that no one outside of your network will see them. SocialMail isn't about random person #3785 clicking a button, it's about actually comunicating with the people who are important to you.\\n\\nWhen you make or share a post, it can be sent to your entire Network, or to specific Contact Books like 'family' or 'friends.'\\n\\nYou can even exclude specific contacts, if you know someone might not appreciate the joke.\\n\\nFull control over incoming and outgoing informaiton is central to SocialMail's design philosophy.\\n\\nWhen SocialMail asks you to log into your email account, you are logging in to your email server, NOT SocialMail. That information is used exclusively for communication between your device and your email server.\\n\\nThe full source code of SocialMail is availible for free at: https://github.com/SocialMail/socialmail"
	Label:
		size_hint_x: 0.3
		size_hint_y: 0.1
	Button:
		size_hint_y: 0.1
		width: self.width
		text: 'Return to Login'
		on_release: root.connect()

<ConnectPage>
	cols: 2
	server: ''
	padding: (10, 50)
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

<UserConnectPage>
	cols: 2
	padding: 100, 50
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size
	Image:
    	source: 'icon128.png'
    	size: self.texture_size
		size_hint_y: 5
		valign: 'middle'
	Label:
		text: "Want to use your own email server?\\nKeep full controll over your own data?\\n\\nEnter your IMAP and SMTP information below.\\n\\nAll information is stored locally."
		halign: 'center'

<ContactPage>:
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size
	size_hint_y: 1
	rowheight: dp(40)
	orientation: 'vertical'
	email: email
	fname: fname
	lname: lname
	contactbooks: contactbooks
	GridLayout: ## Add contact fields ##
		padding: dp(20)
		canvas.before:
			Color:
				rgba: {color_card}
			Rectangle:
				pos: self.pos
				size: self.size
		height: self.minimum_height
		size_hint_y: None
		cols: 2
		Label:
			size_hint_x: 0.3
			size_hint_y: None
			height: root.rowheight
		Label:
			text: 'Add a New Contact'
			size_hint_y: None
			height: root.rowheight
		Label:
			text: 'Email'
			size_hint_x: 0.3
			size_hint_y: None
			height: root.rowheight
		TextInput:
			id: email
			hint_text: 'enter email'
			size_hint_y: None
			height: root.rowheight
			multiline: False
			write_tab: False
		Label:
			text: 'First'
			size_hint_x: 0.3
			size_hint_y: None
			height: root.rowheight
		TextInput:
			id: fname
			hint_text: 'enter name'
			size_hint_y: None
			height: root.rowheight
			multiline: False
			write_tab: False
		Label:
			text: 'Last'
			size_hint_x: 0.3
			size_hint_y: None
			height: root.rowheight
		TextInput:
			id: lname
			hint_text: 'enter name'
			size_hint_y: None
			height: root.rowheight
			multiline: False
			write_tab: False
		Label:
			size_hint_x: 0.3
			size_hint_y: None
			height: root.rowheight
		Button:
			text: 'Add Contact'
			size_hint_y: None
			height: root.rowheight
			on_release: root.new_contact(email, fname, lname)
		Button:
			text: 'Return'
			size_hint_x: 0.3
			size_hint_y: None
			height: root.rowheight
			on_release: root.return_to_scroll()
		Label:
			size_hint_y: None
			height: root.rowheight
	ScrollView:
		do_scroll_x: False
		do_scroll_y: True
		bar_width: dp(8)
		bar_color: {color_scroll_bar}
		size_hint_y: 1
		BoxLayout:
			canvas.before:
				Color:
					rgba: {color_card}
				Rectangle:
					pos: self.pos
					size: self.size
			id: contactbooks
			size_hint_y: None
			orientation: 'vertical'
			height: self.minimum_height
			Label:
				size_hint_y: None
				height: root.rowheight
				text: 'Contact Books'

######################
### Dropdown lists ###
######################

<EmojiBox>:
	scroll: scroll
	grid: grid
	box: box
	ScrollView:
		id: scroll
		canvas.before:
			Color:
				rgba: {color_text_input}
			RoundedRectangle:
				size: self.size
				pos: self.pos
		height: dp(200)
		size_hint_y: None
		do_scroll_y: True
		bar_width: dp(8)
		bar_color: {color_scroll_bar}
		GridLayout:
			id: grid
			cols: 8
			size_hint_y: None
			height: self.minimum_height
	BoxLayout:
		canvas.before:
			Color:
				rgba: {color_background}
			RoundedRectangle:
				size: self.size
				pos: self.pos
		id: box
		height: 30
		size_hint_y: None

<Options>:
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

<CardOptions>:
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

<ImapDropDown>:
	id:cheeseburger
	cols: 1
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

<ContactDropdown>:
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

<BookDropdown>:
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

<PostToDropdown>:
	canvas.before:
		Color:
			rgba: {color_background}
		Rectangle:
			pos: self.pos
			size: self.size

"""

Builder.load_string(kv)

class ImageButton(ButtonBehavior, Image):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

class ScrollBox(ScrollView, BoxLayout):
	pass

class ImageBox(BoxLayout):
	def load_images(self, images):
		print('images ', images)
		if images is not None:
			if len(images) > 1:
				self.main.texture = images[1]['pic']
				self.main.opacity = 1
				self.picbox.clear_widgets()
				if len(images) > 2:
					self.picbox.width = 80
					for i in images:
						if i['name'] != 'icon128.png':
							self.image = ImageButton(texture=i['pic'])
							self.image.bind(on_release=self.update_image)
							self.picbox.add_widget(self.image)

	def update_image(self, x):
		self.main.texture = x.texture

class PostCard(DropDown):
	def __init__(self, **kwargs):
		super(PostCard, self).__init__(**kwargs)
		print('inniting')
		self.open_book(social_app.scroll_page.book_name)
		self.text_sub.text = social_app.send_sub
		self.text_body.text = social_app.send_body

	def _send_mail(self):
		if self.text_sub.text != '' or self.text_body.text != '':
			# split the user email address
			split = imap_user.split('@')
			# insert plus addressing to ensure this email ends up in the user's sent box
			user_sent = split[0] + '+Sent@' + split[1]
			# add the user to the recipients
			print(self.emails)
			recipients = list(self.emails)
			print(recipients)
			recipients.append(user_sent)
			print('Sending to:', recipients)
			trying = SMail._sending_mail(social_app.send_name, imap_host, imap_port, imap_user, imap_pass, recipients, self.text_sub.text, self.text_body.text, '')
			if trying == True:
				self.text_sub.text = ''
				self.text_body.text = ''
			recipients.clear()

	def open_dropdown(self, x):
		print('clicked')
		self.dropdown = PostToDropdown()
		self.dropdown.open(x)
		self.dropdown.BuildList()
		self.dropdown.bind(on_select=lambda instance,book: self.open_book(book))

	def open_book(self, book):
		social_app.scroll_page.book_name = book
		self.text_to.text = book
		print('book is', book)
		contacts = []
		names = ''
		for i in contact_books:
			if i[0] == book:
				for n in i:
					if n != book:
						contacts.append(n[0])
						names = names + n[1] + ' ' + n[2] + ', '
		print(names)
		print(contacts)
		self.emails = contacts
		self.names = names

	def emoji_menu(self, x, card):
		x.dropdown = EmojiBox()#CardOptions()
		x.dropdown.open(x)
		x.dropdown.BuildList(x, card, fav_emoji)

	def insert_emoji(self, emoji):
		# add the emoji to the text field
		if self.current_emoji == 'body':
			self.text_body.text += emoji.text
		if self.current_emoji == 'sub':
			self.text_sub.text += emoji.text
		# clear the emoji from the favorites list
		for i in fav_emoji:
			if i == emoji.text:
				fav_emoji.remove(i)
		# add it to the front of the list
		fav_emoji.insert(0,emoji.text)
		# trim the list
		if len(fav_emoji) > 48:
			fav_emoji.pop(-1)
		# save the list to disk
		with open("resources/fav_emoji.txt","w") as f:
			f.write(",".join(fav_emoji))

class PostToDropdown(DropDown):
	def BuildList(self):
		self.clear_widgets()
		for i in contact_books:
			if len(i) > 1:
				num = str(len(i) - 1)
				book = Button(text=(i[0]+' ('+num+')'),size_hint_y=None, height=44)
				book.book_name = i[0]
				book.bind(on_release=lambda btn: self.select(btn.book_name))
				self.add_widget(book)

class Card(BoxLayout):
	def reply(self, text, card):
		if text != '':
			split = imap_user.split('@')
			user_sent = split[0] + '+Sent@' + split[1]
			print(card.email)
			recipients = list(card.email)
			if user_sent not in recipients:
				recipients.append(user_sent)
			if len(card.replies) > 0:
				origin = f"{card._from} Shared:\n\n{card.nomarkup_body}"
				for i in card.replybox.children:
					if i.share.active == True:
						new_share = f"\n\n{i._from} replied: \n\n {i.nomarkup_body}"
						origin = origin + new_share
				text = origin + f"{imap_name}<{imap_user}> Responded:\n\n{text}"
			print('pressed', card.email, card.subject, text, card.msg_id)
			trying = SMail._sending_mail(social_app.send_name, imap_host, imap_port, imap_user, imap_pass, recipients, card.subject, text, card.msg_id)
			if trying == True:
				card.reply_text.text = ''

	def open_http(self, address):
		address = address.strip('<')
		address = address.strip('>')
		print("testing",address)
		webbrowser.open(address)

	def show_card(self, target):
		print("scrolling to", target)
		Clock.schedule_once(partial(self.scroll_to_field, target), 0)

	def option_pressed(self, x, card):
		print('option pressed')
		x.color = 0.6,0.5,0.6,1

	def option_released(self, x, card):
		x.color = 1,1,1,1
		print('option released')
		x.dropdown = CardOptions()
		x.dropdown.open(card.headerbox)
		x.dropdown.BuildList(x, card)

	def scroll_to_field(self, field):
		Clock.schedule_once(partial(social_app.scroll_page.rv.scroll_to, field), 0)

	def user_return(self, text):
		print(text)

	def add_contact(self, _):
		social_app.screen_manager.current = 'Contacts'
		social_app.contact_page.update_contact(self._from, self.email)

	def emoji_menu(self, x, card):
		x.dropdown = EmojiBox()#CardOptions()
		x.dropdown.open(x)
		x.dropdown.BuildList(x, card, fav_emoji)

	def insert_emoji(self, emoji):
		# add the emoji to the text field
		self.reply_text.text += emoji.text
		# clear the emoji from the favorites list
		for i in fav_emoji:
			if i == emoji.text:
				fav_emoji.remove(i)
		# add it to the front of the list
		fav_emoji.insert(0,emoji.text)
		# trim the list
		if len(fav_emoji) > 48:
			fav_emoji.pop(-1)
		# save the list to disk
		with open("resources/fav_emoji.txt","w") as f:
			f.write(",".join(fav_emoji))

class ReplyCard(BoxLayout):
	def emoji_menu(self, x, card):
		x.dropdown = EmojiBox()#CardOptions()
		x.dropdown.open(x)
		x.dropdown.BuildList(x, card)

	def insert_emoji(self, emoji):
		# add the emoji to the text field
		self.reply_text.text += emoji.text
		# clear the emoji from the favorites list
		for i in fav_emoji:
			if i == emoji.text:
				fav_emoji.remove(i)
		# add it to the front of the list
		fav_emoji.insert(0,emoji.text)
		# trim the list
		if len(fav_emoji) > 48:
			fav_emoji.pop(-1)
		# save the list to disk
		with open("resources/fav_emoji.txt","w") as f:
			f.write(",".join(fav_emoji))

	def open_http(self, address):
		address = address.strip('<')
		address = address.strip('>')
		webbrowser.open(address)

	def scroll_to_field(self, field):
		social_app.scroll_page.rv.scroll_to(field)

	# replying to a specific comment
	def reply(self, text, reply):
		if text != '':
			split = imap_user.split('@')
			user_sent = split[0] + '+Sent@' + split[1]
			recipients = [str(reply.email), user_sent]
			print('pressed', reply.email, reply._from, text, reply.msg_id)
			trying = SMail._sending_mail(social_app.send_name, imap_host, imap_port, imap_user, imap_pass, recipients, reply.subject, text, reply.msg_id)
			if trying == True:
				reply.reply_text.text = ''

class CardOptions(DropDown):
	def BuildList(self, x, card):
		self.clear_widgets()
		label = 'blank'
		# check if message is from self
		if card.email[0] == imap_user:
			if len(card.bcc) > 1:
				print('BCC:',card.bcc)
			label =  'self'
		if label != 'self':
			# search for an existing contact
			for i in contact_books:
				if i[0] == card.email[0]:
					label =f'Update contact info: {card.email[0]}'
			# if no contact exists
			if label == 'blank':
				label = f'Add {card.email[0]} to contacts'
			# create the button
			self.user = Button(text=label, size_hint_y = None, height=44)
			self.user.bind(on_release=card.add_contact)
			self.user.bind(on_release=self.dismiss)
			self.add_widget(self.user)

		self.share = Button(text='Share this Post...', size_hint_y = None, height=44)
		self.share.bind(on_release=lambda x:social_app.scroll_page.share_post(card.subject, card.nomarkup_body))
		self.share.bind(on_release=self.dismiss)
		self.add_widget(self.share)

class ImapDropDown(DropDown):
	def BuildList(self, _):
		self.clear_widgets()
		for i in smtp_servers:
			# smtp_servers is a dict, and the index is a string
			server = Button(text=i, size_hint_y = None, height=44)
			server.bind(on_release=self.UpdateImap)
			self.add_widget(server)

	def UpdateImap(self, server):
		global imap_host
		global imap_port
		global imap_hostS
		global imap_portS
		# using the button's text as an index gets our list
		imap = smtp_servers[server.text]
		print(imap)
		imap_host = imap[0]
		imap_port = imap[1]
		imap_hostS = imap[2]
		imap_portS = imap[3]
		if imap[0] == '':
			social_app.screen_manager.current = 'UserConnect'
			social_app.user_connect_page.UpdateImap()
		new_text = imap_host
		self.select(imap)

class BookDropdown(DropDown):
	def BuildList(self, x):
		print('building')
		self.clear_widgets()
		self.book = x
		for i in contact_books:
			if i[0] == self.book:
				if len(i) > 1:
					self.remove_book = Label(text='Empty book to Remove',size_hint_y=None, height=30)
				if len(i) == 1:
					self.remove_book = Button(text='Remove Book',size_hint_y=None, height=30)
					self.remove_book.book = x
					self.remove_book.bind(on_release=self.delete_book)
		self.add_widget(self.remove_book)

	def delete_book(self, x):
		for i in contact_books:
			if i[0] == x.book:
				if len(i) == 1:
					contact_books.remove(i)
					social_app.contact_page.BuildPage(None)
					social_app.contact_page.save_contacts()
					self.dismiss()

class ContactDropdown(DropDown):
	def BuildList(self, x):
		self.clear_widgets()
		self.contact = x
		print(self.contact)
		self.update = Button(text='Update Contact',size_hint_y=None, height=30)
		self.update.bind(on_release=self.update_contact)
		self.add_widget(self.update)
		dontdelete = False
		for i in contact_books:
			found = False
			if i[0] != contact_books[0][0]:
				for n in i:
					if n[0] == x[0]:
						book = Button(text='Remove from '+ i[0],size_hint_y=None, height=30)
						book.book = i[0]
						book.bind(on_release=self.remove_contact)
						found = True
						dontdelete = True
				if found == False:
					book = Button(text='Add to '+ i[0],size_hint_y=None, height=30)
					book.book = i[0]
					book.bind(on_release=self.add_contact)
				self.add_widget(book)
		if dontdelete == True:
			rem_contact = Label(text='Cannot Delete',size_hint_y=None, height=30)
		if dontdelete == False:
			rem_contact = Button(text='Delete Contact',size_hint_y=None, height=30)
			rem_contact.book = contact_books[0][0]
			rem_contact.bind(on_release=self.remove_contact)
		self.add_widget(rem_contact)

	def remove_contact(self, x):
		print(x.book, self.contact[0])
		for i in contact_books:
			if i[0] == x.book:
				for n in i:
					if n[0] == self.contact[0]:
						i.remove(n)
		self.BuildList(self.contact)
		social_app.contact_page.save_contacts()
		social_app.contact_page.BuildPage(None)
		self.dismiss()

	def add_contact(self, x):
		print(x.book, self.contact[0])
		for i in contact_books:
			if i[0] == x.book:
				list = self.contact
				i.append(list)
		self.BuildList(self.contact)
		social_app.contact_page.save_contacts()
		social_app.contact_page.BuildPage(None)

	def update_contact(self, x):
		print('updating')
		print(self.contact[0])
		social_app.contact_page.update_contact(self.contact[1]+' '+self.contact[2], self.contact)
		self.dismiss()

class ContactPage(BoxLayout):
	def __init__(self, **kwargs):
		super(ContactPage, self).__init__(**kwargs)
		self.book_name = contact_books[0][0]

	def BuildPage(self, button):
		if button != None:
			self.book_name = button.text
		self.contactbooks.clear_widgets()
		title = Label(text='Contact Books',size_hint_y=None,height=self.rowheight)
		self.contactbooks.add_widget(title)
		# scan each contact book
		for i in contact_books:
			# create a button for each book, 0 index is the name of the book
			self.contactbooks.book = BoxLayout(size_hint_y=None,height=self.rowheight)
			self.contactbooks.add_widget(self.contactbooks.book)
			newbook = ToggleButton(text=i[0], group='books', state='normal',size_hint_y=None,height=self.rowheight)
			newbook.bind(on_release=self.BuildPage)
			self.contactbooks.book.add_widget(newbook)
			option = Button(text='...', size_hint_x=0.2)
			option.book = i[0]
			option.bind(on_release=lambda instance: self.book_option(instance, instance.parent))
			self.contactbooks.book.add_widget(option)
			# if the button text is the same as current book
			if self.book_name == i[0]:
				newbook.state = 'down'
				# no we read the whole list
				for n in i:
					# ignore the first entry, which is the Book name
					if n != i[0]:
						# build layout for each entry
						self.contactbooks.box = BoxLayout(size_hint_y=None,height=self.rowheight)
						self.contactbooks.add_widget(self.contactbooks.box)
						name = Label(text=n[1]+' '+ n[2])
						self.contactbooks.box.add_widget(name)
						contact = Button(text=n[0])
						# store this contact's list
						contact.contact = n
						contact.bind(on_release=self.contact_selected)
						self.contactbooks.box.add_widget(contact)
		self.contactbooks.new = BoxLayout(size_hint_y=None,height=self.rowheight)
		self.contactbooks.add_widget(self.contactbooks.new)
		self.contactbooks.new.input = TextInput(hint_text='New Contact Book', write_tab=False, multiline=False)
		self.contactbooks.new.input.bind(on_text_validate=self.new_book)
		self.contactbooks.new.add_widget(self.contactbooks.new.input)
		self.contactbooks.new.save = Button(text='Save Book', size_hint_x=0.2)
		self.contactbooks.new.save.bind(on_release=self.new_book)
		self.contactbooks.new.add_widget(self.contactbooks.new.save)

	def new_book(self, x):
		book = self.contactbooks.new.input.text
		for i in contact_books:
			if i[0] == book:
				self.contactbooks.new.input.text = ''
				self.contactbooks.new.input.hint_text = 'Book already exists...'
				return
		contact_books.append([book])
		self.BuildPage(None)
		self.save_contacts()

	def book_option(self, x, book):
		x.dropdown = BookDropdown()
		x.dropdown.open(book)
		x.dropdown.BuildList(x.book)

	def contact_selected(self, x):
		x.dropdown = ContactDropdown()
		x.dropdown.open(x)
		x.dropdown.BuildList(x.contact)
		print(x.text, x.contact)

	def new_contact(self, email, fname, lname):
		# Find only valid emails from the email string
		is_email = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",email.text)
		if len(is_email) == 0:
			print('Please enter a valid email.')
			return
		if fname.text == '' and lname.text == '':
			print('Please enter at least one name for this contact.')
			return
		new_contact = [is_email[0], fname.text, lname.text]
		print(new_contact)
		#TODO add error reporting
		# search 'Everyone' for existing contact
		for i in contact_books[0]:
			if i[0] == email.text:
				# delete any existing contact
				contact_books[0].remove(i)
		# add contact to Everyone
		contact_books[0].append(new_contact)
		if self.book_name != contact_books[0][0]:
			for i in contact_books:
				if i[0] == self.book_name:
					i.append(new_contact)
		print(contact_books[0])
		# clear text inputs
		email.text = ''
		fname.text = ''
		lname.text = ''
		#TODO add confirmation reporting
		self.BuildPage(None)
		self.save_contacts()

	def update_contact(self, name, email):
		print(name, email)
		split_name = name.split(' ')
		self.email.text = email[0]
		if len(split_name) > 0:
			self.fname.text = split_name[0]
		if len(split_name) > 1:
			lname = ''
			for i in split_name:
				if i != split_name[0]:
					lname = lname + i
			self.lname.text = lname
		self.save_contacts()

	def save_contacts(self):
		with open(f"../contact_books{imap_user}.txt","w") as f:
			f.write(str(contact_books))

	def return_to_scroll(self):
		social_app.screen_manager.current = 'Scroll'

class ScrollPage(BoxLayout):
	def __init__(self, **kwargs):
		super(ScrollPage, self).__init__(**kwargs)
		self.book_name = contact_books[0][0]
		self.rv.bind(on_scroll_stop=self.on_scroll_stop)
		if os.name == "posix" or os.name == 'nt':
			self.rv.scroll_type = ['bars', 'content']
			self.rv.bar_width = 15
		Clock.schedule_once(self.check_scroll, 1)
		Clock.schedule_once(self.late_initialize, 1)

	def late_initialize(self, x):
		self.openhere.post_card = PostCard()

	def open_contacts(self):
		social_app.screen_manager.current = 'Contacts'
		social_app.contact_page.BuildPage(None)

	def open_http(self, address):
		address = address.strip('<')
		address = address.strip('>')
		webbrowser.open(address)

	def check_scroll(self, _):
		###########################################
		### Define the point to load more cards ###
		### How many cards, and when to remove  ###
		###########################################
		# make sure we are on the scroll page screen
		if social_app.screen_manager.current == 'Scroll':
			# load the first two cards, so we have something to scroll through
			if len(self.rv.box.children) < 1:
				global eNum
				eNum = -1
				# add a label with zero height so text is above the scrollview
				self.rv.box.refresh = Label(text='⬇️ Release to refresh. ⬇️', size_hint_y=None,height=0)
				self.rv.box.add_widget(self.rv.box.refresh)
				Clock.schedule_once(self.fetch_mail, 0)
				Clock.schedule_once(self.check_scroll, 1)
			if len(self.rv.box.children) == 2:
				Clock.schedule_once(self.fetch_mail, 0)
				loadmore = Label(text="⬆️ Pull up to load more ⬆️",size_hint_y=None,height=50)
				self.rv.box.add_widget(loadmore)
			# Then check our current scroll, if we scrolled past zero
			if self.rv.scroll_y < 0 and len(self.rv.box.children) > 2:
				self.rv.scroll_y = 0
				#find and update the label
				for i in self.rv.box.children:
					# first item in the list is the most recent widget
					try:
						if i.text == "⬆️ Pull up to load more ⬆️":
							i.text = "Loading..."
							break
					except:
						print("Did not find loading label")
						pass
				Clock.schedule_once(self.fetch_mail, 0.1)
			# Check if we scrolled past the top
			if self.rv.scroll_y > 1:
				self.rv.scroll_y = 1
				#refresh cards
				self.clear()

	def on_scroll_stop(self, _, hello):
		if self.rv.scroll_y < 0 or self.rv.scroll_y > 1:
			self.check_scroll(None)

	def log_out(self):
		social_app.screen_manager.current = 'Connect'
		self.clear()

	def clear(self):
		global eNum
		global _first
		self.rv.box.clear_widgets()
		Clock.schedule_once(self.check_scroll, 1)
		eNum = -1

	def find_last(self):
		### Find the most recent card and scroll to it ###
		get_last = None
		# children is not callable, so iterate to find the first item
		for i in self.rv.box.children:
			# first item in the list is the most recent widget
			if get_last == None:
				get_last = i
			try:
				# need to remove the label
				if i.text == "⬆️ Pull up to load more ⬆️" or i.text == "Loading...":
					self.rv.box.remove_widget(i)
			except:
				# if i.test results in an exception,
				# then we have found the Card we were looking for
				pass
		if self.rv.scroll_y < 0.5:
			self.rv.scroll_to(get_last, 10, True)
		# add a new label
		loadmore = Label(text="⬆️ Pull up to load more ⬆️",size_hint_y=None,height=50)
		self.rv.box.add_widget(loadmore)

	def fetch_mail(self, _):
		global eNum
		email_recieved = SMail._read_mail(imap_hostS, imap_portS, imap_user, imap_pass, imap_folder, eNum)
		#print("got an email: ", email_recieved)
		if email_recieved == False:
			return
		if email_recieved['alreadyLoaded'] == True:
			print('trying next message')
			if eNum < -1:
				eNum -= 1
			return
		# search for images
		images = SMail._read_images(imap_hostS, imap_portS, imap_user, imap_pass, imap_folder, email_recieved['msg_id'])
		hasimage = 0
		if len(images) > 1:
			print(len(images))
			hasimage = image_box_size
		email_is_reply = False
		if email_recieved['inreply'] != None:
			print('message is a reply')
			email_source = SMail._read_source(imap_hostS, imap_portS, imap_user, imap_pass, imap_folder, email_recieved['inreply'])
			print('source', email_source)
			if email_source != False:
				print('source found: ', email_source['subject'])
				email_is_reply = True
		email_replies = []
		if email_is_reply:
			print('about to send for replies')
			email_replies = SMail._find_replies(imap_hostS, imap_portS, imap_user, imap_pass, imap_folder, email_source['msg_id'])
			print('recieved replies?')
			print(email_replies)
			self.load_card({
				'msg_id': email_source['msg_id'],
				'_from': email_source['from'],
				'email': email_source['bcc'],
				'subject': email_source['subject'],
				'body': email_source['body'],
				'nomarkup_body': email_source['nomarkup_body'],
				'_date': email_source['_date'],
				'images': images,
				'replies': email_replies,
				'hasreply': 1,
				'hasimage': hasimage,
				})
		if not email_is_reply:
			self.load_card({
				'msg_id': email_recieved['msg_id'],
				'_from': email_recieved['from'],
				'email': email_recieved['email'],
				'subject': email_recieved['subject'],#.encode('utf-8').decode('utf-8')
				'body': email_recieved['body'],
				'nomarkup_body': email_recieved['nomarkup_body'],
				'_date': email_recieved['date'],
				'images': images,
				'replies': email_replies,
				'hasreply': 0,
				'hasimage': hasimage,
				})
		#if there are more than two cards currently loaded
		if len(self.rv.box.children) > 3:
			self.find_last() # scroll to the last card
		eNum -= 1

	def load_card(self, dict):
		new_card = Card()
		new_card.msg_id=dict['msg_id']
		new_card._from=dict['_from']
		new_card.email=dict['email']
		new_card.subject=dict['subject']
		new_card.body=dict['body']
		new_card.nomarkup_body=dict['nomarkup_body']
		new_card._date=dict['_date']
		new_card.images=dict['images']
		new_card.replies=dict['replies']
		new_card.hasreply=dict['hasreply']
		new_card.hasimage=dict['hasimage']
		for i in dict['replies']:
			new_reply = ReplyCard()
			new_reply.msg_id=i['msg_id']
			new_reply._from=i['_from']
			new_reply.email=i['email']
			new_reply.subject=i['subject']
			new_reply.body=i['body']
			new_card.replybox.add_widget(new_reply)
		self.rv.box.add_widget(new_card)

	def option_menu(self, x):
		x.dropdown = Options()
		x.dropdown.open(x)
		x.dropdown.BuildList(self)

	def share_post(self, sub, body):
		self.openhere.post_card = PostCard()
		self.openhere.post_card.open(self.openhere)
		self.openhere.post_card.text_sub.text = sub
		self.openhere.post_card.text_body.text = body

	def post_card(self, x):
		x.post_card = PostCard()
		x.post_card.open(x)
		x.post_card.text_sub.focus = True

class ConnectPage(GridLayout):
	# runs on initialization
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		try:
			with open("../prev_details.txt","r") as f:
				d = f.read().split(",")
				f.close()
				if len(d) == 7:
					global imap_host
					global imap_port
					global imap_hostS
					global imap_portS
					global imap_user
					global imap_pass
					imap_host = d[0]
					imap_port = d[1]
					imap_hostS = d[2]
					imap_portS = d[3]
					imap_user = d[4]
					encoded = d[5]
					imap_pass = base64.b64decode(encoded).decode("utf-8")
					social_app.send_name = d[6]
				if len(d) != 7:
					print("old login data found, discarding...")
		except:
			print("No prev text found")
		try:
			with open("resources/fav_emoji.txt","r") as f:
				d = f.read().split(",")
				f.close()
				global fav_emoji
				fav_emoji = d
		except:
			print("No emoji favorites found")
		try:
			with open("../custom_servers.txt","r") as f:
				s = f.read()
				f.close()
				global smtp_servers
				smtp_servers = eval(s)
				print(smtp_servers)
		except:
			print("No custom servers found")
		try:
			with open(f"../contact_books{imap_user}.txt","r") as f:
				s = f.read()
				f.close()
				global contact_books
				contact_books = eval(s)
				print(contact_books)
		except:
			print("No Contact Books found")

		self.serverlabel = Label(text=('📡 ' + imap_host),size_hint_x= 0.5)
		self.add_widget(self.serverlabel)

		self.mainbutton = Button(text="Change Sever")
		self.mainbutton.bind(on_release=lambda instance: self.open_dropdown(instance))
		self.add_widget(self.mainbutton)

		self.add_widget(Label(text=u'Display Name:', size_hint_x=0.5))
		self.send_name = TextInput(text=social_app.send_name, halign='center', multiline=False, write_tab=False, hint_text='optional')
		self.send_name.name = 'name'
		self.send_name.bind(text = self.calc)
		self.send_name.bind(on_text_validate = self.focus_text_input)
		self.add_widget(self.send_name)

		self.add_widget(Label(text=u'💌 Email:', size_hint_x=0.5))
		self.username = TextInput(text=imap_user, halign='center', multiline=False, write_tab=False, hint_text='enter email')
		self.username.name = 'username'
		self.username.bind(text = self.calc)
		self.username.bind(on_text_validate = self.focus_text_input)
		self.add_widget(self.username)

		self.add_widget(Label(text=u'🔓 Password:', size_hint_x=0.5))
		self.user_pass = TextInput(text=imap_pass, halign='center', multiline=False, password=True, write_tab=False, hint_text='enter password')
		self.user_pass.name = 'user_pass'
		self.user_pass.bind(text = self.calc)
		self.user_pass.bind(on_text_validate = self.login_button)
		self.add_widget(self.user_pass)

		self.aboutbox = BoxLayout(size_hint_x=0.5)
		self.add_widget(self.aboutbox)
		self.aboutbox.ab = Button(text='ℹ️ About')
		self.aboutbox.ab.bind(on_release=self.about)
		self.aboutbox.add_widget(self.aboutbox.ab)
		self.aboutbox.add_widget(Label())
		self.login = Button(text="Secure Login")
		self.login.bind(on_release=self.login_button)
		self.add_widget(self.login)

		self.server = imap_host
		self.logo = Image(source='icon128.png',size_hint_y=5,size_hint_x=0.5)
		self.add_widget(self.logo)
		self.statement = Label(text=intro_text,size_hint_y=5,halign='center')
		self.statement.width = self.statement.texture_size[0]
		self.add_widget(self.statement)
		#TODO Auto login creates visual bug on android
		#if imap_pass != '':
			#Clock.schedule_once(self.login_button, 2)
		#Clock.schedule_once(self.focus_text_input, 0.1)

	# Sets focus to text input field
	def focus_text_input(self, _):
		self.user_pass.focus = True
		if self.username.text != '':
			self.user_pass.focus = True

	def about(self, x):
		print('clicked')
		social_app.screen_manager.current = 'About'

	def open_dropdown(self, x):
		print('hello')
		x.dropdown = ImapDropDown()
		x.dropdown.open(x)
		x.dropdown.BuildList(x)
		x.dropdown.bind(on_select=lambda instance, x: self.RefreshServer(x))

	def calc(self, _, text):
		global imap_host
		global imap_port
		global imap_hostS
		global imap_portS
		global imap_user
		global imap_pass
		if _.name == 'imapS':
			imap_hostS = text
			print(text)
		if _.name == 'portS':
			imap_portS = text
		if _.name == 'imap':
			imap_host = text
		if _.name == 'port':
			imap_port = text
		if _.name == 'name':
			social_app.send_name = text
		if _.name == 'username':
			imap_user = text
		if _.name == 'user_pass':
			imap_pass = text

	def login_button(self, instance):
		#TODO theme
		#with open("theme/theme_current.txt","w") as f:
			#f.write(f"{color_button},{color_text_input},{color_background},{color_background_info},{color_scroll_bar},{color_card},{color_card_from_text},{color_card_sub_text},{color_card_body_background}")
		# Create info string, update InfoPage with a message and show it
		info = f"One moment please, {imap_user}..."
		social_app.info_page.update_info(info)
		social_app.screen_manager.current = 'Info'
		Clock.schedule_once(self.connect, 1)

	# Connects to the server
	def connect(self, _):
		print(imap_host, imap_port, imap_user, imap_pass)
		if not SMail._login(imap_host, imap_port, imap_user, imap_pass):
			social_app.screen_manager.current = 'Connect'
			return
		# Save log in details (no pass)
		with open("../prev_details.txt","w") as f:
			encoded = base64.b64encode(imap_pass.encode("utf-8"))
			encoded = str(encoded, "utf-8")
			f.write(f"{imap_host},{imap_port},{imap_hostS},{imap_portS},{imap_user},{encoded},{social_app.send_name}")
		with open("../custom_servers.txt","w") as f:
			f.write(str(smtp_servers))

		# Create chat page and activate it
		if not social_app.screen_manager.has_screen('Scroll'):
			social_app.create_scroll_page()
		social_app.screen_manager.current = 'Scroll'

	def RefreshServer(self, text):
		self.serverlabel.text = text[0]
		self.serverlabel.canvas.ask_update()
		print('refreshing', text, self.serverlabel.text)

class UserConnectPage(GridLayout):
	# runs on initialization
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		global imap_host
		global imap_port
		global imap_hostS
		global imap_portS
		global imap_user
		global imap_pass
		try:
			with open("../prev_details.txt","r") as f:
				d = f.read().split(",")
				if len(d) == 7:
					imap_host = d[0]
					imap_port = d[1]
					imap_hostS = d[2]
					imap_portS = d[3]
					imap_user = d[4]
					encoded = d[5]
					imap_pass = base64.b64decode(encoded).decode("utf-8")
					social_app.send_name = d[6]
				if len(d) != 7:
					print("old login data found, discarding...")
		except:
			print("No prev text found")
		self.server = imap_host

		self.add_widget(Label(text='Return:'))  # widget #1, top left

		self.mainbutton = Button(text='Server Select')
		self.mainbutton.bind(on_release=self.Return)
		self.add_widget(self.mainbutton)

		self.imapRow = (BoxLayout())
		self.add_widget(self.imapRow)
		self.imapRow.add_widget(Label(text='📡 SMTP Host:'))  # widget #1, top left
		self.imapRow.ip = TextInput(text=imap_host, multiline=False, write_tab=False)  # defining self.ip...
		self.imapRow.ip.name = 'imap'
		self.imapRow.ip.bind(text = self.calc)
		self.imapRow.add_widget(self.imapRow.ip) # widget #2, top right

		self.portRow = (BoxLayout())
		self.add_widget(self.portRow)
		self.portRow.add_widget(Label(text='📲 SMTP Port:'))
		self.portRow.port = TextInput(text=imap_port, multiline=False, write_tab=False)
		self.portRow.port.name = 'port'
		self.portRow.port.bind(text = self.calc)
		self.portRow.add_widget(self.portRow.port)

		self.imapSRow = (BoxLayout())
		self.add_widget(self.imapSRow)
		self.imapSRow.add_widget(Label(text='📡 IMAP Host:'))  # widget #1, top left
		self.imapSRow.imapS = TextInput(text=imap_hostS, multiline=False, write_tab=False)  # defining self.ip...
		self.imapSRow.imapS.name = 'imapS'
		self.imapSRow.imapS.bind(text = self.calc)
		self.imapSRow.add_widget(self.imapSRow.imapS) # widget #2, top right

		self.portSRow = (BoxLayout())
		self.add_widget(self.portSRow)
		self.portSRow.add_widget(Label(text='📲 IMAP port:'))
		self.portSRow.portS = TextInput(text=imap_portS, multiline=False, write_tab=False)
		self.portSRow.portS.name = 'portS'
		self.portSRow.portS.bind(text = self.calc)
		self.portSRow.add_widget(self.portSRow.portS)

		self.add_widget(Label(text=u'Display Name:', size_hint_x=0.5))
		self.send_name = TextInput(text=social_app.send_name, halign='center', multiline=False, write_tab=False, hint_text='optional')
		self.send_name.name = 'name'
		self.send_name.bind(text = self.calc)
		self.add_widget(self.send_name)

		self.add_widget(Label(text='💌 Email:'))
		self.username = TextInput(text=imap_user, multiline=False, write_tab=False)
		self.username.name = 'username'
		self.username.bind(text = self.calc)
		self.add_widget(self.username)

		self.add_widget(Label(text='🔓 Password:'))
		self.user_pass = TextInput(text=imap_pass, multiline=False, password=True, write_tab=False)
		self.user_pass.name = 'user_pass'
		self.user_pass.bind(text = self.calc)
		self.add_widget(self.user_pass)

		# add our button.
		self.login = Button(text="Secure Login")
		self.login.bind(on_release=self.login_button)
		self.add_widget(Label())  # just take up the spot.
		self.add_widget(self.login)

	def UpdateImap(self):
		self.imapRow.ip.text = imap_host
		self.portRow.port.text = imap_port
		self.imapSRow.imapS.text = imap_hostS
		self.portSRow.portS.text = imap_portS
		self.username.text = imap_user
		self.user_pass.text = imap_pass

	def calc(self, _, text):
		global imap_host
		global imap_port
		global imap_hostS
		global imap_portS
		global imap_user
		global imap_pass
		if _.name == 'imapS':
			imap_hostS = text
			print(text)
		if _.name == 'portS':
			imap_portS = text
		if _.name == 'imap':
			imap_host = text
		if _.name == 'port':
			imap_port = text
		if _.name == 'name':
			social_app.send_name = text
		if _.name == 'username':
			imap_user = text
		if _.name == 'user_pass':
			imap_pass = text

	def login_button(self, instance):
		with open("theme/theme_current.txt","w") as f:
			f.write(f"{color_button},{color_text_input},{color_background},{color_background_info},{color_scroll_bar},{color_card},{color_card_from_text},{color_card_sub_text},{color_card_body_background}")
		# Create info string, update InfoPage with a message and show it
		info = f"One moment please, {imap_user}..."
		social_app.info_page.update_info(info)
		social_app.screen_manager.current = 'Info'
		Clock.schedule_once(self.connect, 1)

	# Connects to the server
	def connect(self, _):
		print(imap_host, imap_port, imap_user, imap_pass)
		if not SMail._login(imap_host, imap_port, imap_user, imap_pass):
			social_app.screen_manager.current = 'UserConnect'
			return
		# Save log in details (no pass)
		with open("../prev_details.txt","w") as f:
			encoded = base64.b64encode(imap_pass.encode("utf-8"))
			encoded = str(encoded, "utf-8")
			f.write(f"{imap_host},{imap_port},{imap_hostS},{imap_portS},{imap_user},{encoded},{social_app.send_name}")
			f.close()
		with open("../custom_servers.txt","w") as s:
			smtp_servers.append([imap_host, imap_port, imap_hostS, imap_portS, imap_folder, imap_sent])
			s.write(str(smtp_servers))
			s.close()
		# Create chat page and activate it
		social_app.create_scroll_page()
		social_app.screen_manager.current = 'Scroll'

	def Return(self, _):
		social_app.screen_manager.current = 'Connect'

class AboutPage(GridLayout):
	def connect(self):
		social_app.screen_manager.current = 'Connect'

# InfoPage is a seperate script

class SocialApp(App):
	send_sub = 'test'
	send_body = ''
	send_name = ''
	def build(self):
		# We are going to use screen manager, so we can add multiple screens
		# and switch between them
		self.screen_manager = ScreenManager(transition = WipeTransition())
		# Initial, connection screen (we use passed in name to activate screen)
		# First create a page, then a new screen, add page to screen and screen to screen manager
		self.connect_page = ConnectPage()
		screen = Screen(name='Connect')
		screen.add_widget(self.connect_page)
		self.screen_manager.add_widget(screen)

		self.user_connect_page = UserConnectPage()
		screen = Screen(name='UserConnect')
		screen.add_widget(self.user_connect_page)
		self.screen_manager.add_widget(screen)

		self.about_page = AboutPage()
		screen = Screen(name='About')
		screen.add_widget(self.about_page)
		self.screen_manager.add_widget(screen)

		self.contact_page = ContactPage()
		screen = Screen(name='Contacts')
		screen.add_widget(self.contact_page)
		self.screen_manager.add_widget(screen)

		# Info page
		self.info_page = InfoPage()
		screen = Screen(name='Info')
		screen.add_widget(self.info_page)
		self.screen_manager.add_widget(screen)
		return self.screen_manager

	# We cannot create chat screen with other screens, as it;s init method will start listening
	# for incoming connections, but at this stage connection is not being made yet, so we
	# call this method later
	def create_scroll_page(self):
		self.scroll_page = ScrollPage()
		screen = Screen(name='Scroll')
		screen.add_widget(self.scroll_page)
		self.screen_manager.add_widget(screen)

# Error callback function, used by sockets client
# Updates info page with an error message, shows message and schedules exit in 10 seconds
# time.sleep() won't work here - will block Kivy and page with error message won't show up
def show_error(message):
	social_app.info_page.update_info(message)
	social_app.screen_manager.current = 'Info'
	Clock.schedule_once(sys.exit, 10)

if __name__ == "__main__":
	social_app = SocialApp()
	social_app.run()
