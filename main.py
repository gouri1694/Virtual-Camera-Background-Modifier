import uvicorn
import numpy as np
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import threading
from stream_utils import Streaming
from fastapi.responses import StreamingResponse
import time
import cv2

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

stream_thread = None

streaming = Streaming()

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

@app.get('/preview')
def preview_video(
    source: str = Query("0"),
    fps: int = Query(15),
    blur_strength: int = Query(21),
    background: str = Query("none")
):
    streaming.update_streaming_config(in_source=source, out_source=None, fps=fps, blur_strength=blur_strength, background=background)

    source_index = int(source) if source.isdigit() else source
    cap = cv2.VideoCapture(source_index)

    if not cap.isOpened():
        return JSONResponse(content={"error": f"Camera {source} could not be opened"}, status_code=400)

    model = streaming.model
    device = streaming.device

    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                break

            results = model.predict(source=frame, save=False, save_txt=False, stream=True, retina_masks=True, verbose=False, device=device)
            mask = streaming.generate_mask_from_result(results)

            if mask is not None:
                if background == "blur":
                    result_frame = streaming.apply_blur_with_mask(frame, mask, blur_strength=blur_strength)
                elif background == "none":
                    result_frame = streaming.apply_black_background(frame, mask)
                elif background == "default":
                    result_frame = streaming.apply_custom_background(frame, mask)
                else:
                    result_frame = frame
            else:
                result_frame = frame  # fallback if mask is None

            # Encode frame for MJPEG stream
            ret, buffer = cv2.imencode('.jpg', result_frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(1 / 15)  # 15 FPS preview

        cap.release()

    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/stop_preview")
def stop_preview():
    streaming.stop_preview()
    return {"message": "Preview stopped"}

@app.get("/start")
def start_stream(
    source: str = Query("0"),
    fps: int = Query(15),
    blur_strength: int = Query(21),
    background: str = Query("none")
):
    streaming.update_streaming_config(in_source=source, out_source=None, fps=fps, blur_strength=blur_strength, background=background)

    global stream_thread

    if streaming.running:
        return JSONResponse(content={"message": "Stream already running"}, status_code=400)

    if fps < 1 or fps > 60:
        return JSONResponse(content={"message": "Invalid FPS value (1-60)"}, status_code=400)

    stream_thread = threading.Thread(
        target=streaming.stream_video, args=()
    )
    stream_thread.start()
    return {"message": f"Streaming started from source: {fps} FPS and blur strength {blur_strength}"}


@app.get("/stop")
def stop_stream():
    streaming.update_running_status()
    return {"message": "Streaming stopped"}


@app.get("/devices")
def devices():
    return streaming.list_available_devices()


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
