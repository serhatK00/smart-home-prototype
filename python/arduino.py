import serial
import queue
import threading
import time
class Arduino():
    def __init__(self,home,port):
        self.port=port
        self.home=home
        self.x = None
        self.connected = False
        self._tx_queue = queue.Queue(maxsize=128)
        self._writer_thread = None
        self._reader_thread = None
        self._message_callback = None

        try:
            self.x = serial.Serial(self.port,9600,timeout=1,write_timeout=0.2)
            self.connected = True
            self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self._writer_thread.start()
            self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self._reader_thread.start()
        except serial.SerialException as err:
            # Keep UI alive even if serial port is busy/unavailable.
            print(f"Arduino baglanti hatasi ({self.port}): {err}")

    def set_message_callback(self, callback):
        self._message_callback = callback

    def _writer_loop(self):
        while self.connected and self.x is not None:
            try:
                message = self._tx_queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                self.x.write(message)
            except serial.SerialTimeoutException:
                print(f"Arduino yazma zaman asimi ({self.port})")
            except serial.SerialException as err:
                self.connected = False
                print(f"Arduino yazma hatasi ({self.port}): {err}")

    def _send(self, message):
        if not self.connected or self.x is None:
            return

        try:
            self._tx_queue.put_nowait(message)
        except queue.Full:
            # Drop oldest user spam bursts instead of freezing the UI.
            print("Arduino gonderim kuyrugu dolu, komut atlandi")

    def _dispatch_message(self, message):
        if self._message_callback is None:
            return

        try:
            self._message_callback(message)
        except Exception as err:
            print(f"Arduino mesaj callback hatasi: {err}")

    def _reader_loop(self):
        while self.connected and self.x is not None:
            try:
                if self.x.in_waiting > 0:
                    mesaj = self.x.readline().decode("utf-8", errors="replace").strip()
                    if mesaj:
                        print("Gelen mesaj:", mesaj)
                        self._dispatch_message(mesaj)
                else:
                    time.sleep(0.05)
            except serial.SerialException as err:
                self.connected = False
                print(f"Arduino okuma hatasi ({self.port}): {err}")
            except Exception as err:
                print(f"Arduino okuma beklenmeyen hata ({self.port}): {err}")
    
    def LightArduino(self):
        if self.home.light:
            self._send(b"light_on\n") #ışığın açılması gerektiğini yazarak anlatıyoruz
            
        else:
            self._send(b"light_off\n")
        pass
            
    def FanArduino(self):
        if self.home.fan:
            self._send(b"fan_on\n") 
        else:
            self._send(b"fan_off\n")
        pass
    def DoorArduino(self):
        if self.home.door_locked:
            self._send(b"door_locked\n") 
        else:
            self._send(b"door_open\n")
        pass
    def DoorOnArduino(self):
        if self.home.door_open:
            self._send(b"open_door\n") 
        else:
            self._send(b"close_door\n")
        pass
    def FireSystemArduino(self):
        if self.home.firesystem:
            self._send(b"firesystem_on\n") 
        else:
            self._send(b"firesystem_off\n")
        pass
    def SecurityModeArduino(self):
        print(f"Security mode durumu(python): {self.home.securitymode}")
        if self.home.securitymode:
            self._send(b"securitymode_on\n")
            print("Security mode acildi, Arduino'ya gonderildi")
        else:
            self._send(b"securitymode_off\n")
        
        pass
