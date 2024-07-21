[![es](https://img.shields.io/badge/Idioma-Español-yellow.svg)](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/blob/main/readme/README_19+_es.md)

---

**You can now download the files for the latest [release](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/releases/latest)!**

Pokémon Essentials Game Updater (PokéUpdater) is a lightweight interface developed in Python with the aim to provide a seamless transition for players to newer version of the game without requiring any manual steps. Current release supports over 20 languages and file hosting / downloading from MEGA, Mediafire, Dropbox or Google Drive.

**Joiplay support for game updating is not planned. Version checking is now supported as of Pokémon Essentials v19.**

![gif preview](/previews/preview_en.gif)

#### Big thanks to [@Eric_Lostie](https://twitter.com/Eric_Lostie) on twitter for allowing us to use his game, Pokémon Añil, as an example for this project

# Implementation

## Quick start

1. Download file `PokeUpdater_x.x.x_PE19+.zip` from the [latest release](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/releases/latest).
2. Extract files `pu_locales` and `pu_config` and the folders `Plugins` and `poke_updater` to the game directory.
3. Add the code for the version check as specified in the [Maintaining your RPG Maker XP Scripts](#maintaining-your-rpg-maker-xp-scripts) section.
4. Log in to [http://pastebin.com](http://pastebin.com/).
5. Create a new Pastebin file with the format specified in section [Set up and maintain the Pastebin file](#set-up-and-maintain-the-pastebin-file) and retrieve its RAW URL.
6. Edit file `pu_config` with notepad, and set the correct values for variables `CURRENT_GAME_VERSION` and `VERSION_PASTEBIN`.

## Maintaining your RPG Maker XP scripts

The PokéUpdater consists of one Ruby plugin named `PokemonEssentialsGameUpdater` which must be added to the `Plugins` folder in the game directory:

- `GameVersion.rb`, which contains the implementations of the required methods for reading a configuration file, validating game versions and downloading a new version.

For the game to check if there are new updates at the loading screen you have to add the following line at the top of the `pbStartLoadScreen` method in the `UI_Load` script under the `UI` section:

```ruby
pbCheckForUpdates()
```

If it is needed that the version is validated at any other point in your game, you can add this `pbCheckForUpdates()` call where required.

### Optional code snippets

#### Having a dedicated version check / game update button

It is possible to add a dedicated button to the load screen to check for updates. To do this, you will need to add the following code to the `pbStartLoadScreen` method in the `UI_Load` script:

- Where the commands are declared with the nomenclature `cmd_something` (for example `cmdNewGame`), after the `commands = []` line add the following:

```ruby
cmd_update     = -1
```

- Where the menu buttons are created with the nomenclature `commands[cmd_something=commands.length]=_INTL("My Something Description")` (for example, `commands[cmd_new_game=commands.length]=_INTL("New Game")`) the following line must be added:

```ruby
commands[cmd_update=commands.length]=_INTL("Check for Updates")
```

Please note that the line in which you add your button is important, as the buttons will be displayed in the same order as they are added. If you want your button to be displayed at the end of the menu, it will need to be added last.

The full `pbStartLoadScreen` method should look like this:

```ruby
  def pbStartLoadScreen
    # PokeUpdater Code
    pbCheckForUpdates()
    # End of PokeUpdater Code
    commands = []
    cmd_continue     = -1
    cmd_new_game     = -1
    cmd_options      = -1
    cmd_language     = -1
    cmd_mystery_gift = -1
    cmd_debug        = -1
    cmd_quit         = -1
    # PokeUpdater Code
    cmd_update       = -1
    # End of PokeUpdater Code

    . . .

    commands[cmd_new_game = commands.length]  = _INTL('New Game')
    commands[cmd_options = commands.length]   = _INTL('Options')
    commands[cmd_language = commands.length]  = _INTL('Language') if Settings::LANGUAGES.length >= 2
    commands[cmd_debug = commands.length]     = _INTL('Debug') if $DEBUG
    # PokeUpdater Code
    commands[cmd_update=commands.length]=_INTL("Check for Updates")
    # End of PokeUpdater Code
    commands[cmd_quit = commands.length]      = _INTL('Quit Game')

    . . .

    loop do
      command = @scene.pbChoose(commands)
      pbPlayDecisionSE if command != cmd_quit
      case command
      when cmd_continue
        . . .
      when cmd_new_game
        . . .
      when cmd_mystery_gift
        pbFadeOutIn { pbDownloadMysteryGift(@save_data[:player]) }
      when cmd_options
        . . .
      when cmd_language
        . . .
      when cmd_debug
        . . .
      # PokeUpdater Code
      when cmd_update
        pbValidateGameVersionAndUpdate(true)
      # End of PokeUpdater Code
      when cmd_quit
        . . .
      else
        pbPlayBuzzerSE
      end
    end
  end
```

## Set up and maintain the Pastebin file

When the scripts have been implemented in your RPG Maker XP project, you will need to set up a new Pastebin file. To do this, you will need to set up an account in https://pastebin.com (this is required to update your Pastebin in the future!).

While logged in you will need to create a new file with the following format:

```
GAME_VERSION=
DOWNLOAD_URL=
```

The DOWNLOAD_URL field can be repeated N times to have multiple download hosts, but there can only be one DOWNLOAD_URL for each host. The player will be able to choose which host to download the game from.


<br>
See below for an explanation on each of the variables:<br><br>

| Variable       | Description                                                                                                                                                                               | Accepted values                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `GAME_VERSION` | Latest game version. Should coincide with the configuration file's `CURRENT_GAME_VERSION` when releasing a new version (see [Releasing a new game update](#releasing-a-new-game-update)). | Any version number in format x.x (e.g. `1.0`, `2.5`, `23.03`, `23.10`).                       |
| `DOWNLOAD_URL` | URL for the downloadable ZIP with the game files.                                                                                                                                         | Any URL for a downloadable file. Accepted hosting sites are MEGA, Mediafire and Dropbox. |

When created, a URL for this Pastebin will be generated. You will need the RAW format URL for the Pastebin. This can be retrieved by clicking on the `raw` button above the first line of your newly generated file.

## Set up and maintain the configuration file

After creating and configuring your Pastebin file, copy the provided `pu_config` file into your project folder. Note both `pu_config` and `pu_locales` are both text files even if they have no extension. The extension has been purposefully removed to discourage users from modifying values. This means that `pu_config` must be opened in a notepad. This file contains the following format:

```
CURRENT_GAME_VERSION=1.0
VERSION_PASTEBIN=
UPDATER_FILENAME=./poke_updater/poke_updater.exe
FORCE_VERSION_CHECK=true
FORCE_UPDATE=true
```

<br>
See below for an explanation on each of the variables:<br><br>

| Variable               | Description                                                                                                                                               | Accepted values                                                                                      | Default value      |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------ |
| `CURRENT_GAME_VERSION` | Game's current version. When validating if an update is available, this variable will be checked against the `GAME_VERSION` set up in your Pastebin file. | Any version number in format x.x (e.g.: `1.0`, `2.5`, `23.10`, etc.).                                | `1.0`              |
| `VERSION_PASTEBIN`     | The URL to your raw Pastebin file. This will be the URL from where the new version details will be validated.                                             | A **RAW** Pastebin URL. If a non RAW Pastebin URL is passed, values will not be properly determined. | Empty              |
| `UPDATER_FILENAME`     | The PokéUpdater executable name. It doesn't need to be changed, but if it is, then it must be maintained in this variable.                                | Any valid filename                                                                                   | `./poke_updater/poke_updater.exe` |
| `FORCE_VERSION_CHECK`  | Flag to forcibly validate if a new version is available based on Pastebin data on game launch.                                                            | Upper or lower case:<br>`true`/`y`/`si`/`yes`/`s`<br>`false`/`n`/`no`                                | `true`             |
| `FORCE_UPDATE`         | If this flag is sent to true and the user chooses not to update the game when prompted the a message will be shown informing that the update is requiered and the game will close.     | Upper or lower case:<br>`true`/`y`/`si`/`yes`/`s`<br>`false`/`n`/`no`                                | `false`             |

After setting the required values for all variables, the file does not need to be changed unless a new version is released.

## Releasing a new game update

If you have followed the previous steps, and have bundled the `poke_updater.exe` and `pu_config` with your newly released game, congratulations! The updater is now ready to be used in the first version that includes it.

When a new version is to be released, some of the values will need to be maintained for the updater to recognize a new release:

- In the `pu_config` of your new release, the `CURRENT_GAME_VERSION` variable will need to be set to the new version number.
- In your Pastebin file, the `GAME_VERSION` variable should be set to the same version as the new `CURRENT_GAME_VERSION` value.
- The `DOWNLOAD_URL` variable should also be updated to the new download URL after uploading it to a supported host.

If maintained properly, games which are running on an older version of your game and which already has the required files will retrieve the game from your `DOWNLOAD_URL` when their older `CURRENT_GAME_VERSION` does not match the newer `GAME_VERSION`.

## Language support

Currently those languages listed below are supported. Translation to other languages may be done in the future, but is not currently planned. To allow script translation, do not forget to copy the `locales` file to your game directory.

| Language             | Included in the executable? | Included in scripts? |
| -------------------- | --------------------------- | -------------------- |
| English              | ✔️                          | ✔️                   |
| Spanish              | ✔️                          | ✔️                   |
| French               | ✔️                          | ✔️                   |
| Portuguese           | ✔️                          | ❌                   |
| Italian              | ✔️                          | ✔️                   |
| German               | ✔️                          | ✔️                   |
| Russian              | ✔️                          | ❌                   |
| Japanese             | ✔️                          | ✔️                   |
| Chinese (simplified) | ✔️                          | ❌                   |
| Korean               | ✔️                          | ✔️                   |
| Arabic               | ✔️                          | ❌                   |
| Turkish              | ✔️                          | ❌                   |
| Polish               | ✔️                          | ❌                   |
| Dutch                | ✔️                          | ❌                   |
| Swedish              | ✔️                          | ❌                   |
| Danish               | ✔️                          | ❌                   |
| Finnish              | ✔️                          | ❌                   |
| Norwegian            | ✔️                          | ❌                   |
| Czech                | ✔️                          | ❌                   |
| Hungarian            | ✔️                          | ❌                   |
| Greek                | ✔️                          | ❌                   |
| Hebrew               | ✔️                          | ❌                   |

_Want to help translate PokéUpdater into your language or notify us about an error in translation? Let us know by [opening an issue](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=bug-report-english.md&title=%5BBUG%5D)!_

## FAQ

#### Q. Which RPG Maker versions do the scripts support?

A. The updater is thought to only be used in RPG Maker XP

#### Q. Which Pokémon Essentials does the updater support?

A. The updater was developed and tested for essentials 16.2 and 21.1 but it should work in any version higher than 16.2. If this is not the case, please report this [through an issue](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=bug-report-english.md&title=%5BBUG%5D).

#### Q. Is Python required to be installed to run the updater?

A. No. The executable is thought to be used by an end user with no extra input on their end. For this reason, the updater is provided as a bundled executable instead of anything else.

#### Q. A user is reporting that they cannot download the game file or that their download is unusually slow, what's going on?

A. MEGA and Mediafire both have a limited transfer quota that can be freely used. After this quota has been consumed, MEGA will not allow any download to continue and Mediafire will reduce the download speed significantly. This is something which we cannot circumvent. The user will need to wait for their download quota to become available again or if you have added multiple download hosts to the pastebin they could try a different host.

#### Q. A user from <INSERT COUNTRY HERE\> cannot access my game file through the host page because of regional restrictions. Can they update the game using the PokéUpdater anyway?

A. The PokéUpdater cannot bypass any regional / content restrictions set by the hosts. By the same measure, it will also not be possible to retrieve private or password protected files.

#### Q. Will my released updates be optional / mandatory?

A. If the scripts have been implemented as specified in the [Maintaining your RPG Maker XP Scripts](#maintaining-your-rpg-maker-xp-scripts) section, it is possible to control whether the version checking / updating will be forcibly done when showing the game load screen by setting the parameters `FORCE_VERSION_CHECK` and `FORCE_UPDATE` of the `pu_config` file. Note that if `FORCE_UPDATE` is set to a `false` value, then the update logic will have to be called somewhere else, for example, a menu button as exemplified in section [Optional code snippets](#optional-code-snippets). Also note that setting `FORCE_VERSION_CHECK` to a `false` value will deactivate the PokéUpdater unless the version validation is performed elsewhere.

#### Q. I don't want to use the PokéUpdater executable, but I still want to notify my users that a new version has been released. Is it possible to do this with the provided scripts?

A. Yes! By setting variable `FORCE_VERSION_CHECK` to a `true` value and `FORCE_UPDATE` to a `false` value and keeping the Pastebin file up to date, the game will raise a message notifying the user that a new version is available but the updater executable will not be run. If this is the only feature required, then it is not mandatory to download and copy the `poke_updater` folder alongside your game.

#### Q. The in-game messages are being displayed in Spanish, are there no translations available?

A. This is probably caused by not having the provided `pu_locales` file in your folder. If file `pu_locales` is missing in the game directory, all messages will be fixed to spanish ones which are found in method `pbGetPokeUpdaterText` of class `GameVersion.rb`. Please note that only those languages supported by Pokémon Essentials 16.2 are taken into account. Existing translations can be modified by updating the locales `pu_locales`.

#### Q. Will user saves be affected by the update process?

A. No. The update process works inside the game folder and will NOT affect any other file in the user's computer. As saves are saved under `C:/Users/USERNAME/AppData/Roaming/GAME_NAME`.

#### Q. My antivirus software detects file `poke_updater.exe` as a potential virus, why is that?

_~~A. As the updater executable is being compiled by using library pyInstaller, antivirus software like Windows Defender automatically detect it as a potential virus. The `poke_updater.exe` file does not contain any kind of malicious code and we are currently working to find a way that it is not detected so. As we want to be as transparent as possible on how the updater works, we have also made the source code for the `poke_updater.exe` available.~~_

A. Starting with release 1.1.0 we have changed the way the executable is being compiled, which should no longer trigger this false positive. If that is not the case, please raise an [issue](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=bug-report-english.md&title=%5BBUG%5D) for us to look further into it.

#### Q. Will you make the source code for the updater available?

_~~A. This is not planned at the moment. If a feature that you require is missing, you can [raise a feature request](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=feature-request-english.md&title=%5BFEATURE+REQUEST%5D). In the future we may make the source code available but this is not a priority at the moment.~~_

A. Yes, with release 1.1.0, the source code has been made available and can be found [here](/poke_updater_source_code/).
