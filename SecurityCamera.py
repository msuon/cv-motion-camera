#! /usr/bin/env python3
import os
import sys
import queue
import signal
import logging
import GDrive
import traceback
import subprocess
from time import sleep
import threading
from motion_camera import CVMotionCamrea

log_path = "/home/msuon/Projects/motion_camera/logs/security_camera.log"


def error_logging_dec(func_name):
    def real_dec(func):
        def wrapper(**kwargs):
            try:
                return func(**kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                logging.error("Exception Occurred on {}: {}".format(func_name, e))
                logging.error("Traceback Info: \n{}".format(tb))
        return wrapper
    return real_dec


class UploadThread(threading.Thread):
    def __init__(self, img_q):
        threading.Thread.__init__(self)
        self.q = img_q
        self._terminate = threading.Event()
        logging.debug("GDrive Thread Starting...")

    def terminate(self):
        self._terminate.set()

    def run(self):
        logging.debug("Upload Thread Ready!")
        try:
            while not self._terminate.is_set():
                if not self.q.empty():
                    i = self.q.get()
                    logging.info("Uploading image from path: {}".format(i))
                    GDrive.add_file(i, "MotionCameraPictures")
                    logging.info("Upload {} complete!".format(i))
                    logging.debug("Removing Pictures...")
                    subprocess.call(["rm {}".format(i)], shell=True)
                    sleep(.25)
            logging.warning("GDrive Thread Exiting!!!")
        except Exception as e:
            logging.debug("Upload Thread Exiting because of exception: " + e.message)


@error_logging_dec("Cleanup Function")
def cleanup_threads(**kwargs):
    for tr in threads:
        if tr.isAlive():
            tr.terminate()
            tr.join()

@error_logging_dec("Main Thread Child Checking")
def child_thread_alive(**kwargs):
    for tr in kwargs["thread_list"]:
        if not tr.isAlive():
            return False
    sleep(1)
    return True

def handle_signals(signal, frame):
    cleanup_threads()
    logging.warning("Program Exiting: SIGNAL")
    sys.exit(0)
    # Todo: exit code isn't triggering restart.


signal.signal(signal.SIGINT, handle_signals)
signal.signal(signal.SIGTERM, handle_signals)

if __name__ == "__main__":
    image_path = "/home/msuon/Projects/motion_camera/images"
    # Initialize Logging
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='{}[%(asctime)s]%(levelname)s: %(message)s')
    logging.debug("Initializing Security Camera...")

    # Create Globals
    image_q = queue.Queue()
    threads = []

    # Check that image path exists
    if not os.path.isdir(os.path.dirname(image_path)):
        os.mkdir(os.path.dirname(image_path))

    # Create GDrive thread
    t = UploadThread(image_q)
    threads.append(t)
    t.start()

    # Create Camera thread
    t = CVMotionCamrea(image_path, 2500, image_q)
    threads.append(t)
    t.start()

    # Stability: Loop until one thread is dead
    while child_thread_alive(thread_list=threads):
        pass

    cleanup_threads(thread_list=threads)
    logging.warning("Program Exiting: Child Termination")

