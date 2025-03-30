module GameVersion
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

end

def fill_updater_config()
	trueValues = ['true', 'y', 'si', 'yes', 's']
	falseValues = ['false', 'n', 'no']
	return if !File.exists?('pu_config')
	config = {}
	File.foreach('pu_config'){|line|
		splitted_line = line.split('=')
		next if !splitted_line

		splitted_line[1] = splitted_line[1].strip
		config[splitted_line[0].strip] = splitted_line[1]
		
		if trueValues.include?(splitted_line[1].downcase) || falseValues.include?(splitted_line[1].downcase)
			config[splitted_line[0].strip] = true ? trueValues.include?(splitted_line[1].downcase) : false        
		elsif splitted_line[1].strip.match(/\d+\.\d+/)
			config[splitted_line[0].strip] = splitted_line[1].strip
		end
	}
	
	GameVersion.poke_updater_config = config

			
	return if !File.exists?('pu_locales')
	if defined?(JSON)
		json_library_available = true
	else
		begin
			# Attempt to require 'json' library
			require 'json'
			json_library_available = true
		rescue LoadError
			# Fallback to using eval if 'json' is not available
			json_library_available = false
		end
	end
	if json_library_available
		GameVersion.poke_updater_locales = JSON.parse(File.read('pu_locales'))
	else
		GameVersion.poke_updater_locales = eval(File.read('pu_locales'))
	end
end
	

def get_lang()
	System.user_language[0..1]
end
	
def get_poke_updater_text(text_name, variable=nil)
	lang = get_lang()
	if GameVersion.poke_updater_locales && GameVersion.poke_updater_locales[text_name] && GameVersion.poke_updater_locales[text_name][lang] && GameVersion.poke_updater_locales[text_name][lang] != ""
		if GameVersion.poke_updater_locales[text_name][lang].include?('#{variable}')
			textToReturn = GameVersion.poke_updater_locales[text_name][lang]
			textToReturn['#{variable}'] = variable.to_s
			return textToReturn
		end
		return GameVersion.poke_updater_locales[text_name][lang]
	end
	case text_name
	when 'NEW_VERSION'
		return "¡Nueva versión #{variable} disponible!"
	when 'BUTTON_UPDATE'
		return "Para actualizar utilice el botón disponible en el menú."
	when 'MANUAL_UPDATE'
		return "Por favor actualice el juego entrando a la red social del creador"
	when 'UPDATE'
		return "El juego se actualizará y reiniciará automáticamente. Esto puede demorar unos minutos. Tus partidas guardadas NO se verán afectadas durante la actualización."
	when 'NO_NEW_VERSION'
		return "Estás en la última versión"
	when 'JOIPLAY_UPDATE'
		return "Estás jugando en joiplay, por favor entra a la red social del creador para descargar la última versión del juego."
	when 'UPDATER_NOT_FOUND'
		return 'No se ha encontrado el actualizador del juego.'
	when 'NO_NEW_VERSION_OR_INTERNET'
		return 'No tienes conexión a internet o se encontró una nueva versión del juego.'
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
	end
end


def validate_game_version_and_update(from_update_button=false)
	fill_updater_config if !GameVersion.poke_updater_config || !GameVersion.poke_updater_config['VERSION_PASTEBIN']
	return if !GameVersion.poke_updater_config
	if !GameVersion.poke_updater_config['VERSION_PASTEBIN'] || GameVersion.poke_updater_config['VERSION_PASTEBIN'] == ''
		Kernel.pbMessage(get_poke_updater_text('NO_PASTEBIN_URL')) if from_update_button
		return
	end
	validate_version(GameVersion.poke_updater_config['VERSION_PASTEBIN'], from_update_button)
end

def validate_game_version(from_update_button=false)
	fill_updater_config if !GameVersion.poke_updater_config || !GameVersion.poke_updater_config['VERSION_PASTEBIN']
	return if !GameVersion.poke_updater_config 
	if !GameVersion.poke_updater_config['VERSION_PASTEBIN'] || GameVersion.poke_updater_config['VERSION_PASTEBIN'] == ''
		Kernel.pbMessage(get_poke_updater_text('NO_PASTEBIN_URL')) if from_update_button
		return
	end
	validate_version(GameVersion.poke_updater_config['VERSION_PASTEBIN'], from_update_button)
