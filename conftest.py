# conftest.py
import os
import glob
import subprocess
import pytest
import time
from pyvirtualdisplay import Display
from seleniumbase import BaseCase

# ------------------------------
# Directories
# ------------------------------
SCREENSHOT_DIR = "latest_logs/screenshots"
VIDEO_DIR = "saved_videos"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
# os.makedirs(VIDEO_DIR, exist_ok=True) - Moved to fixture to ensure existence

# ------------------------------
# Start virtual display
# ------------------------------
@pytest.fixture(scope="session", autouse=True)
def start_virtual_display():
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    print(f"[VIRTUAL DISPLAY] Started Xvfb display on {display.display}")
    yield
    display.stop()
    print("[VIRTUAL DISPLAY] Stopped virtual display")

# ------------------------------
# Configure Chrome options for SeleniumBase
# ------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_chrome_options():
    # Disable SeleniumBase headless because pyvirtualdisplay handles it
    BaseCase.headless = False
    BaseCase.window_size = "1920x1080"
    BaseCase.chrome_options = [
        "--disable-infobars",
        "--disable-popup-blocking",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        "--use-gl=desktop",
        "--window-size=1920,1080"
    ]

# ------------------------------
# Record video per test case
# ------------------------------
@pytest.fixture(scope="function", autouse=True)
def record_test_video(request):
    # Get the display from env (set by pyvirtualdisplay)
    display_port = os.environ.get("DISPLAY")
    if not display_port:
        yield
        return

    test_name = request.node.name
    os.makedirs(VIDEO_DIR, exist_ok=True)
    video_path = os.path.join(VIDEO_DIR, f"{test_name}.mp4")
    
    # ffmpeg command to record the Xvfb display
    cmd = [
        "ffmpeg",
        "-y",                  # Overwrite output file
        "-f", "x11grab",       # Grab X11 display
        "-video_size", "1920x1080",
        "-framerate", "15",    # 15 fps
        "-i", display_port,    # Input display
        "-c:v", "libx264",     # Codec
        "-preset", "ultrafast",# Fast encoding
        "-pix_fmt", "yuv420p", # Pixel format for compatibility
        video_path
    ]
    
    # Start recording
    # Redirect stdout/stderr to avoid spamming test output
    # We can capture stderr to a file for debugging if needed
    log_path = os.path.join(VIDEO_DIR, f"{test_name}_ffmpeg.log")
    with open(log_path, 'w') as log_file:
        proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
    
    yield
    
    # Stop recording
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    
    if proc.returncode != 0 and proc.returncode != 255: # 255 is often returned on terminate
        print(f"[VIDEO] ffmpeg exited with code {proc.returncode}. Check {log_path}")
    else:
        print(f"[VIDEO] Saved video: {video_path}")
        # Clean up log if successful
        if os.path.exists(log_path):
            os.remove(log_path)

# ------------------------------
# Capture screenshot after each test
# ------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    yield
    test_instance = getattr(item, "instance", None)
    if isinstance(test_instance, BaseCase):
        screenshot_file = os.path.join(SCREENSHOT_DIR, f"{item.name}.png")
        try:
            test_instance.save_screenshot(screenshot_file)
            print(f"[SCREENSHOT] Saved screenshot: {screenshot_file}")
        except Exception as e:
            print(f"[SCREENSHOT] Failed to save screenshot: {e}")
