DISPLAY_DAYS_BACK = 45

DATABASE_DAYS_BACK = 100

#
# list of recipients of Obituary app e-mails
#
DN_OBIT_EMAIL_RECIPIENTS = [
#    'recipient@domain.com', 
]

try:
    from local_obituary_settings import *
except ImportError, e:
# Commented out error as it was being output during a dumpdata and 
# corrupting the .json data file.
#
#     print 'Unable to load local_obituary_settings.py:', e
    pass