end

def check_for_updates(from_update_button=false)
	if major_version >= 19 # Esto es para evitar correr este codigo en Joiplay
		fill_updater_config() if !GameVersion.poke_updater_config || !GameVersion.poke_updater_config['VERSION_PASTEBIN']
		if GameVersion.poke_updater_config && GameVersion.poke_updater_config['VERSION_PASTEBIN'] && GameVersion.poke_updater_config['VERSION_PASTEBIN'] != ''
			validate_game_version(from_update_button)
		end
	end
end


def new_version?(new_version, current_version)
  # Split version strings into arrays of integers
  old_version_nums = current_version.split('.').map(&:to_i)
  new_version_nums = new_version.split('.').map(&:to_i)

  # Compare version numbers using spaceship operator
  (new_version_nums <=> old_version_nums) == 1
end

def validate_version(url, from_update_button=false, update=true)
	begin
		data = pbDownloadToString(url)
	rescue MKXPError
		Kernel.pbMessage("#{get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET')}")
		return
	end
	if data
		lines = data.split("\n")
		newVersion = nil
		lines.each do |line|
			if line.include?("GAME_VERSION")
				line_split = line.strip.split("=")
				if line_split.length > 1
					newVersion = line.strip.split("=")[1].strip
					break
				end
			end
		end
		if GameVersion.poke_updater_config
			if new_version?(newVersion, GameVersion.poke_updater_config['CURRENT_GAME_VERSION'])
				newVersionText = get_poke_updater_text('NEW_VERSION', newVersion)  
			
				Kernel.pbMessage("#{newVersionText}")
				if $joiplay
					Kernel.pbMessage("#{get_poke_updater_text('JOIPLAY_UPDATE')}")
					return
				end

				if !pbConfirmMessage("#{get_poke_updater_text('ASK_FOR_UPDATE')}")
					return if !GameVersion.poke_updater_config['FORCE_UPDATE']
					Kernel.pbMessage("#{get_poke_updater_text('FORCE_UPDATE_ON')}")
					Kernel.exit!
				end

				if !GameVersion.poke_updater_config['FORCE_UPDATE'] && !update
					if !File.exists?(GameVersion.poke_updater_config['UPDATER_FILENAME'])
						Kernel.pbMessageBlack("#{get_poke_updater_text('MANUAL_UPDATE', GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'])}")
						if !GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'].empty? && pbConfirmMessageBlack("#{get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM')}")
							System.launch(GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'])
						end
						return
					end
					if GameVersion.poke_updater_config['HAS_UPDATE_BUTTON'] 
						Kernel.pbMessage("#{get_poke_updater_text('BUTTON_UPDATE')}")
					else
						Kernel.pbMessage("#{get_poke_updater_text('MANUAL_UPDATE', GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'])}")
						if !GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'].empty? && pbConfirmMessage("#{get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM')}")
							System.launch(GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'])
						end
					end
					return
				end
				
				if GameVersion.poke_updater_config['FORCE_UPDATE'] || update
					if !File.exists?(GameVersion.poke_updater_config['UPDATER_FILENAME'])
						Kernel.pbMessage("#{get_poke_updater_text('MANUAL_UPDATE', GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'])}")
						if !GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'].empty? && pbConfirmMessage("#{get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM')}")
							System.launch(GameVersion.poke_updater_config['MANUAL_DOWNLOAD_LINK'])
						end
						return
					end
					Kernel.pbMessage(get_poke_updater_text('UPDATE'))
					IO.popen(GameVersion.poke_updater_config['UPDATER_FILENAME'])
					Kernel.exit!
				end
			else
				Kernel.pbMessage(get_poke_updater_text('NO_NEW_VERSION')) if from_update_button
			end 
		end
	else
		Kernel.pbMessage(get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET'))
		return
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
