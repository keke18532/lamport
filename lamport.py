#-*- coding: UTF-8 -*-
import os,sys,linecache,random,socket,time,_thread


CLOCK = 0
LIST = []
THREADNUM = 0
CLOCKQUEUE = []
OUTPUTSTRING = ''

def getConfig(argv):
#Read configuration
#Check if the input parameter is valid. Configuration should be both exist in the file and unused.
#Create the output file. Named as "output-id-port.txt"
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
# Return x and mn_number<=x<=max_number
	return random.randrange(min_number,max_number+1)

def sendConfirmation(configs):
#Send confirmation to other node and check exist node in the same time
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

def localEvent():
#Local event: l n, where n is the amount by which the clock was increased
	global CLOCK,OUTPUTSTRING
	increment = getRandomNumber(1,5)
	CLOCK += increment
	print('l',increment)
	OUTPUTSTRING += 'l '+str(increment)+'\n'

def sendMessage():
#Sending a message: s r l, where r is the receiving node ID and l is the clock value sent in the message.
#Detect if the randomly choosed node is still alive when connecting and sending.
#Once connecting or sending failed, remove the
	global CLOCK,OUTPUTSTRING,LIST
	s = socket.socket()
	host = socket.gethostname()
	if len(LIST)==1:
		return False
	node = LIST[getRandomNumber(1,len(LIST)-1)]
	flag = False
	if s.connect_ex((host,node[1])) == 0: 
		message = "message "+str(LIST[0][0])+" "+str(CLOCK)
		try:		
			s.send(bytes(message,'UTF-8'))
			print('s',node[0],CLOCK)
			OUTPUTSTRING += 's '+str(node[0])+' '+str(CLOCK)+'\n'
			CLOCK += 1
			flag = True
		except Exception as err:  
			LIST.remove(node)
		finally:
			#write in
			s.close()
			return flag
	else:
		LIST.remove(node)
		return False

def startRandomEventSeq():
# get a random nuber from0 to 1
# define 0 as local event
# define 1 as sending message event
# write output into the text file 
	i = 0	
	while i<10:
		if THREADNUM == 0:
			if getRandomNumber(0,1)==0:
				localEvent()
			else:
				if sendMessage()==False:
					continue
			time.sleep(0.5)
			i += 1
	time.sleep(2)	
	filename = 'output-'+str(LIST[0][0])+'-'+str(LIST[0][1])+'.txt'
	f = open(filename,'w+')
	f.write(OUTPUTSTRING)
	f.close()
	os._exit(0)

def receiveMessage(nodeid,clock):
#Receiving a message: r s t n, where s is the sender of the message, t is the timestamp that was in the message, and n is the clock value after running Lamport’s algorithm.
	global THREADNUM,OUTPUTSTRING,CLOCK,CLOCKQUEUE
	local = CLOCK
	THREADNUM += 1
	CLOCKQUEUE.append(int(clock))
	THREADNUM -= 1
	if THREADNUM == 0:
		CLOCKQUEUE.append(CLOCK)
		CLOCK = max(CLOCKQUEUE) + 1
		CLOCKQUEUE = []
		print('r',nodeid,clock,CLOCK)
		OUTPUTSTRING += 'r '+nodeid+' '+clock+' '+str(CLOCK)+'\n'


def main(argv):
#Initialization
#Waiting for confirmation from other node
#Waiting for start signal
#Receiving the coming message 
	if getConfig(argv):
		print('ID:',LIST[0][0],' port:',LIST[0][1])
	else:
		print('No right line for configuration')
		return
	configs = linecache.getlines(argv[1])
	sendConfirmation(configs)
	print('Init Done')
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
				print('Activated Node: \n',LIST)
				_thread.start_new_thread(startRandomEventSeq,())

main(sys.argv)



