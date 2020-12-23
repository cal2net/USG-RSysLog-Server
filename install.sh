#! /bin/bash


while getopts "d:h:" flag;
do
    case $flag in
      d) dirname=${OPTARG};;
      h) help=${OPTARG};;
    esac
done

if [ -z "$help" ];
then
  echo "starting..."
else
  echo "To install please provid the following"
  echo "  -d <directory to install files>"
  exit
fi


if [ -z "$dirname" ];
then
  echo "Need the directory you want to install the code"
  echo "Use -h option for installation parameters"
  exit
else
  echo "Installing to $dirname"
fi


echo "Have the parameters invoking installation scripts"


python3 install.py $dirname
python3 -m venv "$dirname/src/env"
source "$dirname/src/env/bin/activate"
pip3 install -r "$dirname/requirements.txt"
deactivate
chmod +x "$dirname/usg-rsyslog.sh"

os=${OSTYPE//[0-9.-]*/}

case "$os" in
  darwin)
    echo "I'm a Mac"
    ;;

  linux)
    echo "I'm Linux"
    sudo cp "$dirname/usg-rsyslog.service" "/etc/systemd/system/"
    sudo systemctl enable usg-rsyslog
    sudo systemctl start usg-rsyslog
    echo "R-Syslog Service shoule be started now"
    ;;
  *)

  echo "Unknown Operating system $OSTYPE"

esac
