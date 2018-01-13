# 虛擬世界互動介面

提供一個可以藉由手勢辨識來跟電腦互動的功能。

# 動機

<p align="center">
    <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/Minority-Report.jpg" width="70%" height="70%">
</p>

《關鍵報告》是一部由Steven Spielberg於2002年所拍攝的一部科幻電影。電影背景設定在一個高科技的未來世界，在這麼一個世界裏面，跟電腦互動的方式並不只是單單的利用鍵盤滑鼠，而是可以直接在空中跟電腦所投影出來的畫面，可以想像就是我們現在所謂的擴增實境，來進行互動。

我們這一組想要重現此場景，不過鑑於我們手邊的硬體設備限制，我們想要先初步設計一個可以追蹤使用者，且不需用藉由滑鼠鍵盤，來跟電腦進行簡單的互動功能，像是利用手勢進行頭影片的翻頁等等簡易卻方便的功能。

# 作法
## 架構

<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/Structure.jpg" width="100%" height="100%">
</p> 

我們的整個架構，流程，如上圖所示，而整體又可大致分為兩大部份 ── "臉部偵測&追蹤"，以及"手勢辨識&指令傳送"。

首先，先例用Logitech Webcam C310拍攝人體上半身，將此畫面丟入Respberry Pi 3中進行人臉辨識以及人臉追蹤，接著將此資訊傳到Arduino UNO，得到人臉位置與相機中心的差距，Arduino再藉由伺服馬達MG 996R來旋轉鏡頭。

人臉位置校正完了之後，Rpi camera所拍攝出來頸部以下的畫面會傳送至另一個Respberry Pi 3中，以進行手勢的辨識，最終判斷出來的手勢再轉換成指令，藉由區域網路傳送至我們的電腦。

## 臉部偵測&追蹤

### § 臉部偵測

<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/face-detect.png" width="50%" height="50%">
</p>

臉部偵測的部份利用OpenCV 3.3所提供的library、目標影像追蹤則是使用Dlib提供的library。

利用`cv2.CascadeClassifier`，可以偵測所有出現在畫面的人臉，並且我們選取面積最大的當作我們要跟隨的臉部影像。

為了避免不斷偵測臉部，利用`dlib.correlation_tracker`，可以持續跟隨變化不劇烈的目標影像，做法是將剛剛跟隨的局部影像給tracker去進行跟隨，再將完整的影像畫面丟進function `tracker.update(baseImage)`，計算影像的Quality，若數值夠高，則維持追蹤的狀態，並且更新局部影像位置；若數值過低，則取消追蹤狀態，重新進行臉部偵測。

### § 臉部追蹤

<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/rpi-arduino.jpg" width="100%" height="100%">
</p>

上圖為線路架構，RPi負責追蹤臉部，傳送旋轉的指令給Arduino，Arduino再控制Servo進行旋轉。我們是透過4條電線進行訊號傳遞，分別控制左轉、右轉、上轉、下轉的訊號，也可以使用Bluetooth、I2C等等。

在利用dlib的correlation_tracker的時候，我們可以得到臉部的中心位置，當中心位置超出我們設定的邊界，就傳訊號給Arduino旋轉，直到影像中心位置回到邊界中間。

Arduino則是設定好伺服馬達的初始角度後，在`loop()`內不斷進行訊號偵測，當我偵測到來自RPi的訊號時，我就朝某個方向不斷增加/減少值，來更新我的伺服馬達角度，為了避免Servo亂轉，當我更新的值要超過180或小於0的時候，便不再讓伺服馬達轉動。

### # RPi3 & Arduino

|            |RPi3        |Arduino     |
|:----------:|:----------:|:----------:|
|Up          |GPIO20      |PIN12       |
|Down        |GPIO21      |PIN13       |
|Left        |GPIO23      |PIN5        |
|Right       |GPIO24      |PIN6        |

### # Arduino & MG996R

|            |Arduino     |MG996R      |
|:----------:|:----------:|:----------:|
|GND         |GND         |GND         |
|VCC         |5V          |V+          |
|Servo (X)   |PIN9        |PWM         |
|Servo (Y)   |PIN10       |PWM         |

### # RPi3 & LED

|            |RPi3        |LED         |
|:----------:|:----------:|:----------:|
|GND         |GND         |V -         |
|VCC         |GPIO26      |V+          |

## 手勢辨識&指令傳送

### § 手勢辨識

手勢辨識的部份利用OpenCV 3.3所提供的library。

首先是膚色偵測與校準，偵測的部分利用`cv2.inRange2`鎖定我們所感興趣的顏色範圍，校準的部分利用cv2的trackbar功能，即時的轉換校準範圍，針對不同的背景環境進行即時的修改。

#### Skin detection
<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/skin%20detect.jpg" width="60%" height="60%">
</p>

#### Track bar
<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/trackbar.jpg" width="50%" height="50%">
</p>

