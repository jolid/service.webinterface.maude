import time, sys, os, re
import string,cgi,time
from os import curdir, sep
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import xbmc
import xbmcaddon
try: 
	import simplejson as json
                                                                                                                                                                                                                                                        
except ImportError: 
	import json  

WEB_ROOT = '.'
DB = None
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global WEB_ROOT
		global DB
		parts = urlparse(self.path)
		try:
			path = parts.path
			query = parts.query
			data = cgi.parse_qs(query, keep_blank_values=True)
			if path == '/query/':
				if data['method'][0] == 'subscriptions':
					self.send_response(200)
					self.send_header('Content-type',	'application/json')
					self.end_headers()
					rows = DB.query("SELECT rw_subscriptions.subscriptionid, rw_subscriptions.showid, rw_shows.showname, rw_subscriptions.enabled FROM rw_subscriptions JOIN rw_shows on rw_subscriptions.showid=rw_shows.showid ORDER BY rw_shows.showname ASC")
					self.wfile.write(json.dumps(rows))
				elif data['method'][0] == 'search':
					rows = DB.query("SELECT rw_shows.showname, rw_shows.showid, rw_subscriptions.enabled FROM rw_shows LEFT JOIN rw_subscriptions ON rw_shows.showid=rw_subscriptions.showid WHERE rw_shows.showname REGEXP ? ORDER BY rw_shows.showname ASC", [data['s'][0]])	
					self.wfile.write(json.dumps(rows))
								
				elif data['method'][0] == 'toggleShowSubscription':
					self.send_response(200)
					self.send_header('Content-type',	'application/json')
					self.end_headers()
					showid = data['showid'][0]
					row = DB.query("SELECT subscriptionid FROM rw_subscriptions WHERE showid=?", [showid])
					print row
					if row:
						DB.execute("DELETE FROM rw_subscriptions WHERE subscriptionid=?", [row[0]])
					else:
						DB.execute("INSERT INTO rw_subscriptions(showid) VALUES(?)", [showid]);
					DB.commit()

				elif data['method'][0] =='getSubscriptionInfo':
					self.send_response(200)
					self.send_header('Content-type',	'application/json')
					self.end_headers()
					showid = data['showid'][0]
					row = DB.query("SELECT CONCAT(rw_episodelinks.provider, ' (', count(rw_episodes.showid), ')') AS providers FROM rw_episodes JOIN rw_episodelinks on rw_episodes.episodeid = rw_episodelinks.episodeid WHERE rw_episodes.showid=? GROUP BY rw_episodelinks.provider", [showid])
					self.wfile.write(json.dumps(row))
						
				elif data['method'][0] == 'getLogContent':
					self.send_response(200)
					self.send_header('Content-type',	'text/plain')
					self.end_headers()
					logfile = os.path.join(xbmc.translatePath('special://temp'), 'xbmc.log')
					f = open(logfile)
					contents = f.read()
					contents = re.sub('<host>(.+?)</host>', '<pass>******</pass>', contents)
					contents = re.sub('<name>(.+?)</name>', '<name>******</name>', contents)
					contents = re.sub('<user>(.+?)</user>', '<user>******</user>', contents)
					contents = re.sub('<pass>(.+?)</pass>', '<pass>******</pass>', contents)
					self.wfile.write(contents)
					f.close()
				
				return
			else:
				if self.path=='/':
					self.path='/index.html'
				fileName, fileExtension = os.path.splitext(self.path)
				f = open(WEB_ROOT + sep + self.path) 
				self.send_response(200)
				if fileExtension =='.css':
					self.send_header('Content-type',	'text/css')
				elif fileExtension =='.js':
					self.send_header('Content-type',	'application/javascript')
				elif fileExtension =='.jpg':
					self.send_header('Content-type',	'image/jpeg')
				elif fileExtension =='.png':
					self.send_header('Content-type',	'image/png')
				elif fileExtension =='.gif':
					self.send_header('Content-type',	'image/gif')
				else:
					self.send_header('Content-type',	'text/html')

				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return
			return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	
	def do_POST(self):
		global rootnode
		try:
    			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
    			if ctype == 'multipart/form-data':
				query=cgi.parse_multipart(self.rfile, pdict)
				print query
    			self.send_response(301)
    
    			self.end_headers()
    			upfilecontent = query.get('upfile')
    			print "filecontent", upfilecontent[0]
    			self.wfile.write("<HTML>POST OK.<BR><BR>");
    			self.wfile.write(upfilecontent[0]);
		except:
			pass


class MaudeServer:
	def __init__(self):
		self.addon_id = "service.webinterface.maude"
		self.settings_id = "plugin.video.theroyalwe"
    		self.addon = xbmcaddon.Addon(self.addon_id)
    		self.datadir = self.addon.getAddonInfo('profile')
		self.datapath = None
    		self.addondir = self.addon.getAddonInfo('path')
		self.webroot = '/www'
		self.port = 8181
		self.delay = 30
	
	def loadSettings(self):
		global WEB_ROOT
		global DB
		xbmc.log("Loading service settings")
		addon = xbmcaddon.Addon(self.addon_id)
		self.enabled = addon.getSetting('server-enabled')
		self.port = int(addon.getSetting('server-port'))
		self.authenticate = addon.getSetting('server-authentication')		
		self.username = addon.getSetting('server-username')
		self.username = addon.getSetting('server-password')
		addon = xbmcaddon.Addon(self.settings_id)
		if not self.datapath:
			self.datapath = os.path.join(xbmc.translatePath('special://profile/addon_data/' + self.settings_id +'/maude'), '')
			WEB_ROOT = os.path.join(xbmc.translatePath(self.addondir + self.webroot), '')
			if not os.path.exists(self.datapath):
				os.makedirs(self.datapath)
		'''if addon.getSetting('database_mysql')=='true':
			from donnie.databaseconnector import MySQLDatabase
			DB = MySQLDatabase(addon.getSetting('database_mysql_host'), addon.getSetting('database_mysql_name'), addon.getSetting('database_mysql_user'), addon.getSetting('database_mysql_pass'))
			DB.connect()
		else:
			from donnie.databaseconnector import SQLiteDatabase'''

		from donnie.databaseconnector import DataConnector
		Connector = DataConnector()
		if Connector.getSetting('database_mysql')=='true':
			DB_TYPE = 'mysql'
		else:
			DB_TYPE = 'sqlite'
		DB = Connector.GetConnector()
		DB.connect()
		
	
	def start(self):
		xbmc.log("The Royal We WebInterface Service starting...")
		self.loadSettings()
		self.run()
	
	def run(self):
		xbmc.log("Launching WebInterface on port: " + str(self.port))
		while(not xbmc.abortRequested):
			server = HTTPServer(('', self.port), RequestHandler)
       			print 'Started httpserver...'
        		server.serve_forever()
        	server.socket.close()
		xbmc.log("The Royal We AutoUpdater Service stopping...")

if __name__ == '__main__':
	Maude = MaudeServer()
	Maude.start()
