from PyQt6 import QtGui
from PyQt6 import sip

from mainwindownew import Ui_MainWindow as MainWindow
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
import sys
import signal
from pathlib import Path
from PyQt6.QtGui import QPixmap

from button_progress import button_function_class
from settings_progress import settingsclass
from hirsiz import Ui_guvenlik
from duman import Ui_yangin

import uvicorn

from Api_checks import FastAPIRequest


def _install_runtime_guards():
    # Avoid terminal Ctrl+C interruptions crashing the Qt event loop with traceback.
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    def _quiet_excepthook(exc_type, exc, tb):
        if exc_type is KeyboardInterrupt:
            print("KeyboardInterrupt alindi, uygulama calismaya devam ediyor")
            return
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _quiet_excepthook




class Home_Surface(QMainWindow):
    arduino_message_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.MainSurface = MainWindow()
        self.MainSurface.setupUi(self)
        self.buttonclass=button_function_class(self)
        self.settingsclass=settingsclass(self, self.buttonclass.Arduino)
        self.hirsiz_window = None
        self.hirsiz_ui = None
        self.duman_window = None
        self.duman_ui = None
        self.base_path = Path(__file__).resolve().parent

        self.arduino_message_signal.connect(self._on_arduino_message)
        self.buttonclass.Arduino.set_message_callback(self.arduino_message_signal.emit)

        self.light_on_pixmap = QPixmap(str(self.base_path / "images" / "light_on.png"))
        self.light_off_pixmap = QPixmap(str(self.base_path / "images" / "light_off.png"))
        self.fan_on_pixmap = QPixmap(str(self.base_path / "images" / "fan_on.png"))
        self.fan_off_pixmap = QPixmap(str(self.base_path / "images" / "fan_off.png"))
        self.door_locked_pixmap = QPixmap(str(self.base_path / "images" / "door_locked.png"))
        self.door_unlocked_pixmap = QPixmap(str(self.base_path / "images" / "door_nolocked.png"))
        self.door_open_pixmap = QPixmap(str(self.base_path / "images" / "door_open.png"))
        self.door_close_pixmap = QPixmap(str(self.base_path / "images" / "door_close.png"))
        self.duman_window_pixmap = QPixmap(str(self.base_path / "images" / "fire.png"))
        self.hirsiz_window_pixmap = QPixmap(str(self.base_path / "images" / "hirsiz.png"))

        self.MainSurface.label_3.setPixmap(self.light_off_pixmap)
        self.MainSurface.label_5.setPixmap(self.fan_off_pixmap)
        self.MainSurface.label_7.setPixmap(self.door_unlocked_pixmap)
        self.MainSurface.label_12.setPixmap(self.door_close_pixmap)


        self.api_request=FastAPIRequest(self.buttonclass,self.settingsclass)




        # Default durumlar
        self.light = False
        self.fan = False
        self.door_locked = False
        self.door_open = False
        self.firesystem = False
        self.securitymode = False

        # Buton tiklama baglantilari
        self.MainSurface.light_button.clicked.connect(self._on_light_clicked)
        self.MainSurface.fan_button.clicked.connect(self._on_fan_clicked)
        self.MainSurface.door_button.clicked.connect(self._on_door_clicked)
        self.MainSurface.door_onbutton.clicked.connect(self._on_door_on_clicked)


        # Ayarlar kısmındaki iş21lemler
        self.MainSurface.firesystem_checkbox.stateChanged.connect(self._on_fire_checkbox_changed)
        self.MainSurface.securitymode_checkbox.stateChanged.connect(self._on_security_checkbox_changed)

    def _on_light_clicked(self):
        try:
            self.buttonclass.light_function()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"light click hata: {err}")

    def _on_fan_clicked(self):
        try:
            self.buttonclass.fan_function()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"fan click hata: {err}")

    def _on_door_clicked(self):
        try:
            self.buttonclass.door_function()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"door click hata: {err}")

    def _on_door_on_clicked(self):
        try:
            self.buttonclass.door_on_function()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"door on click hata: {err}")

    def _on_fire_checkbox_changed(self):
        try:
            self.settingsclass.firesystem_function()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"firesystem checkbox hata: {err}")

    def _on_security_checkbox_changed(self):
        try:
            self.settingsclass.securitymode_checkbox()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"securitymode checkbox hata: {err}")

    def _on_arduino_message(self, message):
        print(f"Arduino mesaj callback: {message}")
        if message == "motion_detected":
            print("Hirsiz penceresi aciliyor")
            self._show_hirsiz_window_centered()
        elif message == "fire_on":
            print("Duman penceresi aciliyor")
            self._show_duman_window_centered()
        else:
            print(f"Eslesen komut yok: {message}")

    def _show_hirsiz_window_centered(self):
        if self.hirsiz_window is None or sip.isdeleted(self.hirsiz_window):
            print("Hirsiz penceresi yeniden olusturuluyor")
            self.hirsiz_window = QWidget()
            self.hirsiz_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            self.hirsiz_ui = Ui_guvenlik()
            self.hirsiz_ui.setupUi(self.hirsiz_window)
            self.hirsiz_window.destroyed.connect(self._clear_hirsiz_window)
        else:
            print("Hirsiz penceresi yeniden kullaniliyor")

        self._center_window(self.hirsiz_window)
        self.hirsiz_ui.label.setPixmap(self.hirsiz_window_pixmap)
        self.hirsiz_window.show()
        self.hirsiz_window.raise_()
        self.hirsiz_window.activateWindow()

    def _show_duman_window_centered(self):
        if self.duman_window is None or sip.isdeleted(self.duman_window):
            print("Duman penceresi yeniden olusturuluyor")
            self.duman_window = QWidget()
            self.duman_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            self.duman_ui = Ui_yangin()
            self.duman_ui.setupUi(self.duman_window)
            self.duman_window.destroyed.connect(self._clear_duman_window)
        else:
            print("Duman penceresi yeniden kullaniliyor")

        self._center_window(self.duman_window)
        self.duman_ui.label.setPixmap(self.duman_window_pixmap)
        self.duman_window.show()
        self.duman_window.raise_()
        self.duman_window.activateWindow()

    def _clear_hirsiz_window(self):
        self.hirsiz_window = None
        self.hirsiz_ui = None

    def _clear_duman_window(self):
        self.duman_window = None
        self.duman_ui = None

    def _center_window(self, window):
        screen = QtGui.QGuiApplication.primaryScreen()
        if screen is None:
            return

        geometry = screen.availableGeometry()
        new_x = geometry.x() + (geometry.width() - window.width()) // 2
        new_y = geometry.y() + (geometry.height() - window.height()) // 2
        window.move(new_x, new_y)



def run():
    try:
        _install_runtime_guards()
        app = QApplication(sys.argv)
        my_window = Home_Surface()
        my_window.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Uygulama kullanici tarafindan durduruldu.")


if __name__ == "__main__":
    run()
