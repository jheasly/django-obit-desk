===========
Django Obit
===========

This Django app is in major flux, but its aim is allow area funeral homes 
to supply a given local newspaper with clean, reliable death notice and 
obituary information that can be quickly and easily formatted and distributed 
both online and in print. A few Adobe InDesign templates are included as 
examples.

Add this to your urls.py:
(r'^add/(?P<model_name>\w+)/$', 'obituary.views.add_new_model'),

Make sure you can send out an e-mail. (Elsewise, it'll bust on save().)

===========
Immediate To Do
===========
- Preceded in death (by wife). <- create logic for; if spouse death date
- is length of relationship ever used?
- serial comma on survivor lists; if 2, merge items, if >2, merge items -2 and -1
- Live/draft status on User's index page.

===========
Other To Do
===========
- Form factory for FH index view?
- Be able to tell a Obituary save from a Death Notice save for e-mail notification purposes.
- Move e-mail addresses to settings.

===========
Odd Areas
===========
- "Length of residence in Lane County area:"
- "Length of relationship:"
- What do outside-of-area folk do?
