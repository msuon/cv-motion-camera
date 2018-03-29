import os
import cv2
import imutils
import datetime
import argparse
from picamera import PiCamera
from picamera.array import PiRGBArray
import queue


class CVMotionCamrea():
    def __init__(self, image_path, pixel_delta_threshold,pixel_sample_size=500, dev_mode=False):
        self.image_path = image_path
        self.pixel_sample_size = pixel_sample_size
        self.pixel_delta_threshold = pixel_delta_threshold
        self.dev_mode = dev_mode
        self.camera = PiCamera()
        self.camera_output = PiRGBArray(self.camera)
        self.prev_frame = self._bw_process_image(self._take_image(), self.pixel_sample_size)

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

    def run(self, image_path_queue):
        while True:
            image = self._take_image()
            frame = self._bw_process_image(image, self.pixel_sample_size)
            frame_diff = cv2.absdiff(self.prev_frame, frame)
            self.prev_frame = frame

            processed_diff = cv2.threshold(frame_diff,100, 255, cv2.THRESH_BINARY)[1]
            processed_diff = cv2.dilate(processed_diff, None, iterations=2)
            (_,contours,_) = cv2.findContours(processed_diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # When motion is detected do the following
            # 1) Print any debugs in dev mode
            # 2) Save image
            # 3) Put image into combined queue
            for c in contours:
                if cv2.contourArea(c) > self.pixel_delta_threshold:
                    # Save Image
                    self._dev_print("Motion Detected!")
                    image_name = "CVImage_{}.jpg".format(datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f"))
                    full_path = os.path.join(self.image_path, image_name)
                    cv2.imwrite(full_path, image)
                    image_path_queue.put(full_path)
                    self._dev_print("Path of file is: {}".format(full_path))
                    break

            # Show image diff if in dev mode
            if self.dev_mode:
                cv2.imshow("Motion Cam -- Dev Mode", frame_diff)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("image_path", help="Path where images taken will be stored")

    args = arg_parser.parse_args()
    motion_cam = CVMotionCamrea(args.image_path, 75, dev_mode=True)
    q = queue.Queue()
    motion_cam.run(q)



