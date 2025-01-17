module GameVersion
	# Required constants for game validation / update
	# Constantes requeridas para validación / actualización del juego
	POKE_UPDATER_CONFIG = {}
	POKE_UPDATER_LOCALES = {}
end

def fill_updater_config()
	trueValues = ['true', 'y', 'si', 'yes', 's']
	falseValues = ['false', 'n', 'no']
	return if !File.exists?('pu_config')
	File.foreach('pu_config'){|line|
			splitted_line = line.split('=')
			next if !splitted_line
			
			splitted_line[1] = splitted_line[1].strip
			GameVersion::POKE_UPDATER_CONFIG[splitted_line[0].strip] = splitted_line[1]
			
			if trueValues.include?(splitted_line[1].downcase) || falseValues.include?(splitted_line[1].downcase)
				GameVersion::POKE_UPDATER_CONFIG[splitted_line[0].strip] = true ? trueValues.include?(splitted_line[1].downcase) : false        
			elsif splitted_line[1].strip.match(/\d+\.\d+/)
				GameVersion::POKE_UPDATER_CONFIG[splitted_line[0].strip] = splitted_line[1].strip.to_f
			end
		}
			
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
			GameVersion::POKE_UPDATER_LOCALES = JSON.parse(File.read('pu_locales'))
		else
			GameVersion::POKE_UPDATER_LOCALES = eval(File.read('pu_locales'))
		end
end
	

def get_lang()
	System.user_language[0..1]
end
	
def get_poke_updater_text(text_name, variable=nil)
	lang = get_lang()
	if GameVersion::POKE_UPDATER_LOCALES && GameVersion::POKE_UPDATER_LOCALES[text_name] && GameVersion::POKE_UPDATER_LOCALES[text_name][lang] && GameVersion::POKE_UPDATER_LOCALES[text_name][lang] != ""
		if GameVersion::POKE_UPDATER_LOCALES[text_name][lang].include?('#{variable}')
			textToReturn = GameVersion::POKE_UPDATER_LOCALES[text_name][lang]
			textToReturn['#{variable}'] = variable.to_s
			return textToReturn
		end
		return GameVersion::POKE_UPDATER_LOCALES[text_name][lang]
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
		return "Estás jugando en joiplay por favor entra a la red social del creador para descargar la última versión del juego."
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
	end
end


def validate_game_version_and_update(from_update_button=false)
	fill_updater_config if !GameVersion::POKE_UPDATER_CONFIG
	return if !GameVersion::POKE_UPDATER_CONFIG
	if !GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] || GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] == ''
		Kernel.pbMessage(_INTL(get_poke_updater_text('NO_PASTEBIN_URL'))) if from_update_button
		return
	end
	validate_version(GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'], true, from_update_button)
end

def validate_game_version(from_update_button=false)
	fill_updater_config if !GameVersion::POKE_UPDATER_CONFIG
	return if !GameVersion::POKE_UPDATER_CONFIG 
	if !GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] || GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] == ''
		Kernel.pbMessage(_INTL(get_poke_updater_text('NO_PASTEBIN_URL'))) if from_update_button
		return
	end
	validate_version(GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'], false, from_update_button)
end

def check_for_updates(from_update_button=false)
	if !$joiplay || major_version >= 19 # Esto es para evitar correr este codigo en Joiplay
		fill_updater_config()
		if GameVersion::POKE_UPDATER_CONFIG && GameVersion::POKE_UPDATER_CONFIG
			validate_game_version(from_update_button)
		end
	end
end

def new_version?(new_version, current_version)
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

def validate_version(url, update=false, from_update_button=false)
	begin
		data = pbDownloadToString(url)
	rescue MKXPError
		Kernel.pbMessage("#{get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET')}")
		return
	end
	if data
		newVersion = data.split("\n")[0].strip.split("=")[1].strip.to_f
		if GameVersion::POKE_UPDATER_CONFIG
			if new_version?(newVersion, GameVersion::POKE_UPDATER_CONFIG['CURRENT_GAME_VERSION'])
				newVersionText = get_poke_updater_text('NEW_VERSION', newVersion)  
				
				Kernel.pbMessage(_INTL("#{newVersionText}"))
				if $joiplay
					Kernel.pbMessage(_INTL("#{get_poke_updater_text('JOIPLAY_UPDATE')}"))
					return
				end
	
				if !pbConfirmMessage(_INTL("#{get_poke_updater_text('ASK_FOR_UPDATE')}"))
					return if !GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE']
					Kernel.pbMessage(_INTL("#{get_poke_updater_text('FORCE_UPDATE_ON')}"))
					Kernel.exit!
				end
	
				if !GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE'] && !update
					if GameVersion::POKE_UPDATER_CONFIG['HAS_UPDATE_BUTTON'] 
						Kernel.pbMessage(_INTL("#{get_poke_updater_text('BUTTON_UPDATE')}"))
					else
						Kernel.pbMessage(_INTL("#{get_poke_updater_text('MANUAL_UPDATE')}"))
					end
					return
				end
				
				if GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE'] || update
					if !File.exists?(GameVersion::POKE_UPDATER_CONFIG['UPDATER_FILENAME'])
						Kernel.pbMessage(_INTL("#{get_poke_updater_text('UPDATER_NOT_FOUND')}"))
						return
					end
					Kernel.pbMessage(_INTL("#{get_poke_updater_text('UPDATE')}"))
					IO.popen(GameVersion::POKE_UPDATER_CONFIG['UPDATER_FILENAME'])
					Kernel.exit!
				end
			else
				Kernel.pbMessage(_INTL(get_poke_updater_text('NO_NEW_VERSION'))) if from_update_button
			end 
		end
	else
		Kernel.pbMessage(_INTL(get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET')))
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
