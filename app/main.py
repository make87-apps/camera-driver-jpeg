import logging
import threading
from threading import Thread

import zenoh
from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface
from make87_messages.image.compressed.image_jpeg_pb2 import ImageJPEG
from make87_messages.core.header_pb2 import Header
import make87
import cv2

last_image_lock = threading.Lock()
last_image: bytes


def get_last_camera_image() -> bytes:
    """Get the latest camera image as bytes."""
    with last_image_lock:
        if last_image is not None:
            return last_image
        else:
            return b""


def handle_get_last_camera_image(query: zenoh.Query):
    img_msg = get_last_camera_image()

    header = Header(entity_path="/camera")
    header.timestamp.GetCurrentTime()
    img_msg = ImageJPEG(data=img_msg, header=header)

    message_encoded = ProtobufEncoder(message_type=ImageJPEG).encode(img_msg)
    query.reply(key_expr=query.key_expr, payload=message_encoded)


def publish_camera_image(config: make87.config.ApplicationConfig):
    global last_image

    zenoh_interface = ZenohInterface(name="zenoh-client", make87_config=config)

    topic = zenoh_interface.get_publisher(name="IMAGE")

    cap = cv2.VideoCapture(make87.resolve_peripheral_name("CAMERA"))

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

        header = Header(entity_path="/camera")
        message = ImageJPEG(data=frame_jpeg_bytes, header=header)
        with last_image_lock:
            last_image = message.data
        payload = ProtobufEncoder(message_type=ImageJPEG).encode(message)
        topic.put(payload=payload)


def main():
    config = make87.config.load_config_from_env()

    camera_thread = Thread(target=publish_camera_image, args=(config,))
    camera_thread.start()

    zenoh_interface = ZenohInterface(name="zenoh-client", make87_config=config)
    image_provider = zenoh_interface.get_provider(name="GET_CAMERA_IMAGE", handler=handle_get_last_camera_image)

    camera_thread.join()


if __name__ == "__main__":
    main()
