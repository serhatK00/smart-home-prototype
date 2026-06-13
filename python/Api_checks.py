from pydantic import BaseModel
import uvicorn
from button_progress import button_function_class 
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtCore import QThread
from fastapi_run import FastApi_class
import threading


class FastAPIRequest(QObject):
    command_received = pyqtSignal(str, str)
    
    def __init__(self,buton_function_class,settingsclass):
        super().__init__()
        self.button_function_class = buton_function_class
        self.settings_class=settingsclass
        self.state_lock = threading.Lock()
        self.command_received.connect(self._handle_command, Qt.ConnectionType.QueuedConnection)
        self.api_thread=QThread()
        self.api_run=FastApi_class(status_getter=self.get_status)
        self.api_run.moveToThread(self.api_thread)
        self.api_thread.started.connect(self.api_run.run_server)
        self.api_run.commands.connect(self.read_website)
        self.api_thread.start()
    
    

      
    @pyqtSlot(str, str)
    def read_website(self,device,action): 
        try:
            # FastAPI thread'inden gelen komutu ana Qt thread'ine aktar.
            self.command_received.emit(device, action)
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"read_website hata: {err}")

    @pyqtSlot(str, str)
    def _handle_command(self, device, action):
        try:
            # komut içerisinde mesela şöyle bir dict olucak diyelim
            # {"device": "light",
            # "action": "on"}
            if device == "light":
                if action == "on":
                    self.button_function_class.light_open()
                elif action == "off":
                    self.button_function_class.light_close()
            elif device == "fan":
                if action == "on":
                    self.button_function_class.fan_open()
                elif action == "off":
                    self.button_function_class.fan_close()
            elif device == "door":
                if action == "lock":
                    self.button_function_class.door_close()
                elif action == "unlock":
                    self.button_function_class.door_open()
            elif device == "door_on":
                if action in ("close", "lock"):
                    self.button_function_class.door_on_close()
                elif action in ("open", "unlock"):
                    self.button_function_class.door_on_open()
            elif device == "firesystem":
                if action == "on":
                    self.settings_class.set_firesystem_checked(True)
                    self.settings_class.firesystem_activate()
                elif action == "off":
                    self.settings_class.set_firesystem_checked(False)
                    self.settings_class.firesystem_deactivate()
            elif device == "securitymode":
                if action == "on":
                    self.settings_class.set_securitymode_checked(True)
                    self.settings_class.securitymode_activate()
                elif action == "off":
                    self.settings_class.set_securitymode_checked(False)
                    self.settings_class.securitymode_deactivate()
            else:
                return {"status": "error", "message": "Bilinmeyen cihaz"}
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"_handle_command hata ({device}:{action}): {err}")

    def get_status(self):
        with self.state_lock:
            return {
                "light": self.button_function_class.show_state["light"],
                "fan": self.button_function_class.show_state["fan"],
                "door": self.button_function_class.show_state["door"],
                "door_locked": self.button_function_class.show_state["door"],
                "door_on": self.button_function_class.show_state["door_on"],
                "firesystem": self.settings_class.show_state["firesystem"],
                "securitymode": self.settings_class.show_state["securitymode"],
            }
