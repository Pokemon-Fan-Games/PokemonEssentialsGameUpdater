module PokeUpdater
	module Config
		# Required constants for game validation / update
		# Constantes requeridas para validación / actualización del juego
		@poke_updater_config = {}
		@poke_updater_locales = {}

		def self.poke_updater_locales=(value)
			@poke_updater_locales = value
		end

		def self.poke_updater_locales
			@poke_updater_locales
		end

		def self.poke_updater_config=(value)
			@poke_updater_config = value
		end

		def self.poke_updater_config
			@poke_updater_config
		end

		TRUE_VALUES = ['true', 'y', 'si', 'yes', 's'].freeze
		FALSE_VALUES = ['false', 'n', 'no'].freeze
	end

	module_function
	def fill_updater_config()
		return if !File.exists?('pu_config')
		config = {}
		File.foreach('pu_config'){|line|
			splitted_line = line.split('=')
			next if !splitted_line

			splitted_line[1] = splitted_line[1].strip
			config[splitted_line[0].strip] = splitted_line[1]

			if Config::TRUE_VALUES.include?(splitted_line[1].downcase) || Config::FALSE_VALUES.include?(splitted_line[1].downcase)
				config[splitted_line[0].strip] = true ? Config::TRUE_VALUES.include?(splitted_line[1].downcase) : false
			elsif splitted_line[1].strip.match(/\d+\.\d+/)
				config[splitted_line[0].strip] = splitted_line[1].strip
			end
		}
		
		Config.poke_updater_config = config

				
		return if !File.exists?('pu_locales')
		Config.poke_updater_locales = HTTPLite::JSON.parse(File.read('pu_locales'))
	end
	

	def get_lang()
		System.user_language[0..1]
	end
	
	def get_poke_updater_text(text_name, variable=nil)
		lang = get_lang()
		if Config.poke_updater_locales && Config.poke_updater_locales[text_name] && Config.poke_updater_locales[text_name][lang] && Config.poke_updater_locales[text_name][lang] != ""
			if Config.poke_updater_locales[text_name][lang].include?('#{variable}')
				textToReturn = Config.poke_updater_locales[text_name][lang]
				textToReturn['#{variable}'] = variable.to_s
				return textToReturn
			end
			return Config.poke_updater_locales[text_name][lang]
		end
		case text_name
		when 'NEW_VERSION'
			return "¡Nueva versión #{variable} disponible!"
		when 'BUTTON_UPDATE'
			return "Para actualizar utilice el botón disponible en el menú."
		when 'MANUAL_UPDATE'
			return "Por favor, actualiza el juego entrando a la red social del creador (Twitter/X: @Sky_fangames)."
		when 'UPDATE'
			return "El juego se actualizará y reiniciará automáticamente. Esto puede demorar unos minutos. Tus partidas guardadas NO se verán afectadas durante la actualización."
		when 'NO_NEW_VERSION'
			return "No hay nuevas versiones disponibles en este momento."
		when 'JOIPLAY_UPDATE'
			return "Estás jugando en joiplay, por favor entra a la red social del creador para descargar la última versión del juego (Twitter/X: @Sky_fangames)."
		when 'UPDATER_NOT_FOUND'
			return 'No se ha encontrado el actualizador del juego.'
		when 'NO_NEW_VERSION_OR_INTERNET'
			return 'No tienes conexión a internet o no se encontró una nueva versión del juego.'
		when 'NO_PASTEBIN_URL'
			return 'No hay una URL al pastebin en el archivo de configuración, repórtalo con el creador del juego.'
		when 'ASK_FOR_UPDATE'
			return '¿Deseas actualizar el juego?'
		when 'FORCE_UPDATE_ON'
			return 'La actualización del juego es obligatoria, el juego se cerrará.'
		when 'UPDATER_MISCONFIGURATION'
			return 'Hay errores en la configuración del updater, repórtalo con el creador del juego.'
		when 'MANUAL_DOWNLOAD_CONFIRM'
			return "¿Desea abrir el link de descarga?"
		when 'ASK_FOR_CHANGELOG'
			return '¿Deseas ver el changelog de la nueva versión?'
		when 'CURRENT_VERSION'
			return "Estás en la versión #{Config.poke_updater_config['CURRENT_GAME_VERSION']}."
		end
	end


	def validate_game_version_and_update(from_update_button=false)
		fill_updater_config if !Config.poke_updater_config || !Config.poke_updater_config['PASTEBIN_URL']
		return if !Config.poke_updater_config
		if !Config.poke_updater_config['PASTEBIN_URL'] || Config.poke_updater_config['PASTEBIN_URL'] == ''
			pbMessage(get_poke_updater_text('NO_PASTEBIN_URL')) if from_update_button
			return
		end
		validate_version(Config.poke_updater_config['PASTEBIN_URL'], from_update_button)
	end

	def validate_game_version(from_update_button=false)
		fill_updater_config if !Config.poke_updater_config || !Config.poke_updater_config['PASTEBIN_URL']
		return if !Config.poke_updater_config
		if !Config.poke_updater_config['PASTEBIN_URL'] || Config.poke_updater_config['PASTEBIN_URL'] == ''
			pbMessage(get_poke_updater_text('NO_PASTEBIN_URL')) if from_update_button
			return
		end
		validate_version(Config.poke_updater_config['PASTEBIN_URL'], from_update_button)
	end

	def check_for_updates(from_update_button=false)
		return if $DEBUG
		return if !network_available?
		fill_updater_config() if !Config.poke_updater_config || !Config.poke_updater_config['PASTEBIN_URL']
		if Config.poke_updater_config && Config.poke_updater_config['PASTEBIN_URL'] && Config.poke_updater_config['PASTEBIN_URL'] != ''
			validate_game_version(from_update_button)
		end
	end


	def new_version?(new_version, current_version)
		# Input validation
		return false if new_version.nil? || current_version.nil?
		return false if new_version.to_s.strip.empty? || current_version.to_s.strip.empty?
		return false if new_version == current_version
		
		begin
			# Parse version components (handles pre-release identifiers)
			new_parts = parse_version_parts(new_version)
			current_parts = parse_version_parts(current_version)
			
			# Compare main version numbers first
			version_comparison = compare_version_numbers(new_parts[:numbers], current_parts[:numbers])
			return version_comparison > 0 if version_comparison != 0
			
			# If main versions are equal, compare pre-release identifiers
			compare_prerelease(new_parts[:prerelease], current_parts[:prerelease]) > 0
		rescue StandardError => e
			# If parsing fails, log error and return false (assume no update needed)
			puts "Error comparing versions '#{new_version}' and '#{current_version}': #{e.message}"
			false
		end
	end

	# Parse version string into numbers and pre-release identifier
	def parse_version_parts(version_string)
		# Split on first non-digit, non-dot character
		if version_string =~ /^(\d+(?:\.\d+)*)(.*)$/
			numbers_part = $1
			prerelease_part = $2.strip
			
			numbers = numbers_part.split('.').map(&:to_i)
			prerelease = prerelease_part.empty? ? nil : prerelease_part.downcase.gsub(/^[.-]/, '')
			
			{ numbers: numbers, prerelease: prerelease }
		else
			# Fallback for malformed versions
			{ numbers: [0], prerelease: version_string.downcase }
		end
	end

	# Compare two arrays of version numbers
	def compare_version_numbers(new_nums, current_nums)
		# Pad shorter version array with zeros
		max_length = [new_nums.length, current_nums.length].max
		new_nums = new_nums.dup.fill(0, new_nums.length, max_length - new_nums.length)
		current_nums = current_nums.dup.fill(0, current_nums.length, max_length - current_nums.length)
		
		new_nums <=> current_nums
	end

	# Compare pre-release identifiers
	# nil (stable release) > any pre-release
	# Within pre-releases: rc > beta > alpha
	def compare_prerelease(new_pre, current_pre)
		return 0 if new_pre == current_pre
		
		# Stable release (nil) is always greater than pre-release
		return 1 if new_pre.nil? && !current_pre.nil?
		return -1 if !new_pre.nil? && current_pre.nil?
		
		# Both are pre-releases, compare them
		pre_order = { 'alpha' => 1, 'beta' => 2, 'rc' => 3 }
		
		new_order = pre_order[new_pre] || 0
		current_order = pre_order[current_pre] || 0
		
		new_order <=> current_order
	end

	def validate_version(url, from_update_button=false, update=true)
		begin
			data = pbDownloadToString(url)
		rescue MKXPError
			pbMessage(get_poke_updater_text("NO_NEW_VERSION_OR_INTERNET").to_s) if from_update_button
			return
		end
		if data && !data.empty?
			lines = data.split("\n")
			new_version = nil
			force_update = false
			download_url = nil
			changelog = nil
			
			lines.each_with_index do |line, i|
				next if line.strip.empty? || line.start_with?("#")
				
				if line.include?("GAME_VERSION")
					key_value = line.strip.split("=", 2)
					if key_value.length > 1
						new_version = key_value[1].strip
					end
				elsif line.include?("DOWNLOAD_URL")
					key_value = line.strip.split("=", 2)
					if key_value.length > 1
						download_url = key_value[1].strip
					end
				elsif line.include?("FORCE_UPDATE")
					key_value = line.strip.split("=", 2)
					if key_value.length > 1
						str_value = key_value[1]&.strip
						force_update = Config::TRUE_VALUES.include?(str_value.downcase)
					end
				elsif line.include?("CHANGELOG")
					key_value = line.strip.split("=", 2)
					if key_value.length > 1
						changelog_start = key_value[1].strip
						changelog_lines = [changelog_start]
						j = i + 1
						while j < lines.length && !lines[j].strip.empty? && !lines[j].include?("=")
							changelog_lines << lines[j]
							j += 1
						end
						changelog = changelog_lines.join("\n").strip
					end
				end
			end
			if Config.poke_updater_config
				if new_version && !new_version.empty? && new_version?(new_version, Config.poke_updater_config['CURRENT_GAME_VERSION'])
					new_version_text = get_poke_updater_text('NEW_VERSION', new_version)

				pbMessage(new_version_text)
					if changelog&.length > 0 && pbConfirmMessage(get_poke_updater_text('ASK_FOR_CHANGELOG'))
						pbMessage("Changelog:\n#{changelog}")
					end
					if $joiplay
						pbMessage(get_poke_updater_text('JOIPLAY_UPDATE').to_s)
						if download_url && pbConfirmMessage(_INTL("¿Quieres abrir el link de la descarga?"))
							begin
								MKXP.launch(download_url) # Joiplay
							rescue MKXPError, NoMethodError, NameError
								puts "Incompatible Joiplay version detected." if $DEBUG_LOG
							end 
      			end
						return
					end

					if !pbConfirmMessage(get_poke_updater_text('ASK_FOR_UPDATE').to_s)
						return if !force_update
						pbMessage(get_poke_updater_text('FORCE_UPDATE_ON').to_s)
						Kernel.exit!
					end

					if !force_update && !update
            unless FileTest.exist?(Config.poke_updater_config['UPDATER_FILENAME'])
							pbMessage("#{get_poke_updater_text('MANUAL_UPDATE', Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'])}")
							if !Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'].empty? && pbConfirmMessageBlack("#{get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM')}")
								System.launch(Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'])
							end
							return
						end
						if Config.poke_updater_config['HAS_UPDATE_BUTTON']
							pbMessage("#{get_poke_updater_text('BUTTON_UPDATE')}")
						else
							pbMessage("#{get_poke_updater_text('MANUAL_UPDATE', Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'])}")
							if !Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'].empty? && pbConfirmMessage("#{get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM')}")
								System.launch(Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'])
							end
						end
						return
					end
					
					if force_update || update
						if !File.exists?(Config.poke_updater_config['UPDATER_FILENAME'])
							pbMessage("#{get_poke_updater_text('MANUAL_UPDATE', Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'])}")
							if !Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'].empty? && pbConfirmMessage("#{get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM')}")
								System.launch(Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'])
							end
							return
						end
						pbMessage(get_poke_updater_text('UPDATE'))
						IO.popen(Config.poke_updater_config['UPDATER_FILENAME'])
						Kernel.exit!
					end
				else
					if from_update_button
						pbMessage(get_poke_updater_text('CURRENT_VERSION', Config.poke_updater_config['CURRENT_GAME_VERSION']))
						pbMessage(get_poke_updater_text('NO_NEW_VERSION')) 
					end
				end 
			end
		else
			pbMessage(get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET')) if from_update_button
			return
		end
	end

end

def major_version
	ret = 0
	if defined?(Essentials)
		ret = Essentials::VERSION.split(".")[0].to_i
	elsif defined?(ESSENTIALS_VERSION)
		ret = ESSENTIALS_VERSION.split(".")[0].to_i
	elsif defined?(ESSENTIALSVERSION)
		ret = ESSENTIALSVERSION.split(".")[0].to_i
	end
	return ret
end
