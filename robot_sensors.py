#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import sdk.FourInfrared as infrared
import time

class SensorMonitor(Node):
    def __init__(self):
        super().__init__('sensor_monitor')
        self.distance = None
        self.create_subscription(Int32, '/sonar_controller/get_distance', self.sonar_cb, 10)

    def sonar_cb(self, msg):
        self.distance = msg.data

def main():
    rclpy.init()
    node = SensorMonitor()
    line = infrared.FourInfrared()

    print("Reading sensors — press Ctrl+C to stop.\n")
    print(f"{'Time':>8}  {'Sonar(mm)':>10}  {'S0':>4} {'S1':>4} {'S2':>4} {'S3':>4}  (T=black line)")
    print("-" * 55)

    try:
        while True:
            rclpy.spin_once(node, timeout_sec=0.05)
            t = time.strftime("%H:%M:%S")
            dist = str(node.distance) if node.distance is not None else "..."
            s = line.readData()
            s0, s1, s2, s3 = ['T' if v else 'F' for v in s]
            print(f"{t:>8}  {dist:>10}  {s0:>4} {s1:>4} {s2:>4} {s3:>4}", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
