import socket
import re
import Queue
import urllib2
import threading
import os
import logging
from BeautifulSoup import BeautifulSoup


def getTitle(q, url):
	html = urllib2.urlopen(url).read()
	soup = BeautifulSoup(html)
	title = soup.title.string
	if isinstance(title, unicode):
		title = title.splitlines()
	else:
		title = title.rstrip(["\n","\r"])
	t = ""
	for i in title:
		t = t + i
	print url + " " + str(t.encode("utf-8"))
	message = url + " " + str(t.encode("utf-8"))
	q.put(message)

logging.basicConfig(filename="linkbot0.log",format='%(asctime)s %(message)s', level=logging.DEBUG)
operational = False

server = "dreamhack.se.quakenet.org"
#server = "port80a.se.quakenet.org"
channel = "#hightech"
channel = "#linkbot0"
nickname = "LinkBot1"

q = Queue.Queue()

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.settimeout(2)

irc.connect((server, 6667))

logging.info("Connected to server %s", server)


irc.send("USER " + nickname + " " + nickname + " " + nickname + " :Linkbot\n")
irc.send("NICK " + nickname + "\n")
irc.send("PRIVMSG nickserv :NOOPE\r\n")
#irc.send("JOIN " + channel + "\n")

logging.info("User and nicknames set")

#print "Entering while loop"

urlReg = re.compile(r"(http://[^ ]+|https://[^ ]+)")
channelReg = re.compile(r"(#[^ ]+)")

while 1:
	try:
		message = irc.recv(2040)
		print message
		logging.info("Recieved message: %s", message)
	except Exception, e:
		#print e
		message = ""

	#PingPong
	if message.find("PING") != -1:
		irc.send("PONG " + message.split()[1] + "\r\n")
		logging.debug("PONG")
	#Joining channels
	if message.find("End of /MOTD command.") != -1:
		irc.send("JOIN " + channel + "\n")
		operational = True
		logging.info("Joined channels")

	if not q.empty():
		print q.qsize()
		while not q.empty():
			m = q.get()
			print "sending message " + m.rstrip(os.linesep)
			logging.info("Sending message: PRIVMSG %s :%s", channel, m)
			#irc.send("PRIVMSG " + channel +" :"+ m.encode('utf8') +" \n")
			irc.send("PRIVMSG " + channel +" :"+ m +" \n")

	else:
		if operational:
			url = urlReg.findall(message)
			if url:
				for u in url:
					print "Found link " + u
					t = threading.Thread(target=getTitle, args=(q, u.rstrip()))
					t.daemon = True
					t.start()
					#irc.send("PRIVMSG " + channel +" :"+ "Found url: " +u +"\n")
