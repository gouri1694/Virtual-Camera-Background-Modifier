# Virtual-Camera-Background-Modifier
A real-time virtual camera application that uses YOLOv8 segmentation to detect and isolate humans in the webcam feed — allowing user to:  webcam feed — allowing you to:
- Blur your background
- Replace it with a custom image
- Black out everything but human

All done locally, with FastAPI backend and a simple web interface for control.

**Features**
- Real-time person segmentation using YOLOv8-seg.pt
- Customizable blur intensity
- Replace background with:
  - A black screen
  - A blurred version
  - A default image (default-office-animated.png)
- MJPEG live preview in browser
- Send processed feed to virtual webcam (via pyvirtualcam)
- Control via web UI: start/stop, preview, FPS, blur, background type
- List connected webcams
- Runs on CPU, GPU (CUDA), or Apple Silicon (MPS)

**Tech Stack**
- FastAPI
 – for REST API and backend
- Ultralytics YOLOv8
 – person segmentation
- OpenCV
 – for video processing
- PyVirtualCam
 – virtual webcam output

HTML/CSS/JS
 – frontend
