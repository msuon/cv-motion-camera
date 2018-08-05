#! /usr/bin/env bash
echo "==========UNINSTALLING UNECCESSARY PACKAGES=========="
dpkg-query -s wolfram-engine
if [ $? = 0 ]
then
    echo "Uninstalling wolfram-engine..."
    apt-get purge wolfram-engine -y
else
    echo "wolfram-engine not installed.. skipping"
fi

dpkg-query -s libreoffice
if [ $? = 0 ]
then
    echo "Uninstalling all libreoffice..."
    apt-get purge libreoffice* -y
else
    echo "libreoffice not installed.. skipping"
fi
apt-get clean -y
apt-get autoremove -y

echo "==========INSTALLING Python3 PIP=========="
apt-get install python3-pip -y


echo "==========INSTALLING VIM=========="
dpkg-query -s vim
if [ $? = 0 ] 
then
    echo "VIM already installed.. skipping"
else
    echo "Installing VIM..."
    apt-get install vim -y
fi

echo "==========Upgrading apt-get=========="
apt-get update -y
apt-get upgrade -y 

echo "==========Installing PiCamera Module=========="
pip3 install picamera -y

echo "==========Installing GDrive API=========="
pip3 install --upgrade google-api-python-client
pip3 install oauth2client
apt-get install python3-httplib2
pip3 install oauth2client
sudo pip3 install --upgrade google-api-python-client

echo "==========Installing Image I/O Packages=========="
apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev -y

echo "==========Installing Video I/O Packages=========="
apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
apt-get install libxvidcore-dev libx264-dev -y

echo "==========Installing HighGUI dependencies=========="
apt-get install libgtk2.0-dev libgtk-3-dev -y

echo "==========Installing Math dependencies=========="
apt-get install libatlas-base-dev gfortran -y

echo "==========Installing Python Headers =========="
apt-get install python2.7-dev python3-dev -y

echo "==========Installing Numpy=========="
pip3 install numpy

echo "==========Installing Imutils=========="
pip3 install imutils

echo "OpenCV DEPENDENCIES installed! Running OpenCV Install Script..."
./opencv-install/install-cv.sh
./opencv-install/install-cv.sh

echo "==========Installing GDrive API=========="
pip3 install --upgrade google-api-python-client
pip3 install oauth2client
apt-get install python3-httplib2
pip3 install oauth2client
sudo pip3 install --upgrade google-api-python-client

echo "==========Enabling PiCamera=========="
echo "start_x=1" >> /boot/config.txt
echo "gpu_mem=128" >> /boot/config.txt

echo "==========Installing Systemd Service=========="
./systemd_file/install-systemd.sh

echo "Installation Complete! Error checking not yet implemented, so check output carefully and reboot if nothing seems wrong. After reboot kill SecurityCamera.py app and run it manually using --noauth_local_webserver option to setup GDrive"
