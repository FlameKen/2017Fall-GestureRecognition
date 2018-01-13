# 虛擬世界互動介面

提供一個可以藉由手勢辨識來跟電腦互動的功能。

# 動機

  《關鍵報告》是一部由Steven Spielberg於2002年所拍攝的一部科幻電影。電影背景設定在一個高科技的未來世界，在這麼一個世界裏面，跟電腦互動的方式並不只是單單的利用鍵盤滑鼠，而是可以直接在空中跟電腦所投影出來的畫面，可以想像就是我們現在所謂的擴增實境，來進行互動。
  我們這一組想要重現此場景，不過鑑於我們手邊的硬體設備限制，我們想要先初步設計一個可以不需用藉由滑鼠鍵盤，來跟電腦進行簡單的互動功能，像是利用手勢進行頭影片的翻頁等等簡易卻方便的功能。

# 作法
## 架構
（架構圖）
  我們的整個架構，流程，如上圖所示，而整體又可大致分為兩大部份 ── "臉部偵測&追蹤"，以及"手勢辨識&指令傳送"。
  首先，先例用Logitech Webcam C310拍攝人體上半身，將此畫面丟入Respberry Pi 3中進行人臉辨識以及人臉追蹤，接著將此資訊傳到Arduino UNO，得到人臉位置與相機中心的差距，Arduino再藉由伺服馬達MG 996R來旋轉鏡頭。
  人臉位置校正完了之後，Rpi camera所拍攝出來頸部以下的畫面會傳送至另一個Respberry Pi 3中，以進行手勢的辨識，最終判斷出來的手勢再轉換成指令，藉由區域網路傳送至我們的電腦。
  
## 臉部偵測&追蹤

## 手勢辨識&指令傳送
   手勢辨識的部份利用OpenCV3.3所提供的function。首先是

# 成果

# 參考資料
