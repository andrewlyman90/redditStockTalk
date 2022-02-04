# production.wsgi
import sys
 
sys.path.insert(0,"/var/www/html/redditStockTalk/")
 
from flaskTest import app as application
