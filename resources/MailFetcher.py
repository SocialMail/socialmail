# -*- coding: utf-8 -*-

import imaplib
import smtplib
import pprint
import base64
import email
import html
import io
import re
import kivy
import secrets
from email.utils import make_msgid
from imaplib import IMAP4
from imaplib import IMAP4_SSL
from smtplib import SMTP
from email import policy
from email.header import Header, decode_header, make_header
from kivy.uix.image import Image, CoreImage
from email.mime.image import MIMEImage
from bs4 import BeautifulSoup

encription_warning = "[Message not found: This email may be encrypted for your security. SocialMail does not currently feature end to end encryption.]"

ids_list = []

class SMail():
	def _read_mail(imap_host, imap_port, imap_user, imap_pass, imap_folder, eNum): # reads the most recent email and parses the text
		### Reading emails from the server. The bulk of the logic is here
		### We prosses an email, clean up the text, check if it is a reply
		### If the message is a reply, search for the original email in the sent box
		### If the original email exists, run a search on the inbox for all emails replying to the original
		### And finally, check for and load images
		global ids_list
		if eNum == -1:
			ids_list = []
		email_recieved = {
			'alreadyLoaded' : False
			}
		try:
			imap = IMAP4_SSL(imap_host, imap_port)
			## login to server
			print(imap_user, imap_pass)
			imap.login(imap_user, imap_pass)
			#imap.ehlo()
			#imap.starttls()
		except:
			print("Failed to login")
			return False
		#print(imap.list()) # for identifying mailboxes on the server
		imap.select()
		result, data = imap.uid('search', None, "ALL") # search and return uids instead
		#print('data', data)
		if -len(data[0].split()) > eNum:
			return False
		current_email_uid = data[0].split()[eNum]
		print('current', current_email_uid)
		result, data = imap.uid('fetch', current_email_uid, '(RFC822)') # fetch the email headers and body (RFC822) for the given ID
		raw_email = data[0][1] # here's the body, which is raw headers and html and body of the whole email
		b = email.message_from_bytes(raw_email, policy=email.policy.default)
		email_recieved['msg_id'] = b['Message-ID']
		for i in ids_list:
			if i == email_recieved['msg_id']:
				print("mail already loaded")
				email_recieved['alreadyLoaded'] = True
				return email_recieved
		ids_list.append(email_recieved['msg_id'])
		print(email_recieved['msg_id'])
		email_recieved['date'] = b['Date']
		if email_recieved['date'] == None:
			email_recieved['date'] = b['Delivery-date']
		email_recieved['inreply'] = b['in-reply-to']
		email_recieved['refs'] = b['references']
		# decode and clean the name out of the From header
		email_from = b['from']
		# get just the text
		frm = BeautifulSoup(email_from, 'html.parser')
		frm = frm.get_text()
		# remove any latent escape chrs
		frm = make_header(decode_header(frm))
		# remove unneccisary quotes
		frm = str(frm).replace('"', '')
		# add result to list
		email_recieved['from'] = str(frm)
		# find all email addresses in the From header
		add1 = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(email_from))
		email_recieved['email'] = add1 # is a list
		# clean the subject text
		email_subject = b['Subject']
		try:
			sub = make_header(decode_header(email_subject))
		except:
			sub = email_subject
		email_recieved['subject'] = str(sub)
		# find and clean up the body text
		email_body = b.get_payload(decode=True)
		if b.is_multipart(): # search for text in the body
			for part in b.walk():
				ctype = part.get_content_type()
				cdispo = str(part.get('Content-Disposition'))
				if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
					email_body = part.get_payload(decode=True)
					#print(email_body)
					break
		# Use beautifulsoup to get readable text
		try: # Try parsing the body text
			body = BeautifulSoup(email_body, 'html.parser')
		except: # if email is encrypted it will throw an exception
			 body = encription_warning
		if body != encription_warning:
			for script in body(["script", "style", "div", "div style"]):
				script.extract() # rip it out
			text = body.get_text()
			urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
			# replace and remove leftover html escape chrs, bad wiziwig
			text = text.replace('=0A', '\n')
			text = text.replace('=20', '\n')
			text = text.replace('=\r\n', '')
			text = text.replace('=\n', '')
			text = text.replace('=C2=A0', '')
			text = text.replace('=C2=A9', '')
			text = text.replace('=09','')
			text = text.replace('=0D','')
			text = text.replace('<td>','')
			text = text.replace('</td>','')
			text = text.replace('<tr>','')
			text = text.replace('</a>','')
			# break into lines and remove leading and trailing space on each
			lines = (line.strip() for line in text.splitlines())
			# drop blank lines
			text = '\n'.join(line for line in lines if line)
			# double space new lines
			text = text.replace('\n', '\n\n')
			email_recieved['nomarkup_body'] = text
			for i in urls:
				text = text.replace(i, f"[ref=<{i}>][color=6666FF][u]{i}[/u][/color][/ref]")
		email_recieved['body'] = text
		imap.close()
		return email_recieved

	def _read_source(imap_host, imap_port, imap_user, imap_pass, imap_folder, email_inreply):
		source = {
			'alreadyLoaded' : False
			}
		try: ## Time to search for the original email
			try:
				if "gmail" in imap_host: # gmail server requires an ssl connection
					print("gmail server")
					imap = IMAP4_SSL(imap_host, imap_port)
				else:
					imap = IMAP4_SSL(imap_host, imap_port)
				## login to server
				#print(imap_user, imap_pass)
				imap.login(imap_user, imap_pass)
				#imap.starttls()
			except:
				print("Failed to login")
				return False
			# while 'INBOX' is standard, many email servers use different methods to label the Sent folder
			# We have to iterate through the most common methods to find the right one
			if "gmail" in imap_host:
				imap.select('"[Gmail]/Sent Mail"') # connect to sent mail.
				# Search for the original email ID
				messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
				#print("Opening gmail 'Sent'")
			if 'gmail' not in imap_host:
				sentbox = False
				try:
					imap.select('Sent') # connect to sent mail.
					# Search for the original email ID
					messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
					sentbox = True
				except:
					print('Sent folder not found')
				if sentbox == False:
					try:
						imap.select('INBOX.Sent') # connect to sent mail.
						# Search for the original email ID
						messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
					except:
						print('Inbox.Sent folder not found, no folders left to try')
			# Process the result to get the message id’s
			messages = messages[1][0].split()
			# Use the first id to view the headers for a message
			result, source_data = imap.fetch(messages[0], '(RFC822)')
			#print("Opening 'Sent'", messages[0])
			raw_source = source_data[0][1] # here's the body, which is raw headers and html and body of the whole email
			s = email.message_from_bytes(raw_source) # convert to message object
			source_subject = s['subject']
			print(source_subject)
			frm = s['From']
			add1 = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(frm))
			source['email'] = add1
			if s['Date'] != None:
				source['_date'] = s['Date']
			if s['Delivery-date'] != None:
				source['_date'] = s['Delivery-date']
			source['bcc'] = ''
			if s['bcc'] != None:
				print("bcc is: ",s['bcc'])
				source['bcc'] = s['bcc'].split(',')
			source['msg_id'] = s['Message-ID']
			#print("BCC from source: ", source_bcc)
			source_body = s.get_payload(decode=True)
			if s.is_multipart(): # search for text in the body
				for part in s.walk():
					ctype = part.get_content_type()
					cdispo = str(part.get('Content-Disposition'))
					if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
						source_body = part.get_payload(decode=True)
						#print(email_body)
						break
			src_sub = BeautifulSoup(source_subject, 'html.parser')
			src_from = BeautifulSoup(frm, 'html.parser')
			try: # extra check for encryption (in case user has encypted email)
				src_body = BeautifulSoup(source_body, 'html.parser')
				text = src_body.get_text()
				urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
				# break into lines and remove leading and trailing space on each
				lines = (line.strip() for line in text.splitlines())
				# drop blank lines
				text = '\n'.join(line for line in lines if line)
				# double space new lines
				text = text.replace('\n', '\n\n')
				source['nomarkup_body'] = text
				for i in urls:
					text = text.replace(i, f"[ref=<{i}>][color=6666FF][u]{i}[/u][/color][/ref]")
				source['body'] = text #.encode('utf-8')
			except: # if email is encrypted it will throw an exception
				source['body'] = encription_warning
			source['from'] = src_from.get_text().split('@')[0]
			source['subject'] = src_sub.get_text()
			ids_list.append(source['msg_id'])
			return source
		except:
			print("no origin found")
			return False

	def _find_replies(imap_host, imap_port, imap_user, imap_pass, imap_folder, email_inreply):
		try:
			# On to find more emails that may be replies to email_in_reply
			replies_list = []
			try:
				if "gmail" in imap_host: # gmail server requires an ssl connection
					print("gmail server")
					imap = IMAP4_SSL(imap_host, imap_port)
				else: # tls is preferred
					imap = IMAP4_SSL(imap_host, imap_port)
				## login to server
				#print(imap_user, imap_pass)
				imap.login(imap_user, imap_pass)
				#imap.starttls()
			except:
				print("Failed to login")
				return False
			imap.select()
			replies = imap.search(None, 'HEADER', 'IN-REPLY-TO', email_inreply)
			# BODY.PEEK[HEADER.FIELDS (SUBJECT)]
			print("searched inbox for ", email_inreply)
			# Process the result to get the message id’s
			replies = replies[1][0].split()
			print("got list of replies")
			# Use the first id to view the headers for a message
			for i in replies:
				reply = {}
				print("Checking list of replies")
				result, reply_data = imap.fetch(i, '(RFC822)')
				print("loaded a reply")
				raw_reply = reply_data[0][1] # here's the body, which is raw headers and html and body of the whole email
				#print("raw reply")
				r = email.message_from_bytes(raw_reply) # convert to message object
				#reply_to = r['in-reply-to']
				reply['refs'] = r['references']
				print("references", reply['refs'])
				reply_from = r['from']
				reply_email = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(reply_from))
				reply['_date'] = r['Date']
				reply['subject'] = r['Subject']
				reply['msg_id'] = r['Message-ID']
				ids_list.append(reply['msg_id'])
				reply_body = r.get_payload(decode=True)
				if r.is_multipart(): # search for text in the body
					for part in r.walk():
						ctype = part.get_content_type()
						cdispo = str(part.get('Content-Disposition'))
						if ctype == ('text/plain' or 'text/html') and 'attachment' not in cdispo:
							reply_body = part.get_payload(decode=True)
							#print(email_body)
							break
				rep_from = BeautifulSoup(reply_from, 'html.parser')
				reply['email'] = reply_email[0]
				reply['_from'] = rep_from.get_text().split('@')[0]
				try: # extra check for encryption (in case user has encypted email)
					rep_body = BeautifulSoup(reply_body, 'html.parser')
					text = rep_body.get_text()
					# break text into lines, and remove leading and trailing space on each
					# make a tuple to prevent unexpected data loss when reading
					lines = tuple(line.strip() for line in text.splitlines())
					new_lines = []
					# create a list we can reverse
					for line in lines:
						new_lines.append(line)
					new_lines.reverse()

					### clean '>' qoutes from email replies, and the 'On ~date' message
					count = 0
					# create a new list to add non-qouted lines to
					removed_qoutes = []
					for line in new_lines:
						#create a copy of the line
						new_line = line
						# check only two lines beyond last '>' found
						if count < 3:
							# first letter
							for i in new_line:
								if i == '>':
									new_line = ''
									print('found ', line)
									count = 0
									break
								count += 1
								break
						if new_line != '':
							# add any other lines to new list
							removed_qoutes.append(line)
					# put the lines back in order
					removed_qoutes.reverse()
					print(removed_qoutes)
					# drop blank lines and join back to a string
					text = '\n'.join(line for line in removed_qoutes if line)
					# if less than 20 lines, double space new lines
					text = text.replace('\n', '\n\n')
					urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
					reply['nomarkup_body'] = text
					for i in urls:
						text = text.replace(i, f"[ref=<{i}>][color=6666FF][u]{i}[/u][/color][/ref]")
					# text is now ready
					reply['body'] = text
				except: # if email is encrypted it will throw an exception
					reply['body'] = encription_warning
				#print("Hello! I am found, ")
				replies_list.append(reply)
			return replies_list
		except:
			return False
			print("No more replies found.")

	## Check for image attachments
	def _read_images(imap_host, imap_port, imap_user, imap_pass, imap_folder, message_ID): # reads the most recent email and parses the text
		try: ## Time to search for the original email
			try:
				imap = IMAP4_SSL(imap_host, imap_port)
				## login to server
				imap.login(imap_user, imap_pass)
				#imap.starttls()
			except:
				print("Failed to login")
				return False
			try:
				imap.select()
				# Search for the original email ID
				messages = imap.search(None, 'HEADER', 'MESSAGE-ID', message_ID)
				# Process the result to get the message id’s
				messages = messages[1][0].split()
				# Use the first id to view the headers for aroot.image message
				result, source_data = imap.fetch(messages[0], '(RFC822)')
				raw_source = source_data[0][1] # here's the body, which is raw headers and html and body of the whole email
				b = email.message_from_bytes(raw_source) # convert to message object
				print('checking images now')
				images = [{'name': 'icon128.png', 'pic': CoreImage('icon128.png', ext="png").texture}]
				for part in b.walk():
					image = {}
					ctype = part.get_content_type()
					if ctype in ['image/jpeg', 'image/png', 'image/gif']:
						# un-comment to save file
						#open(part.get_filename(), 'wb').write(part.get_payload(decode=True))
						by = io.BytesIO(part.get_payload(decode=True))
						by.seek(0)
						image['name'] = part.get_filename()
						image['pic'] = CoreImage(by, ext="png").texture
						print(image)
						# Below line is for saving to disk
						images.append(image)
						print('appended')
				return images
			except:
				print('not in inbox')
			if "gmail" in imap_host:
				imap.select('"[Gmail]/Sent Mail"') # connect to sent mail.
				# Search for the original email ID
				messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
				#print("Opening gmail 'Sent'")
			if 'gmail' not in imap_host:
				sentbox = False
				try:
					imap.select('Sent') # connect to sent mail.
					# Search for the original email ID
					messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
					sentbox = True
				except:
					print('Sent folder not found')
				if sentbox == False:
					try:
						imap.select('INBOX.Sent') # connect to sent mail.
						# Search for the original email ID
						messages = imap.search(None, 'HEADER', 'MESSAGE-ID', email_inreply)
					except:
						print('Inbox.Sent folder not found, no folders left to try')
			# Process the result to get the message id’s
			messages = messages[1][0].split()
			# Use the first id to view the headers for aroot.image message
			result, source_data = imap.fetch(messages[0], '(RFC822)')
			raw_source = source_data[0][1] # here's the body, which is raw headers and html and body of the whole email
			b = email.message_from_bytes(raw_source) # convert to message object
			print('checking images now')
			images = [{'name': 'icon128.png', 'pic': CoreImage('icon128.png', ext="png").texture}]
			for part in b.walk():
				image = {}
				ctype = part.get_content_type()
				if ctype in ['image/jpeg', 'image/png', 'image/gif']:
					# un-comment to save file
					#open(part.get_filename(), 'wb').write(part.get_payload(decode=True))
					by = io.BytesIO(part.get_payload(decode=True))
					by.seek(0)
					image['name'] = part.get_filename()
					image['pic'] = CoreImage(by, ext="png").texture
					print(image)
					# Below line is for saving to disk
					images.append(image)
					print('appended')
			return images
		except:
			print('no images found')
			images = [{'name': 'icon128.png', 'pic': CoreImage('icon128.png', ext="png").texture}]
			return images

	def _sending_mail(name, imap_host, imap_port, imap_user, imap_pass, imap_to, subject, message, reply_to):
		print("recieving")
		imap = SMTP(imap_host, imap_port)
		## login to server
		# some servers require tls before login
		if 'gmail' in imap_host:
			imap.starttls()
		imap.login(imap_user, imap_pass)
		# create html safe unicode chrs, for sending emoji
		subject = Header(subject,'utf-8').encode()
		message = html.escape(message).encode('ascii', 'xmlcharrefreplace').decode()
		# can add a custom SocialMail: header for tracking and organizing reply chains, if neccisary
		msg = ("Content-Type: text/html; charset=UTF-8; format=flowed" + "\r\nFrom: " + name + ' <' + imap_user + '>' + "\r\nTo: " + " " + "\r\nMessage-ID: " + make_msgid() + "\r\nIn-Reply-To: " + reply_to + "\r\nSubject: "+ subject +"\r\n\n"+ message)
		print(type(imap_to), imap_to)
		try:
			imap.sendmail(imap_user, imap_to, msg)
			imap.quit()
			print("Mail sent")
			return True
		except:
			print("Failed to send mail")
			return False

	def _imap_login(imap_host, imap_port, imap_user, imap_pass):
		try:
			if "gmail" in imap_host: # gmail server requires an ssl connection
				print("gmail server")
				imap = IMAP4_SSL(imap_host, imap_port)
			else: # tls is preferred
				imap = IMAP4(imap_host, imap_port)
				imap.starttls()
			## login to server
			print(imap_user, imap_pass)
			imap.login(imap_user, imap_pass)
			return True
		except:
			print("Failed to login")
			return False

	def _login(imap_host, imap_port, imap_user, imap_pass):
		print("Logging in ", imap_host, imap_port)
		imap = SMTP(imap_host, imap_port)
		#some servers require tls before login
		if 'gmail' in imap_host:
			imap.starttls()
		try:
			print('trying ', imap_user, imap_pass)
			imap.login(imap_user, imap_pass)
		except:
			print("log in failed")
			return False
		print("Successfully logged in")
		return True
