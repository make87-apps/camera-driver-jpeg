import logging

from make87_messages.image.ImageJPEG_pb2 import ImageJPEG
from make87 import get_topic, topic_names, peripheral_names, PublisherTopic
import cv2


def main():
    topic = get_topic(name=topic_names.IMAGE_DATA)

    cap = cv2.VideoCapture(peripheral_names.CAMERA)

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Error: failed to capture frame.")
            break

        ret, frame_jpeg = cv2.imencode(".jpeg", frame)
        if not ret:
            logging.error("Error: Could not encode frame to JPEG.")
            break

        frame_jpeg_bytes = frame_jpeg.tobytes()

        message = ImageJPEG(data=frame_jpeg_bytes)
        topic.publish(message)

        print(f"Published JPEG with hash: {hash(frame_jpeg_bytes)}")


if __name__ == "__main__":
    main()
