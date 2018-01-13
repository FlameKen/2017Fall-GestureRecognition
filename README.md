# 虛擬世界互動介面

提供一個可以藉由手勢辨識來跟電腦互動的功能。

# 動機

<img src="https://github.com/NTUEE-ESLab/2017Fall-GestureRecognition/blob/master/img/Minority-Report.jpg" width="50%" height="50%">

《關鍵報告》是一部由Steven Spielberg於2002年所拍攝的一部科幻電影。電影背景設定在一個高科技的未來世界，在這麼一個世界裏面，跟電腦互動的方式並不只是單單的利用鍵盤滑鼠，而是可以直接在空中跟電腦所投影出來的畫面，可以想像就是我們現在所謂的擴增實境，來進行互動。
  
我們這一組想要重現此場景，不過鑑於我們手邊的硬體設備限制，我們想要先初步設計一個可以追蹤使用者，且不需用藉由滑鼠鍵盤，來跟電腦進行簡單的互動功能，像是利用手勢進行頭影片的翻頁等等簡易卻方便的功能。

# 作法
## 架構

<img src="https://github.com/NTUEE-ESLab/2017Fall-GestureRecognition/blob/master/img/Structure.jpg" width="50%" height="50%">
  
我們的整個架構，流程，如上圖所示，而整體又可大致分為兩大部份 ── "臉部偵測&追蹤"，以及"手勢辨識&指令傳送"。
  
首先，先例用Logitech Webcam C310拍攝人體上半身，將此畫面丟入Respberry Pi 3中進行人臉辨識以及人臉追蹤，接著將此資訊傳到Arduino UNO，得到人臉位置與相機中心的差距，Arduino再藉由伺服馬達MG 996R來旋轉鏡頭。
  
人臉位置校正完了之後，Rpi camera所拍攝出來頸部以下的畫面會傳送至另一個Respberry Pi 3中，以進行手勢的辨識，最終判斷出來的手勢再轉換成指令，藉由區域網路傳送至我們的電腦。
  
## 臉部偵測&追蹤

## 手勢辨識&指令傳送

手勢辨識的部份利用OpenCV 3.3所提供的function。
   
首先是膚色偵測與校準，偵測的部分利用`cv2.inRange2`鎖定我們所感興趣的顏色範圍，校準的部分利用cv2的trackbar功能，即時的轉換校準範圍，針對不同的背景環境進行即時的修改。
   
<img src="https://github.com/NTUEE-ESLab/2017Fall-GestureRecognition/blob/master/img/trackbar.jpg" width="30%" height="30%">

再來是找出膚色輪廓，以及輪廓凹陷處來辨識為何種手型。選取輪廓的部分利用`cv2.findContour`，輪廓凹陷處利用`cv2.convexHull`，偵測完之後會得到許多convexity defects，可以想成是手指與手指之間的間隙。由於膚色辨識所得出來的結果並不是很乾淨，還會夾帶許多雜訊，所以最後利用一些演算法，像是把指縫夾角過大，或是手指過短的defects去掉，便可以得到較準確的手指數量與位置，來算出最後所比出的手勢為何。
    
    
<img src="https://github.com/NTUEE-ESLab/2017Fall-GestureRecognition/blob/master/img/skin%20detect.jpg" width="50%" height="50%">
<img src="https://github.com/NTUEE-ESLab/2017Fall-GestureRecognition/blob/master/img/contour.jpg" width="50%" height="50%">
    
手勢算出來之後，最後就是指令的傳送，我們利用區域網路的方式，找到接收端的ip address，而Respberry Pi 3 再利用socket的形式傳送給接收端。我們也有額外實作出另一種方式，就算沒有網路，只要有一條網路線，也一樣可以建立一個一對一的區域網路，之後就一樣，找到接收端的ip address，Respberry Pi 3 利用socket傳送指令。

## 指令操作(接收端)

這個部分就比較optional，視接收端為何種器材，而必須寫出不同的操作方式。我們這邊的介紹以電腦為主。
  
電腦的輸入主要是以滑鼠跟鍵盤為主，而python提供了一個叫做`pyautogui`的module，可以進行幾乎所有的滑鼠以及鍵盤的指令動作，以下介紹幾個我們常用的指令。
  
1.  `pyautogui.moveRel(x, y, duration=t)`: 滑鼠移動一段距離。x跟y代表相對的x方向以及y方向的pixel格數，以左上方為原點，整個螢幕為第一象限。t為這個指令執行的所花時間，設得太大則滑鼠移動過慢，太快也不自然，需要實驗一下設計出最合適的duration。

2.  `pyautogui.dragRel(x, y, duration=t)`: 與第一個指令基本上一樣，除了一點就是他是拖曳著移動的，用在像是使用滑鼠選取範圍，或是拉一條線等等。

3.  `pyautogui.click()`: 按一下滑鼠左鍵。

4.  `pyautogui.rightClick()`: 按一下滑鼠右鍵。

5.  `pyautogui.press(mesg)`: 控制鍵盤的指令，mesg通常放的是一個字母，或是shift、ctrl等功能鍵。

6.  `pyautogui.keyDown(mesg)` & `pyautogui.keyUp(mesg)`: 上面一個指令是瞬間發生的，也就是如果我們今天想要將這個功能實作在遊戲上，他會瞬間按下然後瞬間放開，所以如果是移動式的指令，基本上不會動。如果要避免這種情況的話，我們需要的只是按下，並且等待一段時間再放開，因此這邊需要配合`keyDown(mesg)`以及`keyUp(mesg)`，中間再放一行`time.sleep(t)`，(建議t < 0.3)，這樣便可以將這個實作應用在遊戲上。
  
# 成果

1.  [Face Tracker]

<a href="http://www.youtube.com/watch?feature=player_embedded&v=_Xq-OTUw1Vc" target="_blank"><img src="http://img.youtube.com/vi/_Xq-OTUw1Vc/0.jpg" alt="IMAGE ALT TEXT HERE" width="360" height="240" border="20" /></a>

2.  [Slide Controller](https://www.youtube.com/watch?v=H5ghYShFbUI&feature=youtu.be)

3.  [Painter Controller](https://www.youtube.com/watch?v=sr9F48PzTkM&feature=youtu.be)

# 參考資料

1.  [Hand tracking and gesture recognition](https://link.springer.com/article/10.1007/s11042-013-1501-1)

2.  [Computer_Vision](https://github.com/RobinCPC/CE264-Computer_Vision)

3.  [pyautogui](https://automatetheboringstuff.com/chapter18/)
