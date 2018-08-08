import os
import cv2
import queue
import imutils
import logging
import datetime
import argparse
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading

log_path = "./logs/motion_camera.log"


# Todo: add threading to this class
# Todo: add flag to this class
class CVMotionCamrea(threading.Thread):
    def __init__(self, image_path, pixel_delta_threshold, img_path_q, pixel_sample_size=500, dev_mode=False):
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format='[%(asctime)s]%(levelname)s: %(message)s')
        self.image_path = image_path
        self.pixel_sample_size = pixel_sample_size
        self.pixel_delta_threshold = pixel_delta_threshold
        self.dev_mode = dev_mode
        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.exposure_mode = "sports"
        self.camera.resolution = (1280, 720)
        self.camera_output = PiRGBArray(self.camera)
        self.prev_frame = self._bw_process_image(self._take_image(), self.pixel_sample_size)
        self.stop = threading.Event()
        self.image_path_queue = img_path_q
        threading.Thread.__init__(self)
        logging.debug("Camera Thread Starting...")

    def __del__(self):
        self.camera.close()

    def _dev_print(self, msg):
        if self.dev_mode:
            print(msg)

    def _bw_process_image(self, org_img, size):
        processed_img = imutils.resize(org_img, size)
        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_RGB2GRAY)
        return processed_img

    def _take_image(self):
        self.camera_output.truncate(0)
        self.camera.capture(self.camera_output, 'rgb')
        return self.camera_output.array

    def terminate(self):
        self.stop.set()

    def run(self):
        # Todo: Errors here, can't find _terminate, print stack frame at execution maybe?
        logging.debug("Camera Ready!")
        while not self.stop.is_set():
            image = self._take_image()
            frame = self._bw_process_image(image, self.pixel_sample_size)
            frame_diff = cv2.absdiff(self.prev_frame, frame)
            self.prev_frame = frame

            processed_diff = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
            processed_diff = cv2.dilate(processed_diff, None, iterations=2)
            (_, contours, _) = cv2.findContours(processed_diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # When motion is detected do the following
            # 1) Print any debugs in dev mode
            # 2) Save image
            # 3) Put image into combined queue
            for c in contours:
                if cv2.contourArea(c) > self.pixel_delta_threshold:
                    # Save Image
                    self._dev_print("Motion Detected!")
                    image_name = "CVImage_{}.jpg".format(datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f"))
                    logging.debug("Motion Detected! Image at: {}".format(image_name))
                    full_path = os.path.join(self.image_path, image_name)
                    # Write text to image
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bot_left_corner = (10, 50)
                    font_scale = 1
                    font_color = (255, 255, 255)
                    line_type = 2
                    cv2.putText(image, str(cv2.contourArea(c)), bot_left_corner,
                                font, font_scale, font_color, line_type)
                    cv2.imwrite(full_path, image)
                    self.image_path_queue.put(full_path)

                    self._dev_print("Path of file is: {}".format(full_path))
                    break

            # Show image diff if in dev mode
            if self.dev_mode:
                cv2.imshow("Motion Cam -- Dev Mode", frame_diff)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        logging.warning("CV Camera Thread Exiting!!!")


def run_camrea_thread(image_path, image_q):
    c = CVMotionCamrea(image_path, 75, image_q, dev_mode=False)
    c.start()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("image_path", help="Path where images taken will be stored")

    args = arg_parser.parse_args()

    img_q = queue.Queue()
    t = threading.Thread(target=run_camrea_thread, args=(args.image_path, img_q))
    t.start()
    while True:
        if not img_q.empty():
            path = img_q.get()
            print("Queue has path: {}".format(path))
