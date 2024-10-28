import logging

from make87_messages.image.compressed.image_jpeg_pb2 import ImageJPEG
from make87 import initialize, get_publisher_topic, resolve_topic_name, resolve_peripheral_name
import cv2


def main():
    initialize()

    topic_name = resolve_topic_name("IMAGE_DATA")
    topic = get_publisher_topic(name=topic_name, message_type=ImageJPEG)

    cap = cv2.VideoCapture(resolve_peripheral_name("CAMERA"))

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
