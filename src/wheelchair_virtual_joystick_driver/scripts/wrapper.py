#!/usr/bin/env python

__author__      = "Lewis Christopher Brand"
__copyright__ = "Copyright 2022, The University of Nottingham"
__credits__ = ["Lewis Christopher Brand", "Ayse Kucukyilmaz", "Simon Green"]

__license__ = "ECL-2.0"
__version__ = "0.3.0"
__maintainer__ = "Lewis Christopher Brand"
__email__ = "lewisbrand.56@gmail.com"
__status__ = "Development"

"""
	Copyright 2022 University of Nottingham Licensed under the
	Educational Community License, Version 2.0 (the "License"); you may
	not use this file except in compliance with the License. You may
	obtain a copy of the License at
	
	http://www.osedu.org/licenses/ECL-2.0
	Unless required by applicable law or agreed to in writing,
	software distributed under the License is distributed on an "AS IS"
	BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
	or implied. See the License for the specific language governing
	permissions and limitations under the License.
"""

from threading import Lock

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Header

from driver import Joystick


class Wheelchair_virtual_joystick_driver:
    def __init__(self):
        self.joystick = Joystick()
        self.last_message = rospy.Time.now()

        calib_fb = -1
        calib_lr = -1

        try:
            if rospy.has_param('/wheelchair_calibrate_fb'):
                calib_fb = rospy.get_param('/wheelchair_calibrate_fb')

            if rospy.has_param('/wheelchair_calibrate_lr'):
                calib_lr = rospy.get_param('/wheelchair_calibrate_lr')
        except KeyError:
            calib_fb = -1
            calib_lr = -1

        if (calib_fb == -1 or calib_lr == -1):
            rospy.loginfo("No calibration values provided. Running calibration now...")
            self.joystick.calibrate()
            
        else:
            self.joystick.set_calibration_values(calib_fb, calib_lr)
        rospy.loginfo("Calibration complete")
        
        self.stop_motion()

        rospy.Subscriber('/cmd_vel', Twist, self.on_twist)
        self.joy_pub = rospy.Publisher('/joy', Joy, queue_size=10)

    def stop(self):
        """Called when wrapper is stopping.
        """
        self.stop_motion()

    def stop_motion(self):
        """Called to stop all motor motion.
        Will set virtual joystick to 0,0 to stop the motors.
        """
        self.joystick.set_percent(0,0)

    def on_twist(self, msg):
        """Callback for the ROS twist subscriber.

        Args:
            msg (geometry_msgs/Twist): ROS Twist message.
        """
        scale = 10
        x = (msg.linear.x) * scale
        z = (msg.angular.z) * scale

        if (x > 100):
            rospy.loginfo("Trimming x to 100")
            x = 100
        if (x < -100):
            rospy.loginfo("Trimming x to -100")
            x = -100
        if (z > 100):
            rospy.loginfo("Trimming z to 100")
            z = 100
        if (z < -100):
            rospy.loginfo("Trimming z to -100")
            z = -100

        rospy.loginfo("X = {}, Z = {}".format(x, z))
        self.last_message = rospy.Time.now()
        self.joystick.set_percent(x,z)

    def get_last_message(self):
        """Gets the timestamp of the last message recieved.

        Returns:
            rospy.Time: The time of the last received message as a rospy.Time instance.
        """
        return self.last_message

    def publish_joy(self):
        rate = rospy.Rate(10) # 10hz

        while not rospy.is_shutdown():
            x, z = self.joystick.get_percent()
            h = Header()
            h.stamp = rospy.Time.now()
            
            joy = Joy()
            joy.header = h
            joy.axes = [x,z]
            joy.buttons = []

            self.joy_pub.publish(joy)
            rate.sleep()


class Watchdog:
    """Monitors the received messages and sends a stop command if a specific amount of time (the timeout) has past after the last message.
    Designed to prevent runaways.
    """
    def __init__(self, wrapper, timeout=2):
        """Initialises the watchdog

        Args:
            wrapper (Wheelchair_virtual_joystick_driver): The Wheelchair virtual joystick driver wrapper to check.
            timeout (int, optional): The number of seconds to set the watchdog motor timeout to. Defaults to 2.
        """
        self.wrapper = wrapper
        self._lock = Lock()

        self.timeout = timeout

        self.timer = rospy.Timer(rospy.Duration(0.1), self.compare_time, oneshot=False)

    def __del__(self):
        """Destructor.
        """
        self.timer.shutdown()

    def compare_time(self, timerEvent):
        """Compares the current time and the time of the last message. 
        If this is greater than 1 second or no time has been sent yet then a stop is sent.
        """
        if isinstance(timerEvent.last_duration, int):
            if timerEvent.last_duration > self.timeout:
                self.wrapper.stop_motion()
                raise RuntimeError("Watchdog processing time is larger than timeout. Please reduce ROS operations or increase timeout.")

        with self._lock: 
            now = rospy.Time.now()
            last_message = self.wrapper.get_last_message()
            duration = now - last_message

            if (now == 0) or (duration.to_sec() > self.timeout):
                self.wrapper.stop_motion()


if __name__ == "__main__":
    rospy.init_node("wheelchair_virtual_joystick_driver")

    wrapper = Wheelchair_virtual_joystick_driver()
    watchdog = Watchdog(wrapper)
    rospy.on_shutdown(wrapper.stop)

    rospy.loginfo("Joystick driver running. Controller can be turned on")

    try:
        wrapper.publish_joy()
    except rospy.ROSInterruptException:
        pass

    rospy.spin()