再來是找出膚色輪廓，以及輪廓凹陷處來辨識為何種手型。選取輪廓的部分利用`cv2.findContour`，輪廓凹陷處利用`cv2.convexHull`，偵測完之後會得到許多convexity defects，可以想成是手指與手指之間的間隙。由於膚色辨識所得出來的結果並不是很乾淨，還會夾帶許多雜訊，所以最後利用一些演算法，像是把指縫夾角過大，或是手指過短的defects去掉，便可以得到較準確的手指數量與位置，來算出最後所比出的手勢為何。

#### Find contour (Green line) & Get convexhull (red and blue points)
<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/contour.jpg" width="60%" height="60%">
</p>

### § 指令傳送

手勢算出來之後，最後就是指令的傳送，我們利用區域網路的方式，找到接收端的ip address，而Respberry Pi 3 再利用socket的形式傳送給接收端。我們也有額外實作出另一種方式，就算沒有網路，只要有一條網路線，也一樣可以建立一個一對一的區域網路，之後就一樣，找到接收端的ip address，Respberry Pi 3 利用socket傳送指令。

## 指令操作(接收端) & 指令穩定

### § 指令操作

這個部分就比較optional，視接收端為何種器材，而必須寫出不同的操作方式。我們這邊的介紹以電腦為主。

電腦的輸入主要是以滑鼠跟鍵盤為主，而python提供了一個叫做`pyautogui`的module，可以進行幾乎所有的滑鼠以及鍵盤的指令動作，以下介紹幾個我們常用的指令。

1.  `pyautogui.moveRel(x, y, duration=t)`: 滑鼠移動一段距離。x跟y代表相對的x方向以及y方向的pixel格數，以左上方為原點，整個螢幕為第一象限。t為這個指令執行的所花時間，設得太大則滑鼠移動過慢，太快也不自然，需要實驗一下設計出最合適的duration。

2.  `pyautogui.dragRel(x, y, duration=t)`: 與第一個指令基本上一樣，除了一點就是他是拖曳著移動的，用在像是使用滑鼠選取範圍，或是拉一條線等等。

3.  `pyautogui.click()`: 按一下滑鼠左鍵。

4.  `pyautogui.rightClick()`: 按一下滑鼠右鍵。

5.  `pyautogui.press(mesg)`: 控制鍵盤的指令，mesg通常放的是一個字母，或是shift、ctrl等功能鍵。

6.  `pyautogui.keyDown(mesg)` & `pyautogui.keyUp(mesg)`: 上面一個指令是瞬間發生的，也就是如果我們今天想要將這個功能實作在遊戲上，他會瞬間按下然後瞬間放開，所以如果是移動式的指令，基本上不會動。如果要避免這種情況的話，我們需要的只是按下，並且等待一段時間再放開，因此這邊需要配合`keyDown(mesg)`以及`keyUp(mesg)`，中間再放一行`time.sleep(t)`，(建議t < 0.3)，這樣便可以將這個實作應用在遊戲上。

### § 指令穩定

顧名思義，就是要穩定指令，就算RPi3在手勢辨識的時候已經有演算法在控制，但還是會有不穩定的偵測發生。舉例來說，實際上可能我可能一直比著2，但是由於手可能會晃動，或是偵測範圍的抖動，導致會有一瞬間判定出1，或是3，這樣會傳出一個我們不想要的指令。因此我們這邊用了一個Fixed Queue的機制，儲存前5個指令的歷史紀錄，而如果在Queue中至少出現4次同樣的指令的話則會執行該指令。也就是說，在塞滿了歷史紀錄為2的Queue當中突然出現一個1的話，他會忽略那個雜訊1，而繼續執行指令2的動作。當然這麼做會有些缺點，就是當我們在換指令的時候，會有些微的delay，那是因為新指令還在剛丟入到Queue裡面，所以至少要等4個cycle才會執行新指令，不過在穩定指令跟新指令延遲這兩個狀況來取一個trade off的話，這樣的小延遲是可以接受的。

# 成果

1.  [Face Tracker](https://www.youtube.com/watch?v=_Xq-OTUw1Vc&feature=youtu.be)

2.  [Slide Controller](https://www.youtube.com/watch?v=H5ghYShFbUI&feature=youtu.be)

3.  [Painter Controller](https://www.youtube.com/watch?v=sr9F48PzTkM&feature=youtu.be)

<p align="center">
  <img src="https://raw.githubusercontent.com/NTUEE-ESLab/2017Fall-GestureRecognition/master/img/paint.jpg" width="100%" height="100%">
</p>

# 參考資料

1.  [Hand tracking and gesture recognition](https://link.springer.com/article/10.1007/s11042-013-1501-1)

2.  [Computer_Vision](https://github.com/RobinCPC/CE264-Computer_Vision)

3.  [pyautogui](https://automatetheboringstuff.com/chapter18/)
