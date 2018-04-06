import os
import sys
import queue
import logging
import GDrive
import argparse
import traceback
import subprocess
from time import sleep
from threading import Thread
from motion_camera import CVMotionCamrea

log_path = "/home/msuon/Projects/motion_camera/logs/security_camera.log"


def error_logging_dec(func_name):
    def real_dec(func):
        def wrapper(**kwargs):
            try:
                func(**kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                logging.error("Exception Occurred on {}: {}".format(func_name, e))
                logging.error("Traceback Info: \n{}".format(tb))
        return wrapper
    return real_dec


@error_logging_dec("Upload Thread")
def upload_thread(**kwargs):
    while True:
        if not kwargs["img_q"].empty():       # There's confusion here as to where "image_q" came from before kwargs was implemented
            i = kwargs["img_q"].get()
            logging.info("Uploading image from path: {}".format(i))
            GDrive.add_file(i, "MotionCameraPictures")
            logging.info("Upload {} complete!".format(i))
            logging.debug("Removing Pictures...")
            subprocess.call(["rm {}".format(i)], shell=True)

            sleep(.25)


@error_logging_dec("Camera Thread")
def camera_thread(**kwargs):
    logging.debug("Initializing Motion Camera...")
    c = CVMotionCamrea(kwargs["img_path"], 1000)
    logging.debug("Motion Camera Ready!")
    c.run(image_q)  # This is using the global scoped image_q
    # c.run(kwargs["img_q"])  # This is using the keyword args given via function call

if __name__ == "__main__":
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument("image_path", help="Path where images taken will be stored")
#     args = arg_parser.parse_args()
    
    image_path = "/home/msuon/Projects/motion_camera/images"
    # Initialize Logging
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s')
    logging.debug("Initializing Security Camera...")

    # Create Globals
    image_q = queue.Queue()
    threads = []

    # Check that image path exists
    if not os.path.isdir(os.path.dirname(image_path)):
        os.mkdir(os.path.dirname(image_path))

    # Creating pid file for duplication instance avoidance
    pid = str(os.getpid())
    pidfile = "/tmp/SecurityCamera.pid"

    # If path exists program is already running otherwise write pid file
    if os.path.isfile(pidfile):
        logging.info("Program already running exiting this process...")
        sys.exit()
    with open(pidfile, "w") as f:
        f.write(pid)

    logging.debug("GDrive Thread Starting...")
    # Create GDrive thread
    t = Thread(target=upload_thread, kwargs={"img_path": image_path, "img_q": image_q})
    threads.append(t)
    t.start()

    logging.debug("Camera Thread Starting...")
    # Create Camera thread
    t = Thread(target=camera_thread, kwargs={"img_path": image_path, "img_q": image_q})
    threads.append(t)
    t.start()

    for t in threads:
        t.join()

    logging.debug("Removing PID File...")
    subprocess.call(["rm {}".format(pidfile)], shell=True)
    logging.warning("Program exiting...")

    # # Main Loop. Motion cam will run for ever motion_cam = CVMotionCamrea(args.image_path, 100, dev_mode=True)
    # try:
    #     motion_cam.run(image_q)
    # finally:
    #     # When program comes to end, remove pid file so running lock is released
    #     subprocess.call(["rm {}".format(pidfile)], shell=True)
    #     # Join all threads before completely exiting
    #     for t in threads:
    #         t.join()


# Concerns:
# Multiple imports errors
# Reference lost due to variable assignment:w

