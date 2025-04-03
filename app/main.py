import logging

from make87_messages.image.compressed.image_jpeg_pb2 import ImageJPEG
from make87_messages.core.header_pb2 import Header
import make87
import cv2


def main():
    make87.initialize()

    topic = make87.get_publisher(name="IMAGE_DATA", message_type=ImageJPEG)

    cap = cv2.VideoCapture(make87.resolve_peripheral_name("CAMERA"))
    camera_entity_name = make87.get_config_value("CAMERA_ENTITY_NAME", "camera", str)
    verbose = make87.get_config_value("VERBOSE", False, bool)

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

        message = ImageJPEG(
            data=frame_jpeg_bytes, header=make87.create_header(Header, entity_path=f"/{camera_entity_name}")
        )
        topic.publish(message)
        if verbose:
            print(f"Published JPEG with hash: {hash(frame_jpeg_bytes)}")


if __name__ == "__main__":
    main()
