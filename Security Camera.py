import os
import sys
import Queue
import GDrive
import argparse
import subprocess
from time import sleep
from threading import Thread
from motion_camera import CVMotionCamrea

class upload_thread(Thread):
    def __init__(self, img_path_q):
        Thread.__init__(self)
        self.file_paths_q = img_path_q      # This might be a problem (loose reference when assign)

    def run(self):
        while True:
            if not self.file_paths_q.empty():
                curr_image = self.file_paths_q.get()
                GDrive.add_file(curr_image, "PIRSecurity_Pictures")

            sleep(.5)


                # logging.info("Uploading to GDrive...")
                # logging.info("Uploaded {}".format(self.file_path))

if __name__ == "__main__":
    image_q = Queue.Queue()
    threads = []

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("image_path", help="Path where images taken will be stored")
    args = arg_parser.parse_args()

    # Check that image path exists
    if not os.path.isdir(os.path.dirname(args.image_path)):
        os.mkdir(os.path.dirname(args.image_path))
    # logging.basicConfig(filename=log_path, level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s')

    # Creating pid file for duplication instance avoidance
    pid = str(os.getpid())
    pidfile = "/tmp/PIRSecurityCameraV2.pid"

    # If path exists program is already running
    if os.path.isfile(pidfile):
        # logging.info("Program already running exiting this process...")
        sys.exit()
    # Otherwise write a pid file
    with open(pidfile, "w") as f:
        f.write(pid)

    # Create GDrive send thread for posting images to GDrive
    t = upload_thread(image_q)
    t.start()
    threads.append(t)

    # Main Loop. Motion cam will run for ever
    motion_cam = CVMotionCamrea(args.image_path, 100, dev_mode=True)
    try:
        motion_cam.run(image_q)
    finally:
        # When program comes to end, remove pid file so running lock is released
        subprocess.call(["rm {}".format(pidfile)], shell=True)
        # Join all threads before completely exiting
        for t in threads:
            t.join()


# Concerns:
# Multiple imports errors
# Reference lost due to variable assignment:w

