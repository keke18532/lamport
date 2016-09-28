#-*- coding: UTF-8 -*-
import os,sys,linecache,random,socket,_thread,time

configs = linecache.getlines(sys.argv[1])


def beat(port):
	print(port)
	s = socket.socket()
	if s.connect_ex((socket.gethostname(),port)) == 0:
		s.send(bytes('beat','UTF-8'))
	s.close()

count = 0
while count<10:
	i = 0
	while i < len(configs):
		para = int(configs[i].split(' ')[1])
		_thread.start_new_thread(beat,(para,))
		i += 1
	time.sleep(2)
	count += 1