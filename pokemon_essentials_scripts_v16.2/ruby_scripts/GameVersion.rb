#########################################################################################
# CREDITS/CRÉDITOS:                                                                     #
# DPertierra, Iansson                                                                   #
# https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater                     #
# Version: 2.2.0                                                                        #
#########################################################################################
module VersionCheck
  W='wininet'
  SPC=Win32API.new('kernel32','SetPriorityClass','pi','i').call(-1,128)
  IOA=Win32API.new(W,'InternetOpenA','plppl','l').call('',0,'','',0)
  IC=Win32API.new(W,'InternetConnectA','lplpplll','l')
  print(ErrConIn)if IOA==0
	module Connection
		ErrConIn="Unable to connect to Internet"
		ErrConHttp="Unable to connect to the Server"
		ErrNoFile="No file to be downloaded"
		IOU=Win32API.new(W,'InternetOpenUrl','lppllp','l')
		IRF=Win32API.new(W,'InternetReadFile','lpip','l')
		ICH=Win32API.new(W,'InternetCloseHandle','l','l')
		HQI=Win32API.new(W,'HttpQueryInfo','llppp','i')
		module_function
		def validateVersion(url, update=false, from_update_button=false)
			internetOpen = Win32API.new(W,'InternetOpenA','plppl','l').call('',0,'','',0)
			open_url = IOU.call(internetOpen,url,nil,0,0x80000000,0)
			if open_url == 0
				Kernel.pbMessage(_INTL(pbGetPokeUpdaterText('NO_NEW_VERSION_OR_INTERNET')))
				return
			end

			@dls||={}
			@size||={}
			@read||={}
			buf = ''
			a=url.split('/')
			serv,root,fich=a[2],a[3..a.size].join('/'),a[-1]
			print(ErrNoFile)if fich.nil?
			txt=''
			ErrConHttp if IC.call(IOA,serv,80,'','',3,1,0)==0
			f=IOU.call(IOA,url,nil,0,0x80000000,0)
			HQI.call(f,5,k="\0"*1024,[k.size-1].pack('l'),nil)
			@read[fich],@size[fich]=0,k.delete!("\0").to_i
			loop do
				buf,n=' '*1024,0
				r=IRF.call(f,buf,1024,o=[n].pack('i!'))
				n=o.unpack('i!')[0]
				break if r&&n==0
				@read[fich]=(txt<<buf[0,n]).size
			end
			ICH.call(f)
			ICH.call(open_url)
			
			sleep(0.001)
			return if !txt || txt.empty?
			newVersion = nil
			# check that the pastebin has the GAME_VERSION value
			lines = txt.split("\n")
			for line in lines
			if line.include?("GAME_VERSION")
				line_split = line.strip.split("=")
				if line_split.length > 1
				newVersion = line.strip.split("=")[1].strip
				break
				end
			end
			end
		
			if !newVersion
			Kernel.pbMessage("#{pbGetUpdaterText('UPDATER_MISCONFIGURATION')}")
			return
			end
		
			if GameVersion::POKE_UPDATER_CONFIG
				newVersion = newVersion.gsub!(/(?!^[.0-9]*$)/, '')
				if !newVersion
					Kernel.pbMessage("#{pbGetPokeUpdaterText('UPDATER_MISCONFIGURATION')}")
					return
				end
				
				currentVersion = GameVersion::POKE_UPDATER_CONFIG['CURRENT_GAME_VERSION'].gsub!(/(?!^[.0-9]*$)/, '')
				if !currentVersion
					Kernel.pbMessage("#{pbGetPokeUpdaterText('UPDATER_MISCONFIGURATION')}")
					return
				end

				if compare_versions(newVersion, currentVersion)
					newVersionText = pbGetPokeUpdaterText('NEW_VERSION', newVersion)  
					
					Kernel.pbMessage("#{newVersionText}")
					if !Kernel.pbConfirmMessage("#{pbGetPokeUpdaterText('ASK_FOR_UPDATE')}")
						return if !GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE']
						Kernel.pbMessage(_INTL("#{pbGetPokeUpdaterText('FORCE_UPDATE_ON')}"))
						Kernel.exit!
					else
						update = true
					end
	
					if !GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE'] && !update
						if GameVersion::POKE_UPDATER_CONFIG['HAS_UPDATE_BUTTON'] 
							Kernel.pbMessage("#{pbGetPokeUpdaterText('BUTTON_UPDATE')}")
						else
							Kernel.pbMessage("#{pbGetPokeUpdaterText('MANUAL_UPDATE')}")
						end
						return
					end
					
					if GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE'] || update
						if !File.exists?(GameVersion::POKE_UPDATER_CONFIG['UPDATER_FILENAME'])
							Kernel.pbMessage("#{pbGetPokeUpdaterText('UPDATER_NOT_FOUND')}")
							return
						end
						Kernel.pbMessage("#{pbGetPokeUpdaterText('UPDATE')}")
						IO.popen(GameVersion::POKE_UPDATER_CONFIG['UPDATER_FILENAME'])
						Kernel.exit!
					end
				else
					Kernel.pbMessage(pbGetPokeUpdaterText('NO_NEW_VERSION')) if from_update_button 
				end
			end
		end
	end
end

def compare_versions(new_version, current_version)
	old_version_split = current_version.split('.')
	new_version_split = new_version.split('.')
	
	version_len = [new_version_split.length, old_version_split.length].min
	
	(0...version_len).each do |i|
	  return true if new_version_split[i] > old_version_split[i]
	end
	
	# Version number is the same when comparing shorter version number, validate if this is a smaller patch with a non-standard versioning format
	# If there is no difference found, then version number is the same
	return new_version_split.length > old_version_split.length
end