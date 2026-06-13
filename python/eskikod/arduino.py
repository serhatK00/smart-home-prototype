import serial
import queue
import threading
class Arduino():
    def __init__(self,home,port):
        self.port=port
        self.home=home
        self.x = None
        self.connected = False
        self._tx_queue = queue.Queue(maxsize=128)
        self._writer_thread = None

        try:
            self.x = serial.Serial(self.port,9600,timeout=1,write_timeout=0.2)
            self.connected = True
            self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self._writer_thread.start()
        except serial.SerialException as err:
            # Keep UI alive even if serial port is busy/unavailable.
            print(f"Arduino baglanti hatasi ({self.port}): {err}")

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
    
    def LightArduino(self):
        if self.home.light:
            self._send(b"light_on") #ışığın açılması gerektiğini yazarak anlatıyoruz
            
        else:
            self._send(b"light_off")
        pass
            
    def FanArduino(self):
        if self.home.fan:
            self._send(b"fan_on") 
        else:
            self._send(b"fan_off")
        pass
    def DoorArduino(self):
        if self.home.door_locked:
            self._send(b"door_locked") 
        else:
            self._send(b"door_open")
        pass
    def FireSystemArduino(self):
        if self.home.firesystem:
            self._send(b"firesystem_on") 
        else:
            self._send(b"firesystem_off")
        pass
    def SecurityModeArduino(self):
        if self.home.securitymode:
            self._send(b"securitymode_on")
        else:
            self._send(b"securitymode_off")
        pass
