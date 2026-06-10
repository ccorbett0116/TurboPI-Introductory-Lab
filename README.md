# COSC 3P71 — Lab 3: Introduction to Robot Control
**Duration:** 2 hours  
**Prerequisites:** Labs 1 & 2 (robot assembly)

---

## Overview

In this lab you will connect to your TurboPi robot and control it programmatically using Python and ROS 2. By the end of the lab you will have:

- Connected to the robot over the network using VNC
- Changed the robot's Wi-Fi network configuration
- Understood and run scripts that move the robot and take a photo
- Controlled the camera pan/tilt servos in code
- (Bonus) Read live data from the robot's ultrasonic distance sensor and 4-channel infrared line sensor

---

## Background: How the Robot's Software Works

Your TurboPi runs **Raspberry Pi OS (Debian 12)** on its onboard computer. All robot software runs inside a **Docker container** — a self-contained Linux environment that bundles the robot's software and all its dependencies together, isolated from the rest of the system.

Inside that container, the robot runs **ROS 2 Humble** (Robot Operating System). ROS 2 is the industry-standard framework for robot software. It works around a central concept: **topics**.

A **topic** is a named data channel. Nodes (running programs) can **publish** data to a topic or **subscribe** to receive data from it. For example:

- The camera publishes images to `/image_raw`
- The motor controller subscribes to `/cmd_vel` for velocity commands
- The sonar sensor publishes distance readings to `/sonar_controller/get_distance`

Your Python scripts interact with the robot entirely through these topics — you never talk to hardware directly.

---

## Part A: Connecting to the Robot and Changing the Wi-Fi SSID

### Step 0 — Install Required Software

Before connecting to the robot, make sure you have both of these installed on your laptop:

| Tool | Purpose | Download |
|------|---------|----------|
| **TigerVNC Viewer** | See and control the robot's desktop | https://sourceforge.net/projects/tigervnc/ |
| **PuTTY** | SSH terminal to run commands on the robot | https://www.putty.org/ |

### Step 1 — Connect via VNC

**VNC** (Virtual Network Computing) lets you see and control the robot's desktop from your laptop, as if you had a monitor plugged into it.

1. Open **TigerVNC Viewer** on your laptop
2. In the **VNC server** field, type the IP address of your robot (written on the label on the robot) and click **Connect**
3. When prompted for a password, enter: `raspberrypi`
4. You should see the robot's desktop appear

> **Troubleshooting:** If you cannot connect, make sure your laptop is on the same Wi-Fi network as the robot. Ask your instructor for the correct network name.

### Step 2 — Open a Terminal on the Robot

On the robot's desktop, right-click and select **Open Terminal** (or click the terminal icon in the taskbar).

### Step 3 — Edit the Wi-Fi Configuration File

By default every robot broadcasts the same Wi-Fi hotspot name, which makes it impossible to tell them apart. Your task is to give your robot a unique name.

The robot's Wi-Fi settings are stored in a plain Python file:

```
/home/pi/hiwonder-toolbox/wifi_conf.py
```

Open it with the nano text editor:

```bash
nano /home/pi/hiwonder-toolbox/wifi_conf.py
```

You will see:

```python
WIFI_MODE = 1
#WIFI_AP_SSID = 'HW-Robot'
#WIFI_AP_PASSWORD = 'hiwonder'
WIFI_STA_SSID = 'hiwonder_5G'
WIFI_STA_PASSWORD = 'hiwonder'
```

**What these mean:**
- `WIFI_MODE = 1` — the robot is in **AP mode**: it creates its own Wi-Fi hotspot that other devices can connect to. This is the default mode and what we will keep.
- `WIFI_AP_SSID` — the name of the hotspot the robot broadcasts (currently commented out, so it defaults to `HW-Robot`)
- `WIFI_AP_PASSWORD` — the hotspot password

**Your task:** Uncomment `WIFI_AP_SSID` and change it to something unique — for example, your name or student ID. You can also change the password if you like.

```python
WIFI_MODE = 1
WIFI_AP_SSID = 'HW-YourName'
WIFI_AP_PASSWORD = 'hiwonder'
```

To uncomment a line in nano, delete the `#` at the start of the line.

