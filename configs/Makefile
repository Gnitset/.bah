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
	defaults -currentHost write com.apple.Safari DidPromptSearchEngineAlert -bool true
	defaults -currentHost write com.apple.controlcenter BatteryShowPercentage -bool true
	defaults -currentHost write com.apple.screensaver showClock -bool true
	defaults -currentHost write com.apple.universalcontrol HasShownControlNotification -bool true
	defaults delete com.apple.Spotlight "NSStatusItem Visible Item-0" || true
	defaults delete com.apple.dock wvous-br-corner || true
	defaults delete com.apple.tipsd TPSWaitingToShowWelcomeNotification || true
	defaults write "Apple Global Domain" AppleShowAllExtensions -bool true
	defaults write "Apple Global Domain" InitialKeyRepeat -int 15
	defaults write "Apple Global Domain" KeyRepeat -int 2
	defaults write "Apple Global Domain" WebKitDeveloperExtras -bool true
	defaults write "Apple Global Domain" com.apple.swipescrolldirection -bool false
	defaults write com.apple.AppleMultitouchTrackpad HIDScrollZoomModifierMask -int 262144
	defaults write com.apple.AppleMultitouchTrackpad TrackpadFiveFingerPinchGesture -int 0
	defaults write com.apple.AppleMultitouchTrackpad TrackpadFourFingerPinchGesture -int 0
	defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerHorizSwipeGesture -int 1
	defaults write com.apple.AppleMultitouchTrackpad TrackpadTwoFingerFromRightEdgeSwipeGesture -int 0
	defaults write com.apple.DiskUtility DUShowEveryPartition -bool true
	defaults write com.apple.ImageCapture disableHotPlug -bool true
	defaults write com.apple.Safari AlwaysShowTabBar -bool true
	defaults write com.apple.Safari AutoOpenSafeDownloads -bool false
	defaults write com.apple.Safari Command1Through9SwitchesTabs -bool false
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
	defaults write com.apple.Safari.SandboxBroker ShowDevelopMenu -bool true
	defaults write com.apple.Terminal "Default Window Settings" Pro
	defaults write com.apple.Terminal "Startup Window Settings" Pro
	defaults write com.apple.Terminal Command1Through9SwitchesTabs -bool false
	defaults write com.apple.Terminal NSUserKeyEquivalents -dict ett '@$$n'
	defaults write com.apple.TextEdit RichText -bool false
	defaults write com.apple.TimeMachine DoNotOfferNewDisksForBackup -bool true
	defaults write com.apple.WindowManager EnableStandardClickToShowDesktop -bool false
	defaults write com.apple.WindowManager EnableTilingByEdgeDrag -bool false
	defaults write com.apple.WindowManager EnableTilingOptionAccelerator -bool false
	defaults write com.apple.WindowManager EnableTopTilingByEdgeDrag -bool false
	defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
	defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true
	defaults write com.apple.dock mru-spaces -bool false
	defaults write com.apple.dock orientation -string right
	defaults write com.apple.dock tilesize -int 50
	defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad HIDScrollZoomModifierMask -int 262144
	defaults write com.apple.finder DesktopViewSettings '{IconViewSettings={arrangeBy=kind;};}'
	defaults write com.apple.finder FXDefaultSearchScope -string SCcf
	defaults write com.apple.finder FXEnableExtensionChangeWarning -bool false
	defaults write com.apple.finder FXPreferredViewStyle -string clmv
	defaults write com.apple.finder FavoriteTagNames -array ""
	defaults write com.apple.finder FinderSpawnTab -bool false
	defaults write com.apple.finder NewWindowTarget -string PfHm
	defaults write com.apple.finder NewWindowTargetPath -string "file://${HOME}/"
	defaults write com.apple.finder QLEnableTextSelection -bool true
	defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool false
	defaults write com.apple.finder ShowHardDrivesOnDesktop -bool false
	defaults write com.apple.finder ShowMountedServersOnDesktop -bool false
	defaults write com.apple.finder ShowRecentTags -bool false
	defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool false
	defaults write com.apple.finder ShowStatusBar -bool true
	defaults write com.apple.finder SidebarDevicesSectionDisclosedState -bool true
	defaults write com.apple.menuextra.clock ShowSeconds -bool true
	defaults write com.apple.universalaccess closeViewPanningMode -int 0
	defaults write com.apple.universalaccess closeViewScrollWheelModifiersInt -int 262144
	defaults write com.apple.universalaccess closeViewScrollWheelToggle -bool true
	defaults write com.apple.universalaccess closeViewScrollWheelToggle -bool true
	defaults write com.apple.widgets ShowAddSheetOnboardingBanner -bool false
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 27 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>60</integer><integer>50</integer><integer>1048576</integer></array></dict></dict>"
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 118 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>65535</integer><integer>18</integer><integer>262144</integer></array></dict></dict>"
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 119 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>65535</integer><integer>19</integer><integer>262144</integer></array></dict></dict>"
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 120 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>65535</integer><integer>20</integer><integer>262144</integer></array></dict></dict>"
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 121 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>65535</integer><integer>21</integer><integer>262144</integer></array></dict></dict>"
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 122 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>65535</integer><integer>23</integer><integer>262144</integer></array></dict></dict>"
	defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 123 "<dict><key>enabled</key><integer>1</integer><key>value</key><dict><key>type</key><string>standard</string><key>parameters</key><array><integer>65535</integer><integer>22</integer><integer>262144</integer></array></dict></dict>"
	defaults write com.apple.iCal CalendarSidebarShown -bool true
	defaults write com.apple.iCal "Show Week Numbers" -bool true
	defaults write com.mizage.Divvy SuppressImportDialog -bool true
	defaults write com.mizage.Divvy defaultColumnCount -int 10
	defaults write com.mizage.Divvy defaultRowCount -int 10
	defaults write com.mizage.Divvy defaultScreenMarginBottom -int 0
	defaults write com.mizage.Divvy defaultScreenMarginLeft -int 0
	defaults write com.mizage.Divvy defaultScreenMarginRight -int 0
	defaults write com.mizage.Divvy defaultScreenMarginTop -int 0
	defaults write com.mizage.Divvy enableMargins -bool true
	defaults write com.mizage.Divvy globalHotkey -dict keyCode 50 modifiers 2048
	defaults write com.mizage.Divvy showMenuIcon -bool false
	defaults write com.mizage.Divvy useDefaultGrid -bool true
	defaults write com.mizage.Divvy useGlobalHotkey -bool true
	#sudo defaults write /.Spotlight-V100/VolumeConfiguration Exclusions -array /Volumes

