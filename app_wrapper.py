import webview
import threading
from fastapi import FastAPI
import uvicorn

app = FastAPI()


def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    webview.create_window("Qrn-App", "http://127.0.0.1:8000")
    webview.start()


