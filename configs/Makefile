all:
	@echo possible targets ssh screen mutt vim zsh psql install and install-all

install: ssh screen vim zsh psql
install-all: ssh screen mutt vim zsh psql

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

psql:
	install -b -m 0644 psqlrc ${HOME}/.psqlrc

macos:
	defaults -currentHost write com.apple.screensaver showClock 1
	defaults -currentHost write com.apple.Safari DidPromptSearchEngineAlert 1
	defaults -currentHost write com.apple.universalcontrol HasShownControlNotification 1
	defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
	defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true
	defaults write com.apple.Safari Command1Through9SwitchesTabs -bool false
	defaults write com.apple.Safari AlwaysShowTabBar -bool true
	defaults write com.apple.Safari AutoOpenSafeDownloads -bool false
	defaults write com.apple.Safari DownloadsClearingPolicy -int 0
	defaults write com.apple.Safari EnableNarrowTabs -bool false
	defaults write com.apple.Safari FindOnPageMatchesWordStartsOnly -bool false
	defaults write com.apple.Safari IncludeDevelopMenu -bool true
	defaults write com.apple.Safari SafariGeolocationPermissionPolicy -int 2
	defaults write com.apple.Safari SendDoNotTrackHTTPHeader -bool true
	defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true
	defaults write com.apple.Safari ShowOverlayStatusBar -bool true
	defaults write com.apple.Safari ShowStandaloneTabBar -bool true
	defaults write com.apple.Safari WebKitDeveloperExtrasEnabledPreferenceKey -bool true
	defaults write com.apple.dock mru-spaces -bool false
	defaults write com.apple.dock orientation right
	defaults write com.apple.dock tilesize -int 50
	defaults delete com.apple.dock wvous-br-corner
	defaults write com.apple.finder DesktopViewSettings '{IconViewSettings={arrangeBy=kind;};}'
	defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"
	defaults write com.apple.finder FXEnableExtensionChangeWarning -bool false
	defaults write com.apple.finder FXPreferredViewStyle -string "clmv"
	defaults write com.apple.finder FavoriteTagNames -array ""
	defaults write com.apple.finder NewWindowTarget -string "PfHm"
	defaults write com.apple.finder NewWindowTargetPath -string "file://${HOME}/"
	defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool false
	defaults write com.apple.finder ShowHardDrivesOnDesktop -bool false
	defaults write com.apple.finder ShowMountedServersOnDesktop -bool false
	defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool false
	defaults write com.apple.finder ShowStatusBar -bool true
	defaults write com.mizage.Divvy SuppressImportDialog -bool true
	defaults write com.mizage.Divvy defaultColumnCount -int 10
	defaults write com.mizage.Divvy defaultRowCount -int 10
	defaults write com.mizage.Divvy useDefaultGrid -bool true
	defaults write com.mizage.Divvy globalHotkey '{keyCode=50;modifiers=2048;};'
	defaults write com.mizage.Divvy useGlobalHotkey -bool true
	defaults write com.mizage.Divvy showMenuIcon -bool false

macos_sudo:
	sed -ie 's/^#.*$$/&\nauth sufficient pam_tid.so/' /etc/pam.d/sudo

brew: brew_cask brew_formulae

brew_cask:
	brew install \
		homebrew/cask/arduino-ide \
		homebrew/cask/audacity \
		homebrew/cask/autodesk-fusion \
		homebrew/cask/bzflag \
		homebrew/cask/discord \
		homebrew/cask/docker \
		homebrew/cask/firefox \
		homebrew/cask/google-chrome \
		homebrew/cask/gqrx \
		homebrew/cask/karabiner-elements \
		homebrew/cask/keepassx \
		homebrew/cask/logi-options-plus \
		homebrew/cask/microsoft-teams \
		homebrew/cask/mqttx \
		homebrew/cask/prusaslicer \
		homebrew/cask/qflipper \
		homebrew/cask/rar \
		homebrew/cask/raspberry-pi-imager \
		homebrew/cask/secretive \
		homebrew/cask/spotify \
		homebrew/cask/steam \
		homebrew/cask/thonny \
		homebrew/cask/vnc-viewer \
		homebrew/cask/wireshark \
		homebrew/cask/yubico-yubikey-manager \
		--cask

brew_formulae:
	brew install \
		cmake \
		coreutils \
		parera10/csshx/csshx \
		curl \
		esptool \
		exiv2 \
		ffmpeg \
		fio \
		fping \
		git \
		gnupg \
		go \
		helm \
		iperf3 \
		jq \
		kubernetes-cli \
		lftp \
		mkvtoolnix \
		mpv \
		mtr \
		ngrep \
		nmap \
		openssh \
		packer \
		pinentry-mac \
		postgresql@16 \
		pwgen \
		pypy \
		rke \
		rrdtool \
		shadowsocks-libev \
		sipcalc \
		sqlite \
		sshpass \
		svtplay-dl \
		syncthing \
		telnet \
		terraform \
		testdisk \
		testssl \
		watch \
		ykman \
		youtube-dl \
		yt-dlp \
		yubico-piv-tool \
	--formulae
