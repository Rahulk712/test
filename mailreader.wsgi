# =====================
# wsgi.py file begin

import os, sys
# add the mailreader project path into the sys.path
sys.path.append('/home/mailreader/public_html/mail_reader')

# add the virtualenv site-packages path to the sys.path
sys.path.append('/home/mailreader/public_html/mailreader_env/lib/python3.9/site-packages')

# poiting to the project settings
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailreader.settings")
os.environ['DJANGO_SETTINGS_MODULE'] = 'mail_reader.settings'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


# wsgi.py file end
# =================
















