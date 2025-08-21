from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QLCDNumber
from PyQt6.uic import loadUi
from zoneinfo import ZoneInfo
from PyQt6.QtCore import QTimeZone
import tzlocal
from datetime import datetime, timezone #класс импортируем из модуля, класс  по работе с временем и датой
from PyQt6.QtCore import QTimer

class MyWindow(QMainWindow):
    lcdNumber: QLCDNumber
    comboBox: QComboBox
    def update_time(self):
        current_tz = self.comboBox.currentText()#получаем назв. текущ. выбранного часового пояса
        utc_now = datetime.now(timezone.utc)
        current_zone_info = ZoneInfo(current_tz)#создание объекта  информацией о часовом поясt
        t = utc_now.astimezone(current_zone_info)# присоед. инф. о часовом поясе к оюъекту времени ы
        self.lcdNumber.display(t.strftime("%H:%M:%S"))# вызов метода display y lcdnumber
    def __init__(self):
        super().__init__()
        loadUi("mainwindow.ui", self)
      
        self.timer = QTimer()
        self.load_data()
         # Отступы внутрь окна
        self.centralWidget().layout().setContentsMargins(8, 8, 8, 8)  # left, top, right, bottom

        self.setWindowTitle("Международные часы")
        
        self.update_time()#вызов метода updatetime
        self.bind_events()
    
        self.timer.start(1000)
    def bind_events(self):
        self.timer.timeout.connect(self.update_time)    
    def load_data(self):
        l = QTimeZone.availableTimeZoneIds()# возвращает в массив
        l = [bytes(tz).decode('utf-8') for tz in l]#расшифровываем в строки
        l = filter(lambda s: "UTC" not in s,l)#ламбда - функция, def и return в одной строке
        l = filter(lambda s: "GMT" not in s,l)#s - содержит в себе текущий элемент в списке
        l = list(l)
        self.comboBox.addItems(l)
        self.comboBox.update()
        tz = str(tzlocal.get_localzone())
        i = l.index(tz)
        self.comboBox.setCurrentIndex(i)
        
if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()

