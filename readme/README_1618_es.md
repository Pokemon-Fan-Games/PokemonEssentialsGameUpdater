[![en](https://img.shields.io/badge/Language-English-red.svg)](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/blob/main/readme/README_1618_en.md)

---

**¡Ahora puedes descargar los archivos de la última [versión](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/releases/latest)!**

Pokémon Essentials Game Updater (PokéUpdater) es una interfaz liviana desarrollada en Python con el objetivo de proporcionar una transición sin problemas para jugadores a una versión más reciente del juego sin requerir pasos manuales. La versión actual de PokéUpdater es compatible con más de 20 idiomas y permite descargar desde MEGA, Mediafire, Dropbox o Google Drive.

**Por limitaciones técnicas de versiones de Pokémon Essentials previas a V19, no está previsto el soporte para Joiplay.**

![](/previews/preview.gif)

#### Muchas gracias a [@Eric_Lostie](https://twitter.com/Eric_Lostie) en Twitter por permitirnos usar su juego, Pokémon Añil, como ejemplo para este proyecto.

# Implementación

## Guía rápida

1. Descargar el archivo `PokeUpdater_1.1.5_PE16-18.zip` del [último release](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/releases/latest).
2. Extraer los archivos `pu_locales`, `pu_config` y la carpeta `poke_updater` al directorio del juego.
3. Copiar los scripts `VersionCheck.rb` y `GameVersion.rb` junto con el resto de los scripts del juego, antes del script llamado `Main`.
4. Agregar el llamado al control de versiones como se indica en la sección [Mantenimiento de tus scripts de RPG Maker XP](#mantenimiento-de-tus-scripts-de-rpg-maker-xp).
5. Iniciar sesión en http://pastebin.com.
6. Crear un nuevo archivo de Pastebin con el formato indicado en la sección [Configuración y mantenimiento del archivo de Pastebin](#configuración-y-mantenimiento-del-archivo-de-pastebin) y conseguir la URL RAW del mismo.
7. Editar el archivo `pu_config` en un bloc de notas, y colocar el valor correcto a las variables `CURRENT_GAME_VERSION` y `VERSION_PASTEBIN`.

Los usuarios podrán hacer uso del PokéUpdater una vez hayan descargado una versión que incluya los archivos del mismo ya configurados. Para cada release por favor recordar actualizar la variable `CURRENT_GAME_VERSION` a el nuevo número de versión antes de subir el archivo para la descarga y de actualizar ambas variables del Pastebin colocando el mismo número de versión a la variable `GAME_VERSION` y la nueva URL de descarga a la variable `DOWNLOAD_URL`.
<br>
Para más detalle de cada paso, por favor hacer referencia a la sección correspondiente debajo.

## Mantenimiento de tus scripts de RPG Maker XP

El PokéUpdater consiste principalmente de dos scripts de Ruby que deben ser agregados junto al resto de los scripts del juego antes del script llamado "Main":

- `GameVersion.rb`, el cual contiene la implementación de los tres métodos requeridos para leer el archivo de configuración, validar versiones del juego y actualizarlo; y
- `VersionCheck.rb`, el cual contiene la implementación del método que valida si la `GAME_VERSION` detallada en el RAW del archivo de Pastebin es mayor que la `CURRENT_GAME_VERSION` del `pu_config.txt` . Si la variable `FORCE_UPDATE` se ha colocado a un valor `verdadero` o si este método se ha llamado desde otro lugar de los scripts del juego con el parámetro `update=true`, se ejecutará el archivo `poke_updater.exe` luego de cerrarse para actualizar el juego.

Para que el juego valide si hay nuevas actualizaciones en la pantalla de carga, se debe agregar la siguiente línea al principio del método `pbStartLoadScreen` en el script `PScreen_Load`:

```ruby
pbCheckForUpdates()
```

De ser necesario validar la versión del juego en cualquier otro punto del juego, es posible agregar este llamado al método `pbCheckForUpdates()` donde sea requerido.

### Extractos de código opcionales

#### Agregar un botón dedicado para validar versiones / actualizar el juego

Es posible agregar un botón dedicado a la pantalla de carga para validar actualizaciones. Para hacer esto, se debe agregar el siguiente código al método `pbStartLoadScreen` del script `PScreen_Load`:

- Donde los comandos se declaran con la nomenclatura `cmdAlgo` (por ejemplo `cmdNewGame`), antes de la línea `commands = []`, se agrega lo siguiente:

```ruby
cmdUpdate     = -1
```

- Donde los botones se declaran con la nomenclatura `commands[cmdAlgo=commands.length]=_INTL("Mi Descripción de Algo")` (por ejemplo, `commands[cmdNewGame=commands.length]=_INTL("Nuevo Juego")`) la siguiente línea debe ser agregada:

```ruby
commands[cmdUpdate=commands.length]=_INTL("Comprobar nuevas versiones") if !$joiplay
```

Por favor tener en cuenta que el extracto `if !$joiplay` es necesario para no mostrar este botón a usuarios de Joiplay, ya que el PokéUpdater no lo soporta e intentar correrlo resultará en el juego congelándose. También tener en cuenta que la línea en la cuál se agrega el botón también es importante, ya que los botones serán mostados en el mismo orden en el que son declarados. Si se quiere que el nuevo botón sea mostrado al final del menú, se debe agregar su declaración como última.

El extracto `if else` debería verse similar a lo siguiente:

```ruby
def pbStartLoadScreen(savenum=0,auto=nil,savename="Partida 1")
    # PokeUpdater Code
    pbCheckForUpdates()
    # End of PokeUpdater Code

    $PokemonTemp  = PokemonTemp.new
    $game_temp    = Game_Temp.new
    $game_system  = Game_System.new
    $PokemonSystem = PokemonSystem.new if !$PokemonSystem
    cmdContinue    = -1
    cmdNewGame    = -1
    cmdChooseSaveFile =-1
    cmdOption      = -1
    cmdLanguage    = -1
    cmdMysteryGift = -1
    cmdDeleteSaveFile =-1
    # PokeUpdater Code
    cmdUpdate      = -1
    # End of PokeUpdater Code
    commands      = []

    . . .
      commands[cmdContinue=commands.length]=_INTL("Continuar") if showContinue
      commands[cmdNewGame=commands.length]=_INTL("Nuevo juego")
      commands[cmdChooseSaveFile=commands.length]=_INTL("Otras partidas")
      commands[cmdDeleteSaveFile=commands.length]=_INTL("Borrar esta partida")
      commands[cmdMysteryGift=commands.length]=_INTL("Regalo Misterioso") if (trainer.mysterygiftaccess rescue false)
      commands[cmdOption=commands.length]=_INTL("Opciones")
    else
      commands[cmdNewGame=commands.length]=_INTL("Nuevo juego")
      commands[cmdChooseSaveFile=commands.length]=_INTL("Otras partidas")
      commands[cmdOption=commands.length]=_INTL("Opciones")
    end
    # PokeUpdater Code
    commands[cmdUpdate=commands.length]=_INTL("Comprobar nuevas versiones") if !$joiplay
    # End of PokeUpdater Code

    . . .

      if cmdDeleteSaveFile>=0 && command==cmdDeleteSaveFile
        . . .
      elsif cmdNewGame>=0 && command==cmdNewGame
        . . .
      elsif cmdMysteryGift>=0 && command==cmdMysteryGift
        . . .
      elsif cmdChooseSaveFile>=0 &&  command==cmdChooseSaveFile
        . . .
      elsif cmdOption>=0 && command==cmdOption
        . . .
      elsif cmdLanguage>=0 && command==cmdLanguage
        . . .
      # PokeUpdater Code
      elsif cmdUpdate>=0 && command==cmdUpdate && GameVersion::POKE_UPDATER_CONFIG
        pbValidateGameVersionAndUpdate(true)
      end
      # End of PokeUpdater Code
    end
    @scene.pbEndScene
    return
  end
```

## Configuración y mantenimiento del archivo de Pastebin

Cuando los scripts hayan sido implementados en el projecto de RPG Maker XP, será necesario configurar un nuevo archivo de Pastebin. Para hacer esto, es necesario crear una cuenta en https://pastebin.com (¡esto es necesario para actualizar el archivo en el futuro!).

Con la sesión iniciada, se debe crear un nuevo archivo con el siguiente formato:

```
GAME_VERSION=
DOWNLOAD_URL=
```

<br>
Ver debajo para una explicación de cada variable:<br><br>

| Variable       | Descripción                                                                                                                                                                                        | Valores aceptados                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `GAME_VERSION` | Última versión del juego. Debe coincidir con el `CURRENT_GAME_VERSION` del archivo de configuración al lanzar una nueva versión (ver [Al lanzar una nueva versión](#al-lanzar-una-nueva-versión)). | Cualquier número de versión con el formato x.x (por ejemplo: `1.0`, `2.5`, `23.03`, `23.10`).                |
| `DOWNLOAD_URL` | La URL con la cual se descarga el juego.                                                                                                                                                           | Cualquier URL a un archivo descargable. Los sitios de descarga aceptados son MEGA, Mediafire y Google Drive. |

Una vez creado, una URL para este archivo de Pastebin será generada. Se necesitará la URL al formato RAW para el archivo de Pastebin. Para conseguirla, se debe hacer click en el botón que dice `raw` arriba de la primera línea del nuevo archivo generado.

## Configuración y mantenimiento del archivo de configuración

Luego de crear y configurar el archivo de Pastebin, se debe copiar el archivo `pu_config` provisto, a la carpeta del proyecto. Tener en cuenta que `pu_config` y `pu_locales` son ambos archivos de texto incluso aunque no tengan una extensión. La extensión ha sido borrada intencionalmente con el objetivo de desincentivar a los jugadores de hacer cambios en los valores. Esto significa que `pu_config` debe ser abierto en un bloc de notas. Este archivo contiene el siguiente formato:

```
CURRENT_GAME_VERSION=1.0
VERSION_PASTEBIN=
UPDATER_FILENAME=./poke_updater/poke_updater.exe
FORCE_VERSION_CHECK=true
FORCE_UPDATE=true
```

<br>
Ver debajo para una explicación de cada variable:<br><br>

| Variable               | Descripción                                                                                                                                                                   | Valores aceptados                                                                                                                                      | Default value      |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| `CURRENT_GAME_VERSION` | La versión actual del juego. Cuando se valide si hay una nueva versión disponible, esta variable se comparará contra la `GAME_VERSION` configurada en el archivo de Pastebin. | Cualquier número de versión con el formato x.x (por ejemplo: `1.0`, `2.5`, `23.10`, etc.).                                                             | `1.0`              |
| `VERSION_PASTEBIN`     | La URL al formato RAW del archivo de Pastebin. Esta será la URL con la cual los detalles de la nueva versión serán validados.                                                 | Una URL a un formato **RAW** de un archivo de Pastebin. Si se provee una URL de Pastebin no RAW, los valores no podrán ser determinados correctamente. | Empty              |
| `UPDATER_FILENAME`     | El nombre del ejecutable del PokéUpdater. No necesita ser cambiado, pero si se cambia también debe ser mantenido en esta variable.                                            | Cualquier nombre de archivo válido que corresponda con el nombre del ejecutable.                                                                       | `./poke_updater/poke_updater.exe` |
| `FORCE_VERSION_CHECK`  | Booleano para validar obligatoriamente si una nueva versión está disponible basada en la información configurada en el archivo de Pastebin al iniciar el juego.               | Mayúscula o minúscula:<br>`true`/`y`/`si`/`yes`/`s`<br>`false`/`n`/`no`                                                                                | `true`             |
| `FORCE_UPDATE`         | Bolleano para descargar obligatoriamente y actualizar la nueva versión usando la URL indicada en el archivo de Pastebin.                                                      | Mayúscula o minúscula:<br>`true`/`y`/`si`/`yes`/`s`<br>`false`/`n`/`no`                                                                                | `true`             |

Luego de poner los valores requeridos a todas las variables, no es necesario modificar el archivo a menos que una nueva versión sea lanzada.

## Al lanzar una nueva versión

Si se han seguido los pasos anteriores, y se han agregados los archivos `poke_updater.exe` y `pu_config` al juego, ¡felicitaciones! El actualizador ya está listo para ser usado en la primera versión que lo incluya.

Cuando una nueva versión esté por ser lanzada, algunos de los valores deberán ser mantenidos para que el actualizador reconozca una nueva versión:

- En el `pu_config` de la nueva versión, la variable `CURRENT_GAME_VERSION` deberá cambiarse al nuevo número de versión.
- En el archivo de Pastebin, la variable `GAME_VERSION` deberá cambiarse al mismo número que el nuevo valor de la variable `CURRENT_GAME_VERSION`.
- La variable `DOWNLOAD_URL` deberá actualizarse a la nueva URL de descarga luego de subirla a un sitio de descargas soportado.

Si se mantiene correctamente, aquellos juegos que estén corriendo en una versión más vieja y que ya contengan los archivos requeridos, irán a buscar la nueva versión del juego al `DOWNLOAD_URL` cuando la `CURRENT_GAME_VERSION` del juego más viejo no sea igual a la nueva `GAME_VERSION`.

## Idiomas soportados

Actualmente aquellos idiomas listados debajo están soportados. La traducción a otros idiomas puede ser hecha en un futuro, pero no está actualmente planeada. Para permitir traducciones de los scripts, no olvidar copiar el archivo `locales` al directorio del juego.

| Idioma               | ¿Incluído en el ejecutable? | ¿Incluído en los scripts? |
| -------------------- | --------------------------- | ------------------------- |
| Inglés               | ✔️                          | ✔️                        |
| Español              | ✔️                          | ✔️                        |
| Francés              | ✔️                          | ✔️                        |
| Portugués            | ✔️                          | ❌                        |
| Italiano             | ✔️                          | ✔️                        |
| Alemán               | ✔️                          | ✔️                        |
| Ruso                 | ✔️                          | ❌                        |
| Japonés              | ✔️                          | ✔️                        |
| Chino (simplificado) | ✔️                          | ❌                        |
| Coreano              | ✔️                          | ✔️                        |
| Árabe                | ✔️                          | ❌                        |
| Turco                | ✔️                          | ❌                        |
| Polaco               | ✔️                          | ❌                        |
| Holandés             | ✔️                          | ❌                        |
| Suizo                | ✔️                          | ❌                        |
| Danés                | ✔️                          | ❌                        |
| Finlandés            | ✔️                          | ❌                        |
| Noruego              | ✔️                          | ❌                        |
| Checo                | ✔️                          | ❌                        |
| Húngaro              | ✔️                          | ❌                        |
| Griego               | ✔️                          | ❌                        |
| Hebreo               | ✔️                          | ❌                        |

_¿Quieres ayudar a traducir PokéUpdater a tu idioma o notificarnos de un error en la traducción? ¡Háznolo saber creando un [reporte de bug](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=reporte-de-error.md&title=%5BBUG%5D)!_

## Preguntas frecuentes

#### P. ¿Qué versiones de RPG Maker son soportadas por los scripts?

R. El actualizador está pensado para ser usado únicamente con RPG Maker XP.

#### P. ¿Qué versiones de Pokémon Essentials son soportadas por los scripts?

R. A pesar de que el actualizador ha sido desarrollado y probado en PokéEssentials versión 16.2, es probable que esto sea un absoluto mínimo y que cualquier otra nueva versión sea también soportada. De no ser este el caso, por favor reportarlo a través de un [reporte de bug](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=reporte-de-error.md&title=%5BBUG%5D).

#### P. ¿Es necesario instalar Python para correr el actualizador?

R. No. El ejecutable está pensado para ser usado por un usuario final sin entrada extra por su parte. Por esta razón, el actualizador es provisto como un ejecutable en vez de cualquier otra cosa.

#### P. Un usuario reporta que no pueden descargar el archivo de juego o que su descarga es inusualmente lenta, ¿qué está pasando?

R. MEGA y Mediafire ambos tienen un límite en la cuota de transferencia que puede ser libremente utilizada. Al ser consumida la cuota, MEGA no permitirá que una descarga continúe y Mediafire reducirá la velocidad de descarga significativamente. Esto es algo que no podemos evitar. El usuario deberá esperar a que su cuota de descarga esté disponible nuevamente.

#### P. Un usuario de <INGRESE PAÍS AQUÍ\> no puede acceder a mi juego a través de la página de descarga debido a restricciones regionales. ¿Puede actualizar el juego a través de PokéUpdater de todas maneras?

R. El PokéUpdater no puede evitar ninguna restricción regional o de contenido impuestas por las páginas de descarga. De la misma manera, tampoco será posible conseguir archivos privados o protegidos por clave.

#### P. ¿Pueden mis actualizaciones ser opcionales u obligatorias?

R. Si los scripts se han implementado como especificado en la sección [Mantenimiento de tus scripts de RPG Maker XP](#mantenimiento-de-tus-scripts-de-rpg-maker-xp), es posible controlar si el control de versiones y actualización serán llevados a cabo obligatoriamente o no cuando el juego muestre su pantalla de carga cambiando los valores de las variables `FORCE_VERSION_CHECK` y `FORCE_UPDATE` del archivo `pu_config`. Tener en cuenta que si a la variable `FORCE_UPDATE` se le coloca un valor `falso`, entonces la lógica de actualización deberá ser llamada en otro lugar, por ejemplo, en un botón de menú como ejemplificado en la sección [Extractos de código opcionales](#extractos-de-código-opcionales). Tener en cuenta también que configurar la variable `FORCE_VERSION_CHECK` a un valor `falso` desactivará el PokéUpdater a menos que la validación de versiones sea hecha en otro lugar.

#### P. No quiero hacer uso del ejecutable del PokéUpdater pero aún así quiero notificar a mis usarios del lanzamiento de una nueva versión. ¿Es posible hacer esto con los scripts provistos?

R. ¡Sí! Al configurar la variable `FORCE_VERSION_CHECK` a un valor `verdadero` y la variable `FORCE_UPDATE` a un valor `falso` y manteniendo el archivo de Pastebin actualizado, el juego levantará un mensaje notificando al usuario que una nueva versión está disponible pero el ejecutable no se correrá. Si ésta es la única función requerida, entonces no es obligatorio descargar y copíar el archivo `poke_updater.exe` junto con el juego.

#### P. Los textos en el juego se visualizan en español, pero los necesito en otro idioma, ¿no hay traducciones disponibles?

R. Esto es causado probablemente por no tener el archivo `pu_locales` en la carpeta del juego. Si el archivo `pu_locales` no se encuentra en el directorio del juego, los mensajes serán fijados en español que se encuentran en el método `pbGetPokeUpdaterText` de la clase `GameVersion.rb`. Tener en cuenta, que únicamente aquellos idiomas soportados por Pokémon Essentials 16.2 se tienen en cuenta. Las traducciones existentes pueden modificarse actualizando el archivo `pu_locales`.

#### P. ¿Se verán afectadas las partidas existentes del usuario?

R. No. El proceso de actualizaciónb trabaja únicamente dentro de la carpeta del juego y no afectará NINGÚN otro archivo en la PC del usuario. Como las partidas se guardan en la ruta `C:/Usuarios/NOMBRE/SavedGames/NOMBRE_DEL_JUEGO`, no se verán afectadas.

#### P. Mi antivirus detecta el archivo `poke_updater.exe` como un potencial virus, ¿por qué es eso?

_~~R. Debido a que el ejecutable del actualizador es compilado haciendo uso de la librería pyInstaller, programas antivirus como Windows Defender automáticamente lo detectan como un potencial virus. El `poke_updater.exe` no contiene código malicioso de ningún tipo y actualmente estamos trabajando intentando encontrar una manera de que no sea detectado de esta manera. Como queremos ser transparentes sobre cómo funciona el actualizador, hemos hecho disponible el código fuente del archivo `poke_updater.exe`.~~_

R. Comenzando con la versión 1.1.0 hemos cambiado la forma en que compilamos el ejecutable, lo cual debería no volver a disparar este falso positivo. De no ser ese el caso, por favor abrir un nuevo [reporte de problema](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=reporte-de-error.md&title=%5BBUG%5D) para que podamos revisarlo en detalle.

#### P. ¿Harán disponible el código fuente del actualizador?

_~~R. En el futuro es posible que hagamos disponible el código fuente pero no es una prioridad en el momento. Si una funcionalidad requerida no se encuentra disponible puedes levantar una [solicitud de funcionalidad](https://github.com/Pokemon-Fan-Games/PokemonEssentialsGameUpdater/issues/new?assignees=&labels=&projects=&template=solicitud-de-funcionalidad.md&title=%5BFEATURE+REQUEST%5D).~~_

R. Sí, con la versión 1.1.0 el código fuente se ha hecho disponible y puede ser encontrado [aquí](/poke_updater_source_code/).

**Agradecemos a los usuarios del [foro RPG Maker Web](https://forums.rpgmakerweb.com/index.php?threads/http-network-library.15009/#post-149590) por su ayuda con la lógica de descarga de archivos a través de HTTP.**
