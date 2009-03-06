#! /bin/sh

mkdir /backup

cat >> /etc/rsyncd.conf << EOF

[backup]
	path = /backup
	hosts allow = maijna.ladan.se
	auth users = backup
	secrets file = /etc/rsyncd.secrets
	uid = 0
	gid = 0
EOF

cat >> /etc/rsyncd.secrets << EOF
backup:ChangeMe
EOF

chmod 0600 /etc/rsyncd.secrets

/etc/init.d/rsyncd start
rc-update add rsyncd default

#mkdir /backup/www
#/www			/backup/www		none	bind,ro			0 0
#mount --bind /www /backup/www
