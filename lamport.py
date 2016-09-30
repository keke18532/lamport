#-*- coding: UTF-8 -*-
import os,sys,linecache,random,socket,time,_thread


CLOCK = 0
LIST = []
THREADNUM = 0
CLOCKQUEUE = []

def getConfig(argv):
	if(len(argv) < 3):
		return False
	config = linecache.getline(argv[1],int(argv[2]))
	if(config.strip() == ''):
		return False
	#if find right record from file set id and port, then return true, else return false
	para = config.split(' ')
	port=int(para[1])
	s = socket.socket()
	result = True
	if s.connect_ex((socket.gethostname(),port)) == 0:
		print('Port in use')
		result = False
	global LIST
	LIST += [[int(para[0]),port]]
	s.close()
	return result

def getRandomNumber(min_number,max_number):
	return int(random.random()*(max_number-min_number+1))+min_number      
# return x and mn_number<=x<=max_number

def sendConfirmation(configs):
	host = socket.gethostname()
	i = 0
	while i<len(configs):
		para = configs[i].split(' ')
		id = int(para[0])
		port = int(para[1])
		if port != LIST[0][1]:
			s = socket.socket()
			if s.connect_ex((host,port)) == 0:
				LIST.append([id,port])
				string='confirm '+str(LIST[0][0])+' '+str(LIST[0][1])
				s.send(bytes(string,'UTF-8'))
			s.close()
		i+=1
	print('Sending finished')

def localEvent():
#Local event: l n, where n is the amount by which the clock was increased
	global CLOCK
	CLOCK += getRandomNumber(1,5)
	print('l',CLOCK)

def sendMessage():
#Sending a message: s r l, where r is the receiving node ID and l is the clock value sent in the message.
	s = socket.socket()
	host = socket.gethostname()
	if len(LIST)==1:
		return 0
	node = LIST[getRandomNumber(1,len(LIST)-1)]
	if s.connect_ex((host,node[1])) == 0: 
		message = "message "+str(LIST[0][0])+" "+str(CLOCK)
		s.send(bytes(message,'UTF-8'))
		print('s',node[0],CLOCK)
	s.close()
	'''try:		
		s.send(bytes(message,'UTF-8'))
	except Exception as err:  
		
	finally:
		#write in
		print('s',node[0],CLOCK)
		s.close()'''
	

def startRandomEventSeq():
# get a random nuber from0 to 1
# define 0 as local event
# define 1 as sending message event
	i = 0	
	while i<100:
		if THREADNUM == 0:
			if getRandomNumber(0,1)==0:
				localEvent()
			else:
				sendMessage()
			time.sleep(1)
			i += 1
	time.sleep(5)	
	os._exit(0)

def receiveMessage(nodeid,clock):
#Receiving a message: r s t n, where s is the sender of the message, t is the timestamp that was in the message, and n is the clock value after running Lamport’s algorithm.
	global THREADNUM
	global CLOCK
	global CLOCKQUEUE
	local = CLOCK
	THREADNUM += 1
	CLOCKQUEUE.append(int(clock))
	THREADNUM -= 1
	if THREADNUM == 0:
		CLOCKQUEUE.append(CLOCK)
		CLOCK = max(CLOCKQUEUE) + 1
		CLOCKQUEUE = []
		print('r',nodeid,clock,CLOCK)


def main(argv):
#read configuration
#send confirmation to other node and check exist node in the same time
#waiting for confirmation from other node
#waiting for start signal
	if getConfig(argv):
		print('ID:',LIST[0][0],' port:',LIST[0][1])
	else:
		print('No right line for configuration')
		return
	configs = linecache.getlines(argv[1])
	sendConfirmation(configs)
	s = socket.socket()
	host = socket.gethostname()
	s.bind((host,LIST[0][1]))
	s.listen(len(configs))
	while True:
		conn, addr = s.accept()
		string = str(conn.recv(1024)).strip()
		string = string[2:len(string)-1]
		if  string != '':
			para =string.split(' ')
			if para[0] == 'confirm':
				id = int(para[1])
				port = int(para[2])
				LIST.append([id,port])
			elif para[0] == 'message':
				_thread.start_new_thread(receiveMessage,(para[1],para[2],))
			elif para[0] == 'start':
				print('Node Start')
				print(LIST)
				_thread.start_new_thread(startRandomEventSeq,())


	

main(sys.argv)



