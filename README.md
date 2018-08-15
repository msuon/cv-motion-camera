## Introduction 
This project was a response to my bike being stolen from my front door twice, only one year apart. It is not quite done, however with some configuration and setup it should work quite well to capture anyone who is walking past it.  

## Prerequisite 
- RspberryPi (I have tried both the Zero W and 3, both works really well) 
- Raspbian Stretch (Lite version is better) 
- RaspberryPi Camera 

## Installation 
Please note that the setup script isn't yet well fleshed out. No error checking, and it isn't very flexible in terms of possible mirror change of dependencies to be installed. But you should be able to see the list of dependencies of the project and install them manually if the script fails.  
- Run the setup.sh script in the root directory as sudo on the raspberry pi 

## Debugging 
- Tail the logs/gdrive.log file to see the current output of the program. 

## Side note
- This program runs under systemctl, any extensive error logging will be done in journalctl for the cv-pi-camera.service unit.