Save the file: press `Ctrl+X`, then `Y`, then `Enter`.

To apply the change, reboot the robot:

```bash
sudo reboot
```

After about 30 seconds, you should see your new hotspot name appear in your laptop's Wi-Fi list. Reconnect to it (using the password you set), then reconnect VNC and PuTTY at the same IP address as before.

---

## Part B: Programmatic Robot Control

### Connecting via SSH (PuTTY)

While VNC gives you a full desktop, it's easier to run scripts from an SSH terminal. Open PuTTY and fill in:

- **Host Name:** the IP address of your robot
- **Port:** 22
- **Connection type:** SSH

Click **Open**, then log in with username `pi` and password `raspberrypi`. You now have a terminal directly on the robot.

### Getting your scripts onto the robot

PuTTY installs a companion tool called **PSCP** (PuTTY Secure Copy) that lets you copy files to the robot over SSH from your Windows command prompt.

Open **Command Prompt** on your laptop and run (replace `192.168.X.X` with your robot's IP):

```cmd
pscp C:\path\to\robot_move.py     pi@192.168.X.X:/tmp/
pscp C:\path\to\robot_snapshot.py pi@192.168.X.X:/tmp/
pscp C:\path\to\robot_servo.py    pi@192.168.X.X:/tmp/
pscp C:\path\to\robot_sensors.py  pi@192.168.X.X:/tmp/
```

Enter the password `raspberrypi` when prompted. If `pscp` is not found, use the full path: `"C:\Program Files\PuTTY\pscp.exe"`.

Once the files are on the robot, copy them into the Docker container from your PuTTY SSH terminal:

```bash
docker cp /tmp/robot_move.py     turbopi:/tmp/
docker cp /tmp/robot_snapshot.py turbopi:/tmp/
docker cp /tmp/robot_servo.py    turbopi:/tmp/
docker cp /tmp/robot_sensors.py  turbopi:/tmp/
```

### Running a script

All scripts must be run **inside the Docker container** where ROS 2 is installed. The command to do this looks long, but it's the same every time — only the script name changes:

```bash
docker exec --user ubuntu turbopi bash -c \
  'source /opt/ros/humble/setup.bash && \
   source /home/ubuntu/ros2_ws/install/setup.bash && \
   python3 /tmp/SCRIPT_NAME.py'
```

**What each part means:**

| Part | Meaning |
|------|---------|
| `docker exec` | Run a command inside a running container |
| `--user ubuntu` | Run as the `ubuntu` user (who owns the ROS installation) |
| `turbopi` | The name of the container to run in |
| `bash -c '...'` | Start a bash shell and run everything inside the quotes |
| `source /opt/ros/humble/setup.bash` | Load the core ROS 2 Humble environment |
| `source /home/ubuntu/ros2_ws/install/setup.bash` | Load the robot-specific packages (motor controller, sensor drivers, etc.) |
| `python3 /tmp/SCRIPT_NAME.py` | Run your Python script |

Both `source` lines must be run every time — they set up the environment variables and Python paths that ROS 2 needs. Without them, Python cannot find the ROS 2 libraries.

---

### Script 1 — Moving the Robot (`robot_move.py`)

```python
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
        pub.publish(Twist())   # stop
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
```

**Line-by-line explanation:**

| Code | What it does |
|------|-------------|
| `rclpy.init()` | Starts the ROS 2 Python library |
| `Node('robot_mover')` | Creates a new ROS 2 node named `robot_mover`. Every participant in ROS 2 is a node. |
| `create_publisher(Twist, '/cmd_vel', 10)` | Tells ROS 2 that this node will send `Twist` messages on the `/cmd_vel` topic. The `10` is the queue size. |
| `time.sleep(1.0)` | Waits for the publisher to finish connecting to the topic |
| `Twist()` | Creates a velocity message. `linear.x` = forward/backward speed (m/s), `linear.y` = sideways speed (mecanum only), `angular.z` = rotation speed (rad/s) |
| `pub.publish(msg)` | Sends the message. The motor controller receives it and drives the wheels. |
| `pub.publish(Twist())` | Sends an all-zero message — this stops the robot |
| `node.destroy_node()` / `rclpy.shutdown()` | Cleanly shuts down the ROS 2 node |

**Understanding the Twist message:**

A `Twist` message describes motion in 3D space using two vectors:

- **`linear`** — straight-line velocity along each axis (metres per second)
  - `linear.x` — forward (+) or backward (−)
  - `linear.y` — strafe left (+) or right (−) *(mecanum only)*
  - `linear.z` — up/down (not used on ground robots)
- **`angular`** — rotational velocity around each axis (radians per second)
  - `angular.z` — spin left (+) or right (−) *(yaw — the one we use)*
  - `angular.x` / `angular.y` — roll/pitch (not used on ground robots)

Think of it like a joystick: `linear.x` is the forward/back axis, `linear.y` is the left/right strafe axis, and `angular.z` is the twist/rotation.

**Why `linear.y` works for strafing:** The TurboPi has **mecanum wheels** — each wheel has small diagonal rollers. By spinning wheels in different combinations, the robot can move sideways without turning. This is unique to mecanum platforms; a standard 4-wheel robot cannot strafe.

**Optional Exercise:** Modify the script to make the robot drive in a square (forward, turn 90°, repeat 4 times).

The key is figuring out how long to run the turn. `angular.z` is in radians per second, and a 90° turn is π/2 radians. So if you spin at 2.0 rad/s, the time needed is:

```
time = angle / speed = (π/2) / 2.0 ≈ 0.785 seconds
```

This is the same relationship as `distance = speed × time`, just applied to rotation instead of translation.

---

### Script 2 — Taking a Photo (`robot_snapshot.py`)

```python
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
        enc = msg.encoding.lower()
        data = np.frombuffer(msg.data, dtype=np.uint8)
        if enc in ('yuv422_yuy2', 'yuyv', 'yuv422'):
            img = data.reshape((msg.height, msg.width, 2))
            img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUY2)
        elif enc in ('rgb8',):
            img = data.reshape((msg.height, msg.width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif enc in ('bgr8',):
            img = data.reshape((msg.height, msg.width, 3))
        cv2.imwrite(OUTPUT, img)
        print(f"Saved {msg.width}x{msg.height} -> {OUTPUT}")
        self.saved = True

def main():
    rclpy.init()
    node = SnapshotNode()
    print("Waiting for image on /image_raw...")
    deadline = time.time() + 10.0
    while not node.saved and time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    import time
    main()
```

**Key concepts:**

| Code | What it does |
|------|-------------|
| `create_subscription(Image, '/image_raw', self.callback, 10)` | Subscribes to the camera topic. Every time a frame arrives, `callback` is called automatically. |
| `np.frombuffer(msg.data, dtype=np.uint8)` | The image arrives as raw bytes. This converts it into a NumPy array. |
| `data.reshape((msg.height, msg.width, 2))` | Reshapes the flat byte array into a 2D grid of pixels. YUV422 stores 2 bytes per pixel. |
| `cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUY2)` | Converts the YUV colour format to BGR (the format OpenCV uses for saving). |
| `cv2.imwrite(OUTPUT, img)` | Saves the image to disk as a JPEG. |
| `rclpy.spin_once(node, timeout_sec=0.1)` | Processes any incoming ROS 2 messages for up to 0.1 seconds, then returns. We loop this until the image is saved. |

**What is YUV422?** Cameras often store colour more efficiently by sharing colour information between adjacent pixels. YUV422 stores full brightness (Y) for every pixel but shares colour (U, V) between pairs. OpenCV's `cvtColor` handles the conversion automatically.

**To retrieve the photo to your laptop**, first copy it out of the container to the robot's filesystem (in your PuTTY terminal):
```bash
docker cp turbopi:/tmp/snapshot.jpg /tmp/snapshot.jpg
```
Then use PSCP in a Windows Command Prompt to download it to your laptop:
```cmd
pscp pi@192.168.X.X:/tmp/snapshot.jpg C:\Users\YourName\Desktop\snapshot.jpg
```

---

### Script 3 — Controlling the Camera Servos (`robot_servo.py`)

The camera is mounted on a pan/tilt head driven by two PWM servos. Servo positions are set by sending pulse widths in microseconds:

- **~1000** — one extreme (far right / full up)
- **~1500** — center
- **~2000** — other extreme (far left / full down)

The servo IDs on this robot are:
- **Servo 2** — pan (left/right, horizontal)
- **Servo 1** — tilt (up/down, vertical)

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ros_robot_controller_msgs.msg import SetPWMServoState, PWMServoState
import time

SERVO_PAN  = 2   # horizontal (left/right)
SERVO_TILT = 1   # vertical (up/down)

def main():
    rclpy.init()
    node = Node('servo_demo')
    pub = node.create_publisher(
        SetPWMServoState,
        '/ros_robot_controller/pwm_servo/set_state',
        10
    )
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

    print("Center...")        ; set_servos(1500, 1500) ; time.sleep(1.0)
    print("Pan left...")      ; set_servos(pan=2000)   ; time.sleep(1.0)
    print("Pan right...")     ; set_servos(pan=1000)   ; time.sleep(1.0)
    print("Tilt up...")       ; set_servos(pan=1500, tilt=1000) ; time.sleep(1.0)
    print("Tilt down...")     ; set_servos(pan=1500, tilt=2000) ; time.sleep(1.0)
    print("Return to center."); set_servos(1500, 1500)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key concept — custom message types:** Unlike `Twist` (a standard ROS 2 type), `SetPWMServoState` is a custom message defined by the robot manufacturer. Its structure has a `state` field containing a list of `PWMServoState` objects — one per servo. Each `PWMServoState` has:
- `id` — which servo to move (as a list)
- `position` — the target pulse width in microseconds
- `offset` — a calibration trim (leave at 0)

Each servo gets its own `PWMServoState` object; they are then bundled together in `msg.state`.

**Optional Exercise:** Combine `robot_snapshot.py` and `robot_servo.py` to write a script that pans the camera left, takes a photo, pans right, and takes another photo.

---

## Part C (Bonus): Live Sensor Data (`robot_sensors.py`)

The robot has two sensor systems this script reads simultaneously:

- **Ultrasonic (sonar) sensor** — measures distance to the nearest object in front of the robot. Publishes to the ROS 2 topic `/sonar_controller/get_distance` as an integer in **millimetres**.
- **4-channel infrared line sensor** — four IR sensors underneath the robot detect whether each sensor is over a black line (`T`) or not (`F`). This sensor is read directly via a hardware SDK library (`sdk.FourInfrared`), not through ROS 2.

```python
#!/usr/bin/env python3
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
```

Run this script, then try:
- Moving your hand toward the sonar sensor and watch the distance value decrease
- Placing the robot over a black line and watch the `T`/`F` values change across S0–S3

**Beneficial questions to explore:**
1. What value does the sonar return when there is nothing in front of it?
2. Which line sensor channel (S0–S3) is leftmost from the robot's perspective?
3. How could you use the line sensor readings to make the robot steer itself along a line?

---

## Quick Reference

### Running any script on the robot

```bash
# 1. Copy the script to the robot (run on your laptop or robot terminal)
docker cp /tmp/my_script.py turbopi:/tmp/

# 2. Run it
docker exec --user ubuntu turbopi bash -c \
  'source /opt/ros/humble/setup.bash && \
   source /home/ubuntu/ros2_ws/install/setup.bash && \
   python3 /tmp/my_script.py'
```

### Useful ROS 2 commands (run inside the container)

```bash
# List all active topics
ros2 topic list

# See what type of data a topic carries
ros2 topic info /cmd_vel

# Print live data from a topic
ros2 topic echo /sonar_controller/get_distance
```

To open a shell inside the container:
```bash
docker exec -it --user ubuntu turbopi bash
source /opt/ros/humble/setup.bash
source /home/ubuntu/ros2_ws/install/setup.bash
```

### Twist message reference

| Field | Effect | Example value |
|-------|--------|---------------|
| `linear.x` | Forward (+) / Backward (−) | `0.3` m/s |
| `linear.y` | Strafe left (+) / right (−) | `0.3` m/s |
| `angular.z` | Turn left (+) / right (−) | `2.0` rad/s |

