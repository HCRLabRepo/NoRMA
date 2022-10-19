# The NoRMA (Nottingham Robotic Mobility Assistant) platform

## Introduction
The NoRMA (Nottingham Robotic Mobility Assistant) platform is a solution to the high skill and high price barrier for assistive robotics research. NoRMA allows researchers, and users with soldering and basic programming skills, the ability to convert an off-the-shelf powered wheelchair into a ROS compatible research platform at a significantly reduced cost compared to autonomous wheelchairs. The NoRMA platform is ideal for further research into control mechanisms and algorithms for smart wheelchairs and the affordability of the platform allows for the creation of multiple research systems for the price of a single commercial one. 

## Overview
This repo contains several different files and packages which each have a different purpose, specifically a ROS package and a collection of documentation to help explain the hardware configurations and the motivations for NoRMA.

The ROS package contains a hardware driver that interfaces between NoRMA and ROS using the `/joy` topic to publish the GC2 joystick position, and the `/cmd_vel` topic that the driver subscribes to in order to move NoRMA. The package also contains a web interface that publishes to the `/cmd_vel` topic to allow for teleoperational control of NoRMA. The package is formed of two files: `driver.py` which interfaces directly with the ADC and DAC to control the wheelchair, and `wrapper.py` which acts as a ROS interface.

This repo also contains the documentation on how to complete the hardware modifications in the `modification guide.pdf`.

## A note on hardware
A DIY guide is provided for the easy conversion of a powered wheelchair that is able to run this software. The guide discusses the modification of a powered wheelchair that uses the Penny and Giles GC2 Joystick Controller. Any wheelchair that uses this joystick will be compatible with this software. 

NoRMA is designed around easy to acquire, cheap, off-the-shelf components and uses the [Adafruit MCP4728 Quad DAC](https://www.adafruit.com/product/4470) and the [Adafruit ADS1015 12-Bit ADC](https://www.adafruit.com/product/1083). This software is written specifically for this hardware but can be adapted if an alternative ADC and DAC is used.


# Referencing
If you are using any of the code or documentation, please include a reference to the paper that presents this work, found [here]().

>  ⚠️ **_NOTE:_**  The proceedings containing this paper have not been published yet. This page will be updated to contain a link to it. 

L. C. Brand, A. Kucukyilmaz, "Nottingham Robotic Mobility Assistant (NoRMA): An Affordable DIY Robotic Wheelchair Platform," in *UKRAS22 Conference: Robotics for Unconstrained Environments Proceedings*, Aberystwyth 2022.


# Installation
## Compatibility
This software has been tested and verified as working on a Raspberry Pi 3B+ running Ubuntu Server 20.04.5 LTS with [ROS Noetic](http://wiki.ros.org/noetic). It is also known to run correctly on Raspbian Buster, however difficulties were faced with installing ROS on this operating system.

## Requirements
### Software
To use this software, the following additional software must also be installed:

- ROS Noetic
- Python 3
- pip3

This software uses ROS to send and receive commands using ROS topics. ROS Noetic is the officially supported version of ROS.
The driver code is written in Python and requires Python 3 to run correctly.
pip3 is used in the installation of the hardware interface libraries for the driver.
 
### Libraries

The following libraries are required for the driver to operate correctly:

- adafruit-circuitpython-mcp4728
- adafruit-circuitpython-ads1x15

The library packages can be installed by running the following commands:

`sudo pip3 install adafruit-circuitpython-mcp4728`

`sudo pip3 install adafruit-circuitpython-ads1x15`


# How to use it
The repo should be copied into your ROS workspace for it to work.

Navigate to your workspace and run the following command:

`git pull https://github.com/lew101/NoRMA.git`

This will pull the package files into your workspace.

To start the driver with the web interface, run the following command in your ROS workspace:

`roslaunch wheelchair_virtual_joystick_driver norma.launch`

The web interface will be accessible on port 8000.

## Driver calibration
The GC2 joystick controller that NoRMA interfaces uses a hall effect joystick module for signaling. The joystick works by using a fixed reference voltage, known as a center tap, as a 'center' position and then increasing or decreasing the voltage around this to move the wheelchair. In the eight wire implementation that NoRMA uses, this center tap reference voltage is unknown and so is electrically determined using a calibration phase.

For calibration, the joystick should be positioned at the center position. The joystick is then polled repeatedly over a short period of time to find the average center voltage. This is then used as the reference voltage for NoRMA.

As standard, the driver runs a short calibration phase when being launched. This phase can be skipped by providing two calibration values `/wheelchair_calibrate_fb` and `/wheelchair_calibrate_lr` on launch. These values will then be used instead.

## Driver watchdog
The normal operation of the Adafruit MCP4728 DAC is to set a voltage via software which is then maintained by the DAC until a reboot, or a new value is set. This is problematic in robotics as a lack of movement commands would normally be interpreted as no motion is required, however, because of this behavior from the DAC, the result would be continuous motion by the robot.

To prevent this, and the resultant "how to stop your runaway wheelchair" problem, a watchdog is implemented in the ROS wrapper. This monitors the received messages and will stop movement is a timeout has been exceeded. This defaults to 2 seconds.

The watchdog uses the rospy Timer library and so is threadsafe.

## Deviation lockout
The GC2 uses a pair of sensors per axis rather than one per axis to detect the location of the joystick. This ensures that if one of the sensors fails, it it detectable. To do this, there is a small difference between the two sensors. If the difference gets too large, the GC2 locks out and brings the wheelchair to a halt. 

The NoRMA hardware bypasses this protection and so it is implemented at a driver level. There is a regular check on the difference between the two sensors per axis, and if the difference is too great, it will force the GC2 to lockout.

>  ⚠️ **_NOTE:_**  Currently this is not reported in the software but an exception could be added.

# Known Bugs
## UI Caching
At present, if the web GUI page is cached, the virtual joystick (aka the nipple) will disappear from the page. The current workaround is to force refresh the page which will make the virtual joystick reappear.

## UNIX formatting
The early repo contributions were written with DOS formatting rather than Unix formatting. Most scripts have been corrected but git has not recognised the formatting change on some. This may result in python errors when attempting to run `driver.py` or `wrapper.py`. 

The current workaround is to run DOS2UNIX on these files and make them executable.

# Contributing
Pull requests are welcome but may not be looked at quickly. For major changes or bugs, please open an issue first to discuss what you would like to change.

Any unit tests that simulate I2C connectivity would be _very_ welcome.

# Authors and acknowledgement

- Lewis Brand - lewisbrand.56@gmail.com
- Simon Green - simon.castle-green2@nottingham.ac.uk
- Ayse Kucukyilmaz - Ayse.Kucukyilmaz@nottingham.ac.uk

## License
[ECL-2.0](https://opensource.org/licenses/ECL-2.0)

