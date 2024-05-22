module GameVersion
  # Required constants for game validation / update
  # Constantes requeridas para validación / actualización del juego
  POKE_UPDATER_CONFIG = {}
  POKE_UPDATER_LOCALES = {}
end

def pbFillUpdaterConfig()
  trueValues = ['true', 'y', 'si', 'yes', 's']
  falseValues = ['false', 'n', 'no']
  return if !File.exists?('pu_config')
  File.foreach('pu_config'){|line|
      splittedLine = line.split('=')
      next if !splittedLine
      
      splittedLine[1] = splittedLine[1].strip
      GameVersion::POKE_UPDATER_CONFIG[splittedLine[0].strip] = splittedLine[1]
      
      if trueValues.include?(splittedLine[1].downcase) || falseValues.include?(splittedLine[1].downcase)
        GameVersion::POKE_UPDATER_CONFIG[splittedLine[0].strip] = true ? trueValues.include?(splittedLine[1].downcase) : false        
      elsif splittedLine[1].strip.match(/\d+\.\d+/)
        GameVersion::POKE_UPDATER_CONFIG[splittedLine[0].strip] = splittedLine[1].strip.to_f
      end
    }
      
    return if !File.exists?('pu_locales')
    File.foreach('pu_locales'){|line|
      splittedLine = line.split('=')
      next if !splittedLine
      
      splittedLine[1] = splittedLine[1].strip
      texts = splittedLine[1].split('|')
      GameVersion::POKE_UPDATER_LOCALES[splittedLine[0].strip] = []
      for text in texts
        GameVersion::POKE_UPDATER_LOCALES[splittedLine[0].strip].push(text)
      end
    }
end
  

def getLanguage()
  return 7 if $joiplay
  getUserDefaultLangID=Win32API.new("kernel32","GetUserDefaultUILanguage","","i") rescue nil
  ret=0
  if getUserDefaultLangID
    ret=getUserDefaultLangID.call()&0x3FF
  end
  if ret==0 # Unknown
    ret=MiniRegistry.get(MiniRegistry::HKEY_CURRENT_USER, "Control Panel\\Desktop\\ResourceLocale","",0)
    ret=MiniRegistry.get(MiniRegistry::HKEY_CURRENT_USER, "Control Panel\\International","Locale","0").to_i(16) if ret==0
    ret=ret&0x3FF
    return 0 if ret==0  # Unknown
  end
  return 1 if ret==0x11 # Japanese
  return 2 if ret==0x09 # English
  return 3 if ret==0x0C # French
  return 4 if ret==0x10 # Italian
  return 5 if ret==0x07 # German
  return 7 if ret==0x0A # Spanish
  return 8 if ret==0x12 # Korean
  return 7 # Use 'Spanish' by default
end
  
def pbGetPokeUpdaterText(textName, variable=nil)
  lang = getLanguage()
  if GameVersion::POKE_UPDATER_LOCALES && GameVersion::POKE_UPDATER_LOCALES[textName] && GameVersion::POKE_UPDATER_LOCALES[textName][lang] && GameVersion::POKE_UPDATER_LOCALES[textName][lang] != ""
    if GameVersion::POKE_UPDATER_LOCALES[textName][lang].include?('#{variable}')
      textToReturn = GameVersion::POKE_UPDATER_LOCALES[textName][lang]
      textToReturn['#{variable}'] = variable.to_s
      return textToReturn
    end
    return GameVersion::POKE_UPDATER_LOCALES[textName][lang]
  end
  case textName
    when 'NEW_VERSION'
      return "¡Version #{variable} disponible!"
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
  end
end


def pbValidateGameVersionAndUpdate(from_update_button=false)
  pbFillUpdaterConfig if !GameVersion::POKE_UPDATER_CONFIG
  return if !GameVersion::POKE_UPDATER_CONFIG
  if !GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] || GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] == ''
    Kernel.pbMessage(pbGetPokeUpdaterText('NO_PASTEBIN_URL')) if from_update_button
    return
  end
  pbValidateVersion(GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'], true, from_update_button)
end

def pbValidateGameVersion(from_update_button=false)
  pbFillUpdaterConfig if !GameVersion::POKE_UPDATER_CONFIG
  return if !GameVersion::POKE_UPDATER_CONFIG 
  if !GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] || GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'] == ''
	  Kernel.pbMessage(pbGetPokeUpdaterText('NO_PASTEBIN_URL')) if from_update_button
	  return
  end
  pbValidateVersion(GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'], false, from_update_button)
end

def pbCheckForUpdates(from_update_button=false)
	if !$joiplay || major_version >= 19 # Esto es para evitar correr este codigo en Joiplay
	  pbFillUpdaterConfig()
	  if GameVersion::POKE_UPDATER_CONFIG && GameVersion::POKE_UPDATER_CONFIG
		  pbValidateGameVersion(from_update_button)
	  end
	end
end

def pbValidateVersion(url, update=false, from_update_button=false)
	data = pbDownloadData(url)
	if data
	  newVersion = data.split("\n")[0].strip.split("=")[1].strip.to_f
		if GameVersion::POKE_UPDATER_CONFIG
		  if newVersion > GameVersion::POKE_UPDATER_CONFIG['CURRENT_GAME_VERSION']
			newVersionText = pbGetPokeUpdaterText('NEW_VERSION', newVersion)  
			
			Kernel.pbMessage("#{newVersionText}")
			if $joiplay
				Kernel.pbMessage("#{pbGetUpdaterText('JOIPLAY_UPDATE')}")
				return
			end

      if !pbConfirmMessage("#{pbGetPokeUpdaterText('ASK_FOR_UPDATE')}")
        return if !GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE']
        Kernel.pbMessage("#{pbGetPokeUpdaterText('FORCE_UPDATE_ON')}")
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
	else
	  Kernel.pbMessage(pbGetPokeUpdaterText('NO_NEW_VERSION_OR_INTERNET'))
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