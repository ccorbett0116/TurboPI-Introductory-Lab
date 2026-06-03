#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

def main():
    rclpy.init()
    node = Node('robot_mover')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)
    time.sleep(1.0)

    def move(lx=0.0, ly=0.0, az=0.0, duration=1.0):
        msg = Twist()
        msg.linear.x = lx
        msg.linear.y = ly
        msg.angular.z = az
        end = time.time() + duration
        while time.time() < end:
            pub.publish(msg)
            time.sleep(0.05)
        # stop
        pub.publish(Twist())
        time.sleep(0.3)

    sequence = [
        ("Forward",      dict(lx= 0.3)),
        ("Backward",     dict(lx=-0.3)),
        ("Turn left",    dict(az= 2.0)),
        ("Turn right",   dict(az=-2.0)),
        ("Strafe left",  dict(ly= 0.3)),
        ("Strafe right", dict(ly=-0.3)),
    ]

    for label, kwargs in sequence:
        print(f"{label}...")
        move(**kwargs, duration=1.0)

    print("Done.")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
