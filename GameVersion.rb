module GameVersion
  # Required constants for game validation / update
  # Constantes requeridas para validación / actualización del juego
  POKE_UPDATER_CONFIG = {}
  POKE_UPDATER_LOCALES = {}
end
def pbFillUpdaterConfig()
  trueValues = ['true', 'y', 'si', 'yes', 's']
  falseValues = ['false', 'n', 'no']
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
  getUserDefaultLangID=Win32API.new("kernel32","GetUserDefaultUILanguage","","i") rescue nil
  ret=0
  if getUserDefaultLangID
    ret=getUserDefaultLangID.call()&0x3FF
  end
  if ret==0 # Unknown
    ret=MiniRegistry.get(MiniRegistry::HKEY_CURRENT_USER,
       "Control Panel\\Desktop\\ResourceLocale","",0)
    ret=MiniRegistry.get(MiniRegistry::HKEY_CURRENT_USER,
       "Control Panel\\International","Locale","0").to_i(16) if ret==0
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
  
def pbGetPokeUpdaterText(textName)
  lang = getLanguage()
  if GameVersion::POKE_UPDATER_LOCALES && GameVersion::POKE_UPDATER_LOCALES[textName][lang] && GameVersion::POKE_UPDATER_LOCALES[textName][lang] != ""
    return GameVersion::POKE_UPDATER_LOCALES[textName][lang]
  end
  case textName
    when 'NEW_VERSION'
      return "¡Version #{newVersion} disponible!"
    when 'BUTTON_UPDATE'
      return "Para actualizar utilice el botón 'Actualizar juego' del menú."
    when 'MANUAL_UPDATE'
      return "Por favor actualice el juego entrando a la red social del creador"
    when 'UPDATE'
      return "El juego se actualizará y reiniciará automáticamente. Esto puede demorar unos minutos. Tus partidas guardadas NO se verán afectadas durante la actualización."
    when 'NO_NEW_VERSION'
      return "Estás en la última versión"
  end
end

def pbValidateGameVersionAndUpdate()
  return if !GameVersion::POKE_UPDATER_CONFIG
  thread = nil
  thread = VersionCheck::Connection.validateVersion(GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'], true)
  thread.join if thread
end

def pbValidateGameVersion()
  return if !GameVersion::POKE_UPDATER_CONFIG
  thread = nil
  thread = VersionCheck::Connection.validateVersion(GameVersion::POKE_UPDATER_CONFIG['VERSION_PASTEBIN'], false)
  thread.join if thread
end