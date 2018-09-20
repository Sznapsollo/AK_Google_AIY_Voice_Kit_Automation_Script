# script to pair Google AIY Voice Kit with Home Automation Solution

## About

This repository contains Python script for your Google AIY Voice Kit that will plug and play pair it with <a href="https://github.com/Sznapsollo/AKHomeAutomation" target="_blank">AKHomeAUtomation</a> solution present on my other github. However with some changes I am sure it can be used also with other home automation solutions. Take a look below and maybe it will suit you.

Script itself is basically copy of **assistant_library_with_local_commands_demo.py** which is provided in Google AIY Voice Kit and is present by default in /home/pi/AIY-projects-python/src/examples/voice directory.

This script contains the following changes that make it work with AKHomeAutomation (and perhaps other) home automation solution.

- it introduces **getDevicesData** method which is called at the beginnning of script operation. This method contacts home automation server service to receive list of devices (in json format) that would be used by Google Voice Kit. What is crutial is "hotword" property per items that we want to be recognizable by Google Voice Kit.
- it introduces **checkItem** method which is called when Voice Kit analyzes what user said. If command ends with "on" or "off" this method tries to map rest of the sentence with one of items "hotword". If it succeeds, the script would send url to home automation system with proper values to enable/disable proper device.

## Deployment

- If you wish to use this script with <a href="https://github.com/Sznapsollo/AKHomeAutomation" target="_blank">AKHomeAUtomation</a> all you need to do is change _remoteUrl variable with proper server address.
- If you wish to integrate it with other systrems you probably need to change the way how you obtain json list of devices and how you send on/of signal to your automation solution.

## Links

- **<a href="https://youtu.be/tIaoWla-Ykk" target="_blank">Video describing script and integration with AKHomeAutomation</a>**
- **<a href="https://www.youtube.com/watch?v=C19ARWDYR3c&list=PLjd2MVjW6mhFygrvXyVcdNoq6pHK8MdUW" target="_blank">AKHomeAUtomation Youtube playlist</a>**

Take care!
Wanna touch base? office@webproject.waw.pl
