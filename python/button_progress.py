from PyQt6.QtGui import QPixmap
import traceback
from arduino import Arduino
import requests
import threading
import queue


class button_function_class:
    def __init__(self, home_surface):
        self.home = home_surface
        self.Arduino = Arduino(self.home, "COM11")  # Arduino sınıfını başlatırken COM portunu belirtin
        self._api_queue = queue.Queue(maxsize=256)
        self._api_worker = threading.Thread(target=self._api_sender_loop, daemon=True)
        self._api_worker.start()
        self._door_on_io_lock = threading.Lock()
        self.show_state = {
            "light": False,
            "fan": False,
            "door": False,
            "door_on": False,
        }

    #burası web api tarafından çağrıldığında ne olacağını belirleyen fonksiyonlar. Örneğin web api tarafından ışığın açılması gerektiği bilgisi geldiğinde ışığın açılması gerektiğini belirler ve arduinoya bu bilgiyi gönderir. Diğer cihazlar için de benzer şekilde çalışır.
    def light_open(self):
                self.home.light = True
                self.show_state["light"] = True
                self.home.MainSurface.light_button.setStyleSheet("background-color:red;")
                self.home.MainSurface.light_button.setText("KAPAT")
                self._set_pixmap(self.home.MainSurface.label_3, self.home.light_on_pixmap)
                self.Arduino.LightArduino() # Arduino'ya ışığın açılması gerektiğini bildir
    def light_close(self):
                self.home.light = False
                self.show_state["light"] = False
                self.home.MainSurface.light_button.setStyleSheet("background-color:green;")
                self.home.MainSurface.light_button.setText("AC")
                self._set_pixmap(self.home.MainSurface.label_3, self.home.light_off_pixmap)
                self.Arduino.LightArduino() # Arduino'ya ışığın kapatılması gerektiğini bildir

    def fan_open(self):
                self.home.fan = True
                self.show_state["fan"] = True
                self.home.MainSurface.fan_button.setStyleSheet("background-color:red;")
                self.home.MainSurface.fan_button.setText("KAPAT")
                self._set_pixmap(self.home.MainSurface.label_5, self.home.fan_on_pixmap)
                self.Arduino.FanArduino() # Arduino'ya fanın açılması gerektiğini bildir
    def fan_close(self):
                self.home.fan = False
                self.show_state["fan"] = False
                self.home.MainSurface.fan_button.setStyleSheet("background-color:green;")
                self.home.MainSurface.fan_button.setText("AC")
                self._set_pixmap(self.home.MainSurface.label_5, self.home.fan_off_pixmap)
                self.Arduino.FanArduino() # Arduino'ya fanın kapatılması gerektiğini bildir
    def door_open(self):
                self.home.door_locked = False
                self.show_state["door"] = False
                self.home.MainSurface.door_button.setStyleSheet("background-color:green;")
                self.home.MainSurface.door_button.setText("AC")
                self._set_pixmap(self.home.MainSurface.label_7, self.home.door_unlocked_pixmap)
                self.Arduino.DoorArduino() # Arduino'ya kapının kilidini açılması gerektiğini bildir
    def door_close(self):
                self.home.door_locked = True
                self.show_state["door"] = True
                self.home.MainSurface.door_button.setStyleSheet("background-color:red;")
                self.home.MainSurface.door_button.setText("KAPAT")
                self._set_pixmap(self.home.MainSurface.label_7, self.home.door_locked_pixmap)
                self.Arduino.DoorArduino() # Arduino'ya kapının kilitlenmesi gerektiğini bildir

    def door_on_open(self):
        try:
            self.home.door_open = True
            self.show_state["door_on"] = True
            self.home.MainSurface.door_onbutton.setStyleSheet("background-color:red;")
            self.home.MainSurface.door_onbutton.setText("KAPAT")
            self._set_pixmap(self.home.MainSurface.label_12, self.home.door_open_pixmap)
            self.Arduino.DoorOnArduino() # Arduino'ya kapının açılması gerektiğini bildir
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"door_on_open hata: {err}")

    def door_on_close(self):
        try:
            self.home.door_open = False
            self.show_state["door_on"] = False
            self.home.MainSurface.door_onbutton.setStyleSheet("background-color:green;")
            self.home.MainSurface.door_onbutton.setText("AC")
            self._set_pixmap(self.home.MainSurface.label_12, self.home.door_close_pixmap)
            self.Arduino.DoorOnArduino() # Arduino'ya kapının kapatılması gerektiğini bildir
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"door_on_close hata: {err}")
                
           
    def send_command(self,device,action):
        try:
            self._api_queue.put_nowait((device, action))
        except queue.Full:
            print(f"API kuyrugu dolu, komut atlandi ({device}:{action})")

    def _api_sender_loop(self):
        while True:
            device, action = self._api_queue.get()
            self._post_command(device, action)
    
          

    def _post_command(self, device, action):
        url = "http://127.0.0.1:8000/device"
        try:
            requests.post(
                url,
                json={"device": device, "action" : action},
                headers={"X-Origin": "desktop-ui"},
                timeout=0.5,
            )
        except requests.RequestException as err:
            print(f"API istegi basarisiz ({device}:{action}): {err}")
        except Exception as err:
            print(f"API istegi beklenmeyen hata ({device}:{action}): {err}")
    #burası python tarafında butonlara basıldığında ne olacağını belirleyen fonksiyonlar. Örneğin ışık butonuna basıldığında ışığın açılması veya kapatılması gerektiğini belirler ve arduinoya bu bilgiyi gönderir. Diğer cihazlar için de benzer şekilde çalışır.
    def light_function(self):
            try:
                if not self.home.light:
                    self.light_open()
                    self.send_command("light","on")
                else:
                    self.light_close()
                    self.send_command("light","off")
            except KeyboardInterrupt:
                return
            except Exception as err:
                print(f"light_function hata: {err}")

    def fan_function(self):
        try:
            if not self.home.fan:
                self.fan_open()
                self.send_command("fan","on")
            else:
                self.fan_close()
                self.send_command("fan","off")
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"fan_function hata: {err}")

    
    def door_function(self):
        try:
            if not self.home.door_locked:
                self.door_close()
                self.send_command("door","lock")
            else:
                self.door_open()
                self.send_command("door","unlock")
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"door_function hata: {err}")

    def door_on_function(self):
        try:
            if not self.home.door_open:
                self.home.door_open = True
                self.show_state["door_on"] = True
                self.home.MainSurface.door_onbutton.setStyleSheet("background-color:red;")
                self.home.MainSurface.door_onbutton.setText("KAPAT")
                self._set_pixmap(self.home.MainSurface.label_12, self.home.door_open_pixmap)
                threading.Thread(target=self._door_on_io_worker, args=("open",), daemon=True).start()
            else:
                self.home.door_open = False
                self.show_state["door_on"] = False
                self.home.MainSurface.door_onbutton.setStyleSheet("background-color:green;")
                self.home.MainSurface.door_onbutton.setText("AC")
                self._set_pixmap(self.home.MainSurface.label_12, self.home.door_close_pixmap)
                threading.Thread(target=self._door_on_io_worker, args=("close",), daemon=True).start()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"door_on_function hata: {err}")

    def _door_on_io_worker(self, action):
        # Keep potentially slow I/O off the UI thread.
        with self._door_on_io_lock:
            self.Arduino.DoorOnArduino()
            self.send_command("door_on", action)

    def _set_pixmap(self, label, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Resim yuklenemedi: {path}")
        label.setPixmap(pixmap)

