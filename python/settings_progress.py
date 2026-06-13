from arduino import Arduino
import requests
import threading
import queue
class settingsclass():
    def __init__(self, home, arduino=None):
        self.home = home
        self.arduino = arduino if arduino is not None else Arduino(self.home, "com11")
        self._api_queue = queue.Queue(maxsize=256)
        self._api_worker = threading.Thread(target=self._api_sender_loop, daemon=True)
        self._api_worker.start()
        self._firesystem_io_lock = threading.Lock()
        self.show_state = {
            "firesystem": False,
            "securitymode": False,
        }

    def set_firesystem_checked(self, checked):
        checkbox = self.home.MainSurface.firesystem_checkbox
        checkbox.blockSignals(True)
        checkbox.setChecked(checked)
        checkbox.blockSignals(False)
        self.home.firesystem = checked
        self.show_state["firesystem"] = checked

    def set_securitymode_checked(self, checked):
        checkbox = self.home.MainSurface.securitymode_checkbox
        checkbox.blockSignals(True)
        checkbox.setChecked(checked)
        checkbox.blockSignals(False)
        self.home.securitymode = checked
        self.show_state["securitymode"] = checked


    def firesystem_activate(self):
        try:
            self.set_firesystem_checked(True)
            self.arduino.FireSystemArduino() #arduinoya haber ver
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"firesystem_activate hata: {err}")
    def firesystem_deactivate(self):
        try:
            self.set_firesystem_checked(False)
            self.arduino.FireSystemArduino()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"firesystem_deactivate hata: {err}")
    def securitymode_activate(self):
        try:
            self.set_securitymode_checked(True)
            self.arduino.SecurityModeArduino()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"securitymode_activate hata: {err}")
    def securitymode_deactivate(self):
        try:
            self.set_securitymode_checked(False)
            self.arduino.SecurityModeArduino()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"securitymode_deactivate hata: {err}")

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
    def firesystem_function(self):
        try:
            checked = self.home.MainSurface.firesystem_checkbox.isChecked()
            self.home.firesystem = checked
            self.show_state["firesystem"] = checked
            threading.Thread(target=self._firesystem_io_worker, args=(checked,), daemon=True).start()
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"firesystem_function hata: {err}")

    def _firesystem_io_worker(self, checked):
        # Run serial/API I/O outside the Qt UI thread.
        with self._firesystem_io_lock:
            self.home.firesystem = checked
            self.arduino.FireSystemArduino()
            self.send_command("firesystem", "on" if checked else "off")

    def securitymode_checkbox(self):
        try:
            if self.home.MainSurface.securitymode_checkbox.isChecked():
                self.home.securitymode = True
                self.show_state["securitymode"] = True
                self.arduino.SecurityModeArduino()
                self.send_command("securitymode","on")
            else:
                self.home.securitymode = False
                self.show_state["securitymode"] = False
                self.arduino.SecurityModeArduino()
                self.send_command("securitymode","off")
        except KeyboardInterrupt:
            return
        except Exception as err:
            print(f"securitymode_checkbox hata: {err}")
