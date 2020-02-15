# What is SocialMail?

A social media network, where *you* are the network.

Unlike other social networking apps:
* SocialMail does not use it's own server.
* Does not collect any user information.
* Does not control any data you choose to share.

SocialMail aims to replicate all the popular features of other social media networks, without a centralized server. Messages are sent and recieved via a standard email account, everything else is handled locally by the app. 'Posts' are displayed in an endless scrolling page, with pictures, sharing, and comments. Replies are displayed as comments, messages can be shared with everyone in your contact book, or select lists like "Family" or "Friends."

# Why SocialMail?

SocialMail contains:
* No advertising.
* No Data collection.
* No "Algorythims" deciding what you do, or don't see.

The beauty of SocialMail is that it does not require a 'network.' You can send and recieve messages to and from anyone you have an email address for, without requiring them to use the app. Posts you make will be standard emails for them, and any reply they send, will be displayed as a comment on your post. Never again ask "is anyone else even using this thing?" No need to concern over "I like this app, but none of my friends will use it!" SocialMail may be the first social media app that is truely network indipendant.

# Who is SocialMail?

You are.

SocialMail takes a hard line on user privacy. No information is sent to a third party at any time. SocialMail developers consider themselves to be a third party, you and your email server are the only parties involved with your personal information. When SocialMail is running on your device, You are SocialMail. Login information for your email server is stored locally, as are contacts, everything else is stored on your email server. That server can be a popular free server, like gmail or outlook, or it can be a private email server hosted online or in your own home. Your privacy is exactly where it should be, in your own hands.

Additionally, your contacts information is never shared directly. When someone replies to one of your posts, only you will see it, unless you choose to share that reply. Even then, email addresses are never shared, only names. If someone in your contacts wants to contact a friend or family member, they will have to ask you to forward their contact infromation. For thousands of years we called this an Introduction.

# How, is SocialMail?

SocialMail began as an idea, as all things do. Ideally, it could have been built on top of an existing email client. Unfortunately, open source and multi-platform email clients are like unicorns. A program had to be built from scratch.

SocialMail is built with Python, and the open source Kivy module for designing natural user interfaces, and uses IMAP and SMTP protocols to access an email server. From there it displays emails, identifies and sorts replies.

SocialMail development follows a number of design Pillars:
* inter-communication with any other email client: Messages must be standard emails wherever possible, with little to no SocialMail specific encoding or headers.
* As little imformation as possible stored on the device: local copies of emails are not stored, email references must be pulled from the email itself, and not stored as a local database. Login information, and contacts are the only currently allowed exception.
* Zero communication with any third party: no data collection of any kind, not even basic user statistics or number of users.
* Safeguarding contact data: no contact data is ever shared with a recipient, all emails are sent as blind cc, only the username associated with an incoming message will be shared, if the user chooses to share that message/reply.
* Zero advertising: even incmming html emails are stripped down to text for ease of reading. Only direct sharing of pictures and videos will be supported. 

# Beta means Not Finished
SocialMail is still in an expermental state and not ready for public use. Primary features are still missing, information storage is subject to change, and while the alpha has been fairly stable, as we transition to a beta release, it's still "use at your own risk."
