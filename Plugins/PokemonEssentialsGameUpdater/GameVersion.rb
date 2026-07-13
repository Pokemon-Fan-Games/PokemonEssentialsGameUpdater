module PokeUpdater
	module Config
		# Required constants for game validation / update
		# Constantes requeridas para validación / actualización del juego
		class << self
			attr_accessor :poke_updater_config, :poke_updater_locales
		end
		self.poke_updater_config = {}
		self.poke_updater_locales = {}

		CONFIG_FILE = 'pu_config'
		LOCALES_FILE = 'pu_locales.json'
		TRUE_VALUES = ['true', 'y', 'si', 'yes', 's'].freeze
		FALSE_VALUES = ['false', 'n', 'no'].freeze
	end

	DEFAULT_TEXTS = {
		'NEW_VERSION'              => '¡Nueva versión #{variable} disponible!',
		'BUTTON_UPDATE'            => 'Para actualizar utilice el botón disponible en el menú.',
		'MANUAL_UPDATE'            => 'Por favor, actualiza el juego entrando a la red social del creador (Twitter/X: @Sky_fangames).',
		'UPDATE'                   => 'El juego se actualizará y reiniciará automáticamente. Esto puede demorar unos minutos. Tus partidas guardadas NO se verán afectadas durante la actualización.',
		'NO_NEW_VERSION'           => 'No hay nuevas versiones disponibles en este momento.',
		'JOIPLAY_UPDATE'           => 'Estás jugando en joiplay, por favor entra a la red social del creador para descargar la última versión del juego (Twitter/X: @Sky_fangames).',
		'UPDATER_NOT_FOUND'        => 'No se ha encontrado el actualizador del juego.',
		'NO_NEW_VERSION_OR_INTERNET' => 'No tienes conexión a internet o no se encontró una nueva versión del juego.',
		'NO_PASTEBIN_URL'          => 'No hay una URL al pastebin en el archivo de configuración, repórtalo con el creador del juego.',
		'ASK_FOR_UPDATE'           => '¿Deseas actualizar el juego?',
		'FORCE_UPDATE_ON'          => 'La actualización del juego es obligatoria, el juego se cerrará.',
		'UPDATER_MISCONFIGURATION' => 'Hay errores en la configuración del updater, repórtalo con el creador del juego.',
		'MANUAL_DOWNLOAD_CONFIRM'  => '¿Desea abrir el link de descarga?',
		'ASK_FOR_CHANGELOG'        => '¿Deseas ver el changelog de la nueva versión?',
		'CURRENT_VERSION'          => 'Estás en la versión #{variable}.'
	}.freeze

	REMOTE_KEYS = ['GAME_VERSION', 'DOWNLOAD_URL', 'FORCE_UPDATE', 'CHANGELOG'].freeze

	module_function

	# Parses a "KEY = value" line. Returns nil when the line has no separator,
	# is empty or is a comment.
	def parse_config_line(line)
		return nil if line.nil?
		stripped = line.strip
		return nil if stripped.empty? || stripped.start_with?('#')
		key, value = stripped.split('=', 2)   # limit 2: values may contain '='
		return nil if value.nil?
		[key.strip, value.strip]
	end

	def fill_updater_config
		if File.exist?(Config::CONFIG_FILE)
			config = {}
			File.foreach(Config::CONFIG_FILE) do |line|
				key, value = parse_config_line(line)
				next if key.nil?
				if Config::TRUE_VALUES.include?(value.downcase)
					config[key] = true
				elsif Config::FALSE_VALUES.include?(value.downcase)
					config[key] = false
				else
					config[key] = value
				end
			end
			Config.poke_updater_config = config
		end

		return if !File.exist?(Config::LOCALES_FILE)
		begin
			Config.poke_updater_locales = HTTPLite::JSON.parse(File.read(Config::LOCALES_FILE))
		rescue StandardError => e
			puts "PokeUpdater: could not parse #{Config::LOCALES_FILE}: #{e.message}"
		end
	end

	def config_ready?(from_update_button = false)
		fill_updater_config if Config.poke_updater_config.nil? || Config.poke_updater_config['PASTEBIN_URL'].nil?
		url = Config.poke_updater_config && Config.poke_updater_config['PASTEBIN_URL']
		return true if url && !url.to_s.strip.empty?
		pbMessage(get_poke_updater_text('NO_PASTEBIN_URL')) if from_update_button
		false
	end

	def get_lang
		System.user_language[0..1]
	end

	def get_poke_updater_text(text_name, variable = nil)
		localized = Config.poke_updater_locales &&
		            Config.poke_updater_locales[text_name] &&
		            Config.poke_updater_locales[text_name][get_lang]
		text = (localized.nil? || localized.empty?) ? DEFAULT_TEXTS[text_name] : localized
		return nil if text.nil?
		text.sub('#{variable}', variable.to_s)   # sub returns a copy: never mutates the cached locale
	end

	def validate_game_version(from_update_button = false)
		return if !config_ready?(from_update_button)
		return if !network_available?
		validate_version(Config.poke_updater_config['PASTEBIN_URL'], from_update_button)
	end
	# Kept for backwards compatibility with games calling the old name.
	def validate_game_version_and_update(from_update_button = false)
		validate_game_version(from_update_button)
	end

	def check_for_updates(from_update_button = false)
		return if $DEBUG
		return if !network_available?
		validate_game_version(from_update_button)
	end

	def new_version?(new_version, current_version)
		return false if new_version.nil? || current_version.nil?
		return false if new_version.to_s.strip.empty? || current_version.to_s.strip.empty?
		return false if new_version == current_version

		begin
			new_parts = parse_version_parts(new_version)
			current_parts = parse_version_parts(current_version)

			version_comparison = compare_version_numbers(new_parts[:numbers], current_parts[:numbers])
			return version_comparison > 0 if version_comparison != 0

			compare_prerelease(new_parts[:prerelease], current_parts[:prerelease]) > 0
		rescue StandardError => e
			puts "Error comparing versions '#{new_version}' and '#{current_version}': #{e.message}"
			false
		end
	end

	# Parse version string into numbers and pre-release identifier
	def parse_version_parts(version_string)
		if version_string =~ /^(\d+(?:\.\d+)*)(.*)$/
			numbers_part = $1
			prerelease_part = $2.strip

			numbers = numbers_part.split('.').map(&:to_i)
			prerelease = prerelease_part.empty? ? nil : prerelease_part.downcase.gsub(/^[.-]/, '')

			{ numbers: numbers, prerelease: prerelease }
		else
			{ numbers: [0], prerelease: version_string.downcase }
		end
	end

	# Compare two arrays of version numbers
	def compare_version_numbers(new_nums, current_nums)
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

		return 1 if new_pre.nil? && !current_pre.nil?
		return -1 if !new_pre.nil? && current_pre.nil?

		pre_order = { 'alpha' => 1, 'beta' => 2, 'rc' => 3 }

		new_order = pre_order[new_pre] || 0
		current_order = pre_order[current_pre] || 0

		new_order <=> current_order
	end

	# Reads the remote manifest. Returns a hash with the recognised keys.
	# CHANGELOG may span several lines: everything until the next recognised key.
	def parse_remote_manifest(data)
		result = { 'FORCE_UPDATE' => false }
		lines = data.split("\n")
		i = 0
		while i < lines.length
			key, value = parse_config_line(lines[i])
			i += 1
			next if key.nil? || !REMOTE_KEYS.include?(key)

			if key == 'CHANGELOG'
				changelog_lines = [value]
				while i < lines.length
					peek_key, _peek_value = parse_config_line(lines[i])
					break if peek_key && REMOTE_KEYS.include?(peek_key)
					break if lines[i].strip.empty?
					changelog_lines << lines[i]
					i += 1
				end
				result['CHANGELOG'] = changelog_lines.join("\n").strip
			elsif key == 'FORCE_UPDATE'
				result['FORCE_UPDATE'] = Config::TRUE_VALUES.include?(value.downcase)
			else
				result[key] = value
			end
		end
		result
	end

	# Tells the player to download the game by hand, and opens the link if they agree.
	def prompt_manual_download
		link = Config.poke_updater_config['MANUAL_DOWNLOAD_LINK'].to_s
		pbMessage(get_poke_updater_text('MANUAL_UPDATE', link))
		return if link.empty?
		return if !pbConfirmMessage(get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM'))
		System.launch(link)
	end

	# UPDATER_FILENAME names the binary without extension (./poke_updater/poke_updater).
	# Windows adds .exe; mac and Linux use the name as is. Configs that still carry
	# the .exe keep working.
	#
	# is_windows? and NOT is_really_windows?: under Wine/Proton the game is a Windows
	# process, so it has to spawn the .exe; it could not exec a native binary anyway.
	def updater_path
		updater = Config.poke_updater_config['UPDATER_FILENAME'].to_s
		return updater if updater.empty?
		updater = updater.sub(/\.exe\z/i, '')
		System.is_windows? ? "#{updater}.exe" : updater
	end

	# Runs the updater binary. On Windows the path from the config is enough; mac and
	# Linux need it absolute, and the executable bit is routinely lost when unzipping.
	#
	# IO.popen([path]): the array form execs the file directly. Given a plain string,
	# Ruby splits it on spaces, so a game folder like "LA BASE DE SKY" would try to
	# run ".../GitHub/LA" and die with ENOENT.
	def launch_updater(updater)
		# 2-element array [exe, argv0] forces no-shell execvp across all Ruby impls;
		# single-element arrays can still be shell-tokenized on some runtimes,
		# truncating paths at the first space (e.g. ".../GitHub/LA" from "LA BASE DE SKY").
		return IO.popen([updater, updater]) if System.is_windows?
		path = File.expand_path(updater)
		File.chmod(0755, path) if !File.executable?(path)
		IO.popen([path, path])
	end

	def validate_version(url, from_update_button = false, update = true)
		begin
			data = pbDownloadToString(url)
		rescue MKXPError, StandardError => e
			puts "PokeUpdater: download failed: #{e.message}" if $DEBUG_LOG
			pbMessage(get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET')) if from_update_button
			return
		end

		if data.nil? || data.empty?
			pbMessage(get_poke_updater_text('NO_NEW_VERSION_OR_INTERNET')) if from_update_button
			return
		end
		return if Config.poke_updater_config.nil?

		manifest = parse_remote_manifest(data)
		new_version = manifest['GAME_VERSION']
		force_update = manifest['FORCE_UPDATE']
		download_url = manifest['DOWNLOAD_URL']
		changelog = manifest['CHANGELOG']
		current_version = Config.poke_updater_config['CURRENT_GAME_VERSION']

		if new_version.nil? || new_version.empty? || !new_version?(new_version, current_version)
			if from_update_button
				pbMessage(get_poke_updater_text('CURRENT_VERSION', current_version))
				pbMessage(get_poke_updater_text('NO_NEW_VERSION'))
			end
			return
		end

		pbMessage(get_poke_updater_text('NEW_VERSION', new_version))
		if !changelog.to_s.empty? && pbConfirmMessage(get_poke_updater_text('ASK_FOR_CHANGELOG'))
			pbMessage("Changelog:\n#{changelog}")
		end

		if $joiplay
			pbMessage(get_poke_updater_text('JOIPLAY_UPDATE'))
			if download_url && pbConfirmMessage(get_poke_updater_text('MANUAL_DOWNLOAD_CONFIRM'))
				begin
					MKXP.launch(download_url) # Joiplay
				rescue MKXPError, NoMethodError, NameError
					puts "Incompatible Joiplay version detected." if $DEBUG_LOG
				end
			end
			return
		end

		if !pbConfirmMessage(get_poke_updater_text('ASK_FOR_UPDATE'))
			return if !force_update
			pbMessage(get_poke_updater_text('FORCE_UPDATE_ON'))
			Kernel.exit!
		end

		updater = updater_path
		if updater.empty? || !File.exist?(updater)
			prompt_manual_download
			return
		end

		# Check-only mode: point the player at the in-menu update button instead of updating now.
		if !force_update && !update
			if Config.poke_updater_config['HAS_UPDATE_BUTTON']
				pbMessage(get_poke_updater_text('BUTTON_UPDATE'))
			else
				prompt_manual_download
			end
			return
		end

		pbMessage(get_poke_updater_text('UPDATE'))
		launch_updater(updater)
		Kernel.exit!
	end
end

unless defined?(network_available?)
	def network_available?(retries: 3, delay: 0.5)
		retries.times do
			begin
			response = HTTPLite.get("http://httpbin.org/status/200")
			return true if response && response.fetch(:status) == 200
			rescue StandardError, MKXPError
			return false
			end
			pbWait(delay) if retries > 1
		end
		false
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
