all:
	@echo possible targets config_ssh config_screen config_mutt config_vim config_zsh and install_all

install_all: config_ssh config_screen config_mutt config_vim config_zsh

config_ssh:
	install -d -m 0755 ${HOME}/.ssh
	install -b -m 0644 ssh_config ${HOME}/.ssh/config
	install -b -m 0644 ssh_authorized_keys ${HOME}/.ssh/authorized_keys

config_screen:
	install -b -m 0644 screenrc ${HOME}/.screenrc

config_mutt:
	install -b -m 0640 muttrc ${HOME}/.muttrc

config_vim:
	install -b -m 0644 vimrc ${HOME}/.vimrc

config_zsh:
	install -b -m 0644 zshrc ${HOME}/.zshrc
	install -b -m 0644 zprofile ${HOME}/.zprofile
	rm ${HOME}/.zcompdump* 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zshrc' 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zprofile' 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zshrc.local' 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zprofile.local' 2> /dev/null || exit 0
