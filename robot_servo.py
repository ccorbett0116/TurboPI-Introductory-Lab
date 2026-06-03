#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ros_robot_controller_msgs.msg import SetPWMServoState, PWMServoState
import time

# PWM servo position range: ~500 (full left/down) to ~2500 (full right/up)
# Center is ~1500
SERVO_PAN  = 2   # left/right (horizontal)
SERVO_TILT = 1   # up/down (vertical)

def main():
    rclpy.init()
    node = Node('servo_demo')
    pub = node.create_publisher(SetPWMServoState, '/ros_robot_controller/pwm_servo/set_state', 10)
    time.sleep(1.0)

    def set_servos(pan=1500, tilt=1500):
        state_pan = PWMServoState()
        state_pan.id       = [SERVO_PAN]
        state_pan.position = [pan]
        state_pan.offset   = [0]

        state_tilt = PWMServoState()
        state_tilt.id       = [SERVO_TILT]
        state_tilt.position = [tilt]
        state_tilt.offset   = [0]

        msg = SetPWMServoState()
        msg.state    = [state_pan, state_tilt]
        msg.duration = 0.02
        pub.publish(msg)
        time.sleep(0.8)

    print("Center...")
    set_servos(1500, 1500)
    time.sleep(1.0)

    print("Pan left...")
    set_servos(pan=2000)
    time.sleep(1.0)

    print("Pan right...")
    set_servos(pan=1000)
    time.sleep(1.0)

    print("Tilt up...")
    set_servos(pan=1500, tilt=2000)
    time.sleep(1.0)

    print("Tilt down...")
    set_servos(pan=1500, tilt=1000)
    time.sleep(1.0)

    print("Return to center.")
    set_servos(1500, 1500)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
