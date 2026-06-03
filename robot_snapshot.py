#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2
import sys

OUTPUT = '/tmp/snapshot.jpg'

class SnapshotNode(Node):
    def __init__(self):
        super().__init__('snapshot_node')
        self.saved = False
        self.sub = self.create_subscription(Image, '/image_raw', self.callback, 10)

    def callback(self, msg):
        if self.saved:
            return

        # Convert raw bytes to numpy array based on encoding
        enc = msg.encoding.lower()
        data = np.frombuffer(msg.data, dtype=np.uint8)

        if enc in ('rgb8',):
            img = data.reshape((msg.height, msg.width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif enc in ('bgr8',):
            img = data.reshape((msg.height, msg.width, 3))
        elif enc in ('mono8', '8uc1'):
            img = data.reshape((msg.height, msg.width))
        elif enc in ('bgra8', 'rgba8'):
            img = data.reshape((msg.height, msg.width, 4))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR if 'bgr' in enc else cv2.COLOR_RGBA2BGR)
        elif enc in ('yuv422_yuy2', 'yuyv', 'yuv422'):
            img = data.reshape((msg.height, msg.width, 2))
            img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUY2)
        elif enc in ('yuv420', 'nv12'):
            img = data.reshape((msg.height * 3 // 2, msg.width))
            img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_NV12)
        else:
            print(f"Unsupported encoding: {msg.encoding}")
            sys.exit(1)

        cv2.imwrite(OUTPUT, img)
        print(f"Saved {msg.width}x{msg.height} ({msg.encoding}) -> {OUTPUT}")
        self.saved = True

def main():
    rclpy.init()
    node = SnapshotNode()
    print(f"Waiting for image on /image_raw ...")

    import time
    deadline = time.time() + 10.0
    while not node.saved and time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)

    if not node.saved:
        print("Timeout: no image received within 10 seconds.")
        sys.exit(1)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
