import uvicorn
from PyQt6.QtCore import QObject, pyqtSignal
from pydantic import BaseModel
from fastapi import FastAPI, Request

class Command(BaseModel):
    device: str
    action: str
class FastApi_class(QObject):
    commands=pyqtSignal(str,str)
    def __init__(self, status_getter=None):
        super().__init__()
        self.app=FastAPI()
        self.status_getter = status_getter
        self.setup_routes()
    def setup_routes(self):
        @self.app.post("/device")
        def read_website(komut:Command, request: Request):
            try:
                if request.headers.get("x-origin", "").lower() == "desktop-ui":
                    return {"status":"success", "source":"local-skip"}
                self.commands.emit(komut.device,komut.action)
            except Exception as err:
                return {"status": "error", "message": str(err)}
            return {"status":"success"}

        @self.app.get("/status")
        def get_status():
            try:
                if self.status_getter is not None:
                    state = self.status_getter()
                    # Hem eski (root) hem yeni (data) formati birlikte dondur.
                    return {"status": "success", "data": state, **state}
                return {"status": "error", "message": "status_getter tanimli degil"}
            except Exception as err:
                return {"status": "error", "message": str(err)}
        
    def run_server(self):
        try:
            # QThread icinde calistigi icin uvicorn signal handler'larini kapat.
            config = uvicorn.Config(
                self.app,
                host="127.0.0.1",
                port=8000,
                log_level="warning",
                access_log=False,
            )
            server = uvicorn.Server(config)
            server.install_signal_handlers = lambda: None
            server.run()
        except KeyboardInterrupt:
            return