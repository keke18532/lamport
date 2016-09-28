#-*- coding: UTF-8 -*-
import os,sys,linecache,random,socket


CLOCK=0
LIST=[]

def getConfig(argv):
	if(len(argv) < 3):
		return False
	else :
		config = linecache.getline(argv[1],int(argv[2]))
		#if find right record from file set id and port, then return true, else return false
		if(config.strip() == ''):
			return False
		else:
			para = config.split(' ')
			global LIST
			LIST += [[int(para[0]),int(para[1])]]
			return True

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
		print(id,' ',port)
		if port != LIST[0][1]:
			s = socket.socket()
			if s.connect_ex((host,port)) == 0:
				LIST.append([[id,port]])
				string='confirm '+str(LIST[0][0])+' '+str(LIST[0][1])
				s.send(bytes(string,'UTF-8'))
			s.close()
		i+=1
	print('Sending finished')

def startRandomEvent():
# get a random nuber from0 to 1
# define 0 as local event
# define 1 as sending message event
	if getRandomnumber(0,1)==0:
		localEvent()
	else:
		sendMessage()

def main(argv):
#read configuration
#send confirmation to other node and check exist node in the same time
#waiting for confirmation from other node
#waiting for start signal
	if get_Config(argv):
		print('ID:',LIST[0][0],' port:',LIST[0][1])
	else:
		print('No right line for configuration')
	configs = linecache.getlines(argv[1])
	send_Confirmation(configs)
	s = socket.socket()
	host = socket.gethostname()
	s.bind((host,LIST[0][1]))
	s.listen(len(configs))
	while True:
		conn, addr = s.accept()
		string = str(conn.recv(1024)).strip()
		string = string[2:len(string)-1]
		if  string == 'beat':
			conn.close()
			startRandomEvent()
		elif  string != '':
			print(string)
			para =string.split(' ')
			id = int(para[1])
			port = int(para[2])
			LIST.append([[id,port]])

def localEvent():
	global CLOCK
	CLOCK += getRandomNumber(1,5)

def sendMessage():
	s = socket.socket()
	host = socket.gethostname()
	node = LIST[getRandomNumber(1,len(LIST))]
	if s.connect_ex((host,node[1]))
		message = "message "+str(LIST[0][0])+" "+str(CLOCK)
		s.send(bytes('','UTF-8'))
	s.close()
	
'''def receieve_Message():
	#define message as 'type:(ping or clock),clock:(clock)'
	
	while True:
		
		if s.recv(1024)'''


main(sys.argv)

'''
receive message
update clock count
write result
'''
'''
a thread for receiving message
main process work for event
what will happen if CLOCK got locked?
'''