macos_dock:
#	defaults read com.apple.dock persistent-apps | grep -q Discord.app || defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Discord.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
#	defaults read com.apple.dock persistent-apps | grep -q Slack.app || defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Slack.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
	defaults write com.apple.dock persistent-apps -array ''
	defaults write com.apple.dock persistent-others -array ''
	defaults write com.apple.dock recent-apps -array ''
	for app in \
		/System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app \
		/System/Applications/Messages.app \
		/System/Applications/Mail.app \
		/System/Applications/Calendar.app \
		/System/Applications/Utilities/Terminal.app \
		/System/Applications/Photos.app \
		/Applications/Slack.app \
		/Applications/Discord.app \
		/Applications/Firefox.app \
		/Applications/Spotify.app \
		/System/Applications/FindMy.app \
	; do \
		defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>$${app}</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>" \
	; done
	killall Dock

macos_sudo:
	sed -ie 's/^#.*$$/&\nauth sufficient pam_tid.so/' /etc/pam.d/sudo

macos_mas:
	mas install \
		413857545  `# Divvy` \
		409183694  `# Keynote` \
		1558453954 `# Keyword Search` \
		430255202  `# Mactracker` \
		409203825  `# Numbers` \
		409201541  `# Pages` \
		6463635304 `# Refunder` \
		409907375  `# Remote Desktop` \
		877615577  `# Serial` \
		803453959  `# Slack` \
		728530824  `# SubEthaEdit` \
		1436522307 `# Transmit` \
		1295203466 `# Windows App` \
		1451685025 `# WireGuard` \
		1497506650 `# Yubico Authenticator` \


brew: brew_cask brew_formulae

brew_cask:
	brew install \
		homebrew/cask/arduino-ide \
		homebrew/cask/audacity \
		homebrew/cask/autodesk-fusion \
		homebrew/cask/bzflag \
		homebrew/cask/discord \
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
		homebrew/cask/wireshark-app \
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
		mas \
		mkvtoolnix \
		mpv \
		mtr \
		ngrep \
		nmap \
		openssh \
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
		yt-dlp \
		yubico-piv-tool \
	--formulae
