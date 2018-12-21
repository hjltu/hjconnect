#!/bin/bash

# 19-nov-18 start
# installing hjconnect service

# check sudo

ME=`whoami`

if [[ $ME != root ]] ; then
	echo run it with sudo
	exit 1
fi

# check installed supervisor and pano-mqtt

if [[ $1 != -y ]] ; then
	echo Installing hjconnect service
	read -p 'supervisor and paho-mqtt is installed? y/n :' ANS

	if [[ $ANS != y ]] ; then
		exit 1
	fi
fi

# file gen

echo generate conf files

gen_conf_file(){
cat > $1.conf << EOF
# apt install supervisor
# /etc/supervisor/conf.d/hjconnect.conf
# supervisorctl reread
# supervisorctl update
# service supervisor restart

[program:$1.py]
environment=PYTHONPATH="/home/$SUDO_USER:$PYTHONPATH",HOME="/home/$SUDO_USER",TERM="xterm"
directory=$PWD
user=$SUDO_USER
command=/usr/bin/python3 -u $PWD/$1.py
autostart=true
autorestart=true
stderr_logfile=/var/log/$1.err.log
stdout_logfile=/var/log/$1.out.log

stdout_logfile_maxbytes=10MB
stderr_logfile_maxbytes=10MB
stdout_logfile_backups=1
stderr_logfile_backups=1
EOF

chmod +x $1.py
chmod +x $1.conf
mv $1.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
service supervisor restart
}

gen_conf_file hjconnect

echo end

