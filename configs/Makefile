config_ssh:
	install -d -m 0755 ~/.ssh
	install -bC -m 0644 ssh_config ~/.ssh/config
	install -bC -m 0644 ssh_authorized_keys ~/.ssh/authorized_keys

config_screen:
	install -bC -m 0644 screenrc ~/.screenrc

config_mutt:
	install -bC -m 0640 muttrc ~/.muttrc

config_vim:
	install -bC -m 0644 vimrc ~/.vimrc

config_zsh:
	install -bC -m 0644 zshrc ~/.zshrc
	install -bC -m 0644 zprofile ~/.zprofile
	rm ~/.zcompdump* 2> /dev/null || exit 0
#	zsh -c 'autoload zrecompile; zrecompile .zshrc'
#	zsh -c 'autoload zrecompile; zrecompile .zprofile'
#	zsh -c 'autoload zrecompile; zrecompile .zshrc.local'
#	zsh -c 'autoload zrecompile; zrecompile .zprofile.local'
