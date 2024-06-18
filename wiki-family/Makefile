.PHONY: setup config

setup:
	gpg --output LocalSettings.php -d --yes LocalSettings.php.pgp
	ansible-playbook --ask-become-pass -i ~/programs/service-management/hosts.ini setup.yaml
	rm -vf LocalSettings.php

config:
	gpg --output LocalSettings.php -d --yes LocalSettings.php.pgp
	ansible-playbook --ask-become-pass -i ~/programs/service-management/hosts.ini update-config.yaml
	rm -vf LocalSettings.php

LocalSettings.php.pgp: LocalSettings.php
	gpg --armor -o LocalSettings.php.pgp --symmetric --yes LocalSettings.php
