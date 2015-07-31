all:
	@echo possible targets ssh screen mutt vim zsh minicom psql install and install-all

install: ssh screen vim zsh
install-all: ssh screen mutt vim zsh minicom psql

ssh:
	install -d -m 0755 ${HOME}/.ssh
	install -b -m 0644 ssh_config ${HOME}/.ssh/config
	install -b -m 0644 ssh_authorized_keys ${HOME}/.ssh/authorized_keys

screen:
	install -b -m 0644 screenrc ${HOME}/.screenrc

mutt:
	install -b -m 0640 muttrc ${HOME}/.muttrc

vim:
	install -b -m 0644 vimrc ${HOME}/.vimrc

zsh:
	install -b -m 0644 zshrc ${HOME}/.zshrc
	install -b -m 0644 zprofile ${HOME}/.zprofile
	rm ${HOME}/.zcompdump* 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zshrc' 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zprofile' 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zshrc.local' 2> /dev/null || exit 0
	zsh -c 'zcompile ${HOME}/.zprofile.local' 2> /dev/null || exit 0

minicom:
	install -b -m 0644 minirc.dfl ${HOME}/.minirc.dfl

psql:
	install -b -m 0644 psqlrc ${HOME}/.psqlrc
