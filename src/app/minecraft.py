import pyautogui
import socket
import time as t
import math
import re
from gui import *

class FixedQueue:
	def __init__(self):
		self.list = ["none", "none", "none", "none", "none"]
		self.max_item = 5
		self.n_maj = 4
		
	def __str__(self):
		return str(self.list)
	
	def push(self, item):
		if self.list.__len__() == self.max_item:
			self.list.pop()
		self.list.insert(0, item)
	
	def pop(self):
		return self.list.pop()
	
	def major(self):
		maj = 'none'
		count = 0
		for i in self.list:
			cur_cnt = self.list.count(i)
			if cur_cnt > 3:
				maj = i
				if i == "click" and cur_cnt != 5:
					maj = 'none'
			'''
			if cur_cnt > 2:
				if self.list[0] != i and self.list[1] != i:
					return 'none'
				else:
					return i
			if cur_cnt > count:
				maj = i
				count = cur_cnt
			'''
		return maj
	
	def coun(self, value):
		return self.list.count(value)

Hist = FixedQueue()

def instHist(action):
	final_action = Hist.major()
	Hist.push(action)
	return final_action

def main():
	pyautogui.FAILSAFE = False
	print ('Starting....')
	# get the hostname
	host = socket.gethostname()
	port = 5000  # initiate port no above 1024

	server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
	server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
	server_socket.listen(2)
	conn, address = server_socket.accept()  # accept new connection
	print("Connection from: " + str(address))
	try:
		while True:
			data = conn.recv(1024).decode()
			if not data:
				break
			#inst = data.split(' ')
			#print("Instruction received: " + str(data))
			insts = data.split(",")
			#data = input(' -> ')
			#conn.send(data.encode())
			#print (inst, '\n')
			if (data == "quit"):
				break
			left_hand = False
			for inst in insts:
				instruction(inst, left_hand)
				left_hand = True
			#t.sleep(0.1)
	except KeyboardInterrupt:
		return
		#print('\nDone.')
	
def instruction(inst, left):
	inst_dict = {
					#mouse
					"three_rot": "moveRel",
					"four_rot": "moveRel",
					"five_rot": "moveRel",
					"one_rot": "moveRel",
					"three_click": "click",
					"four_click": "click",
					"five_click": "click",
					"one_click": "click",
					#"gesture_rot": "dragRel",
					#"seven_rot": "dragRel",
					#"two_rot": "dragRel",
					#"gesture_rot": "press",
					#"seven_rot": "press",
					#"two_rot": "press",
				}
	'''
	if left:
		inst_dict = {
						#mouse
						
						"n": "moveRel -50 50 0.3",
						"m": "moveRel 0 50 0.3",
						",": "moveRel 50 50 0.3",
						"h": "moveRel -50 0 0.3",
						"k": "moveRel 50 0 0.3",
						"y": "moveRel -50 -50 0.3",
						"u": "moveRel 0 -50 0.3",
						"i": "moveRel 50 -50 0.3",
						"c": "scroll 200",
						"v": "scroll -200",
						"o": "mouseDown",
						"l": "mouseUp",
						"p": "click",
						
						#keyboard
						
						"three_up": "press 1",
						"four_up": "press 2",
						"five_up": "press 3",
						"three_down": "press 7",
						"four_down": "press 8",
						"five_down": "press 9",
						
					}
	else:
	'''
	ins = inst.split(' ')
	x, y = 0, 0
	direct = ""
	if len(ins) > 1:
		#print(ins)
		ins[1] = re.sub(r'[a-zA-Z_]', '', ins[1])
		param = float(ins[1])
		if param >= 45 and param < 135:
			direct = "down"
		elif param >= 135 or param < -135:
			direct = "left"
		elif param < 45 and param >= -45 :
			direct = "right"
		elif param < -45 and param >= -135:
			direct = "up"
		x = 10*math.cos(param*math.pi/180)
		y = 10*math.sin(param*math.pi/180)
	action = inst_dict.get(ins[0], "none").split(' ')
	#print(action)
	action[0] = instHist(action[0])
	#print(action)
	#print ("Instruction to action: ", action)
	
	'''
	if action[0] == "moveTo": moveTo(int(inst[1]), int(inst[2]), float(inst[3]))
	elif action[0] == "moveRel": moveRel(int(action[1]), int(action[2]), float(action[3]))
	elif action[0] == "dragTo": dragTo(int(inst[1]), int(inst[2]), float(inst[3]))
	elif action[0] == "dragRel": dragRel(int(action[1]), int(action[2]), float(action[3]))
	el
	'''
	if len(action) == 1:
		if action[0] == "click": click()
		elif action[0] == "moveRel": moveRel(x, y, 0.1)
		elif action[0] == "dragRel": dragRel(x, y, 0.1)
		elif action[0] == "press": press(direct)
		elif action[0] == "mouseDown": mouseDown()
		elif action[0] == "mouseUp": mouseUp()
	elif len(action) == 2:
		if action[0] == "press": press(action[1])
		elif action[0] == "scroll": scroll(int(action[1]))
	#else: print("Invalid instruction\n")
	
if __name__ == '__main__':
	main()
