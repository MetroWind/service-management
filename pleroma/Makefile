.PHONY: setup config

setup:
	gpg --output config.exs -d --yes config.exs.pgp
	ansible-playbook --ask-become-pass --ask-pass -i ~/programs/service-management/hosts.ini setup.yaml
	rm -vf config.exs

config:
	gpg --output config.exs -d --yes config.exs.pgp
	ansible-playbook --ask-become-pass --ask-pass -i ~/programs/service-management/hosts.ini copy-config.yaml
	rm -vf config.exs

config.exs.pgp: config.exs
	gpg --armor -o config.exs.pgp --symmetric --yes config.exs
