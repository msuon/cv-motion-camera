#! /usr/bin/env bash
install_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
systemdfile_name="cv-pi-camera.service"
systemdfile_path="$install_path/$systemdfile_name"
systemdinstall_path="/etc/systemd/system/"
echo "MOVING systemd file to install dir"
cp $systemdfile_path $systemdinstall_path
echo "Enabling systemd service"
systemctl enable $systemdfile_name 
