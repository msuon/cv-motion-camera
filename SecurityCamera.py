import os
import sys
import queue
import logging
import GDrive
import argparse
import subprocess
from time import sleep
from threading import Thread
from motion_camera import CVMotionCamrea

log_path = "/home/msuon/Projects/motion_camera/logs/security_camera.log"
# class upload_thread(Thread):
#     def __init__(self, img_path_q):
#         Thread.__init__(self)
#         self.file_paths_q = img_path_q      # This might be a problem (loose reference when assign)
#
#     def run(self):
#         while True:
#             if not self.file_paths_q.empty():
#                 curr_image = self.file_paths_q.get()
#                 GDrive.add_file(curr_image, "PIRSecurity_Pictures")
#
#             sleep(.5)


def upload_thread(image_path, image_q):
    while True:
        if not image_q.empty():
            i = image_q.get()
            logging.info("Uploading image from path: {}".format(i))
            GDrive.add_file(i, "MotionCameraPictures")
            logging.info("Upload {} complete!".format(i))
            logging.debug("Removing Pictures...")
            subprocess.call(["rm {}".format(i)], shell=True)

            sleep(.25)


def camera_thread(img_path, img_q):
    c = CVMotionCamrea(img_path, 75)
    c.run(image_q)

if __name__ == "__main__":
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument("image_path", help="Path where images taken will be stored")
#     args = arg_parser.parse_args()
    
    image_path = "/home/msuon/Projects/motion_camera/images"
    # Initialize Logging
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s')
    logging.debug("Starting Security Camera...")

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
    t = Thread(target=upload_thread, args=(image_path, image_q))
    threads.append(t)
    t.start()

    logging.debug("Camera Thread Starting...")
    # Create Camera thread
    t = Thread(target=camera_thread, args=(image_path, image_q))
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

