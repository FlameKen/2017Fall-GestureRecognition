import pyautogui, time
time.sleep(5)
pyautogui.FAILSAFE = True

def copy():	
	ctrl(c)
	#pyautogui.keyDown('ctrlleft')
	#pyautogui.typewrite('c')
	#pyautogui.keyUp('ctrlleft')
	
def paste():	
	ctrl(v)
	#pyautogui.keyDown('ctrlleft')
	#pyautogui.typewrite('c')
	#pyautogui.keyUp('ctrlleft')
	
def moveTo(x, y, t):
	pyautogui.moveTo(x, y, duration=t)

def moveRel(x, y, t):
	#pyautogui.mouseUp()
	pyautogui.moveRel(x, y, duration=t)
	
def dragTo(x, y, t):
	pyautogui.dragTo(x, y, duration=t)
	
def dragRel(x, y, t):
	#pyautogui.moveRel(x, y, duration=t)
	pyautogui.dragRel(x, y, duration=t)

def click():
	#x = int(input("Enter your x: "))
	#y = int(input("Enter your y: "))
	x, y = pyautogui.position()
	pyautogui.click(x, y)
	#pyautogui.click()
	
def mouseDown():
	pyautogui.mouseDown()
	
def mouseUp():
	pyautogui.mouseUp()
	
def doubleClick():
	pyautogui.doubleClick()

def rightClick():
	pyautogui.rightClick()
	
def scroll(length):
	#length = int(input("Enter your length: "))
	pyautogui.scroll(length)

def zoomIn():
	times = int(input("Enter your zoom times: "))
	pyautogui.keyDown('ctrlleft')
	for _ in range(times):
		pyautogui.scroll(200)
	pyautogui.keyUp('ctrlleft')
	
def zoomOut():
	times = int(input("Enter your zoom times: "))
	pyautogui.keyDown('ctrlleft')
	for _ in range(times):
		pyautogui.scroll(-200)
	pyautogui.keyUp('ctrlleft')
	
def ctrl(char):
	pyautogui.hotKey('ctrlleft', char)
	#pyautogui.keyDown('ctrlleft')
	#pyautogui.press(char)
	#pyautogui.keyUp('ctrlleft')
	
def press(mesg):
	pyautogui.keyDown(mesg)
	time.sleep(0.3)
	pyautogui.keyUp(mesg)
	#pyautogui.press(mesg)
	#for i  in range(len(mesg)):
	#	pyautogui.press(mesg[i])
	#pyautogui.press('enter')