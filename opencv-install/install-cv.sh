#! /usr/bin/env bash
install_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cv_lib_path="$install_path/cv2.cpython-35m-arm-linux-gnueabihf.so"
dependencies_tar_path="$install_path/dependencies.tar.gz"
echo "COPYING $cv_lib_path to /usr/local/lib/python3.5/dist-packages/"
cp $cv_lib_path /usr/local/lib/python3.5/dist-packages/ 
echo "EXTRACTING DEPENDENCIES from $dependencies_tar_path to /usr/local/lib/"
tar -xzvf $dependencies_tar_path -C "/usr/local/lib/"
