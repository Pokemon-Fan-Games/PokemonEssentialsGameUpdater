from enum import Enum

class Host(Enum):
    MEGA=1
    GOOGLE_DRIVE=2
    MEDIAFIRE=3
    DROPBOX=4
    ANONFILES=5

class QuitBoxTitle():
    TITLE = {
        'en': 'Quit',
        'es': 'Salir',
        'fr': 'Quitter',
        'pt': 'Sair',
        'it': 'Esci',
        'de': 'Beenden',
        'ru': 'Выход',
        'ja': 'やめる',
        'zh': '退出',
        'ko': '종료',
        'ar': 'الخروج',
        'tr': 'Çıkış',
        'pl': 'Wyjdź',
        'nl': 'Stoppen',
        'sv': 'Avsluta',
        'da': 'Afslut',
        'fi': 'Lopeta',
        'no': 'Avslutt',
        'cs': 'Opustit',
        'hu': 'Kilépés',
        'el': 'Αποχώρηση',
        'he': 'יציאה'
    }

class Step():
    RETRIEVING = (1,{
        'en': 'Retrieving version information...', 
        'es': 'Recuperando información de la versión...', 
        'fr': 'Récupération des informations de version...', 
        'pt': 'Recuperando informações da versão...', 
        'it': 'Recupero delle informazioni sulla versione...', 
        'de': 'Abrufen von Versionsinformationen...', 
        'ru': 'Получение информации о версии...', 
        'ja': 'バージョン情報の取得中...', 
        'zh': '检索版本信息...', 
        'ko': '버전 정보 검색 중...', 
        'ar': 'استرجاع معلومات الإصدار...', 
        'tr': 'Sürüm bilgileri alınıyor...', 
        'pl': 'Pobieranie informacji o wersji...', 
        'nl': 'Ophalen van versie-informatie...', 
        'sv': 'Hämtar versionsinformation...', 
        'da': 'Henter versionsoplysninger...', 
        'fi': 'Haetaan versiotietoja...', 
        'no': 'Henter versjonsinformasjon...', 
        'cs': 'Načítání informací o verzi...', 
        'hu': 'Verzióinformációk lekérése...', 
        'el': 'Ανάκτηση πληροφοριών έκδοσης...', 
        'he': 'איסוף מידע על גרסה...'})
    DELETING = (0,{
        'en': 'Removing old files...', 
        'es': 'Eliminando archivos antiguos...', 
        'fr': 'Suppression des anciens fichiers...', 
        'pt': 'Removendo arquivos antigos...', 
        'it': 'Rimozione dei vecchi file...', 
        'de': 'Entfernen alter Dateien...', 
        'ru': 'Удаление старых файлов...', 
        'ja': '古いファイルを削除中...', 
        'zh': '删除旧文件...', 
        'ko': '이전 파일 제거 중...', 
        'ar': 'إزالة الملفات القديمة...', 
        'tr': 'Eski dosyalar kaldırılıyor...', 
        'pl': 'Usuwanie starych plików...', 
        'nl': 'Oude bestanden verwijderen...', 
        'sv': 'Tar bort gamla filer...', 
        'da': 'Fjerner gamle filer...', 
        'fi': 'Poistetaan vanhat tiedostot...', 
        'no': 'Fjerner gamle filer...', 
        'cs': 'Odstraňování starých souborů...', 
        'hu': 'Régi fájlok törlése...', 
        'el': 'Αφαίρεση παλαιών αρχείων...', 
        'he': 'מסיר קבצים ישנים...'
        })
    DOWNLOADING=(1,{
        'en': 'Downloading new version...', 
        'es': 'Descargando nueva versión...', 
        'fr': 'Téléchargement de la nouvelle version...', 
        'pt': 'Baixando nova versão...', 
        'it': 'Download della nuova versione...', 
        'de': 'Die neue Version wird heruntergeladen...', 
        'ru': 'Загрузка новой версии...', 
        'ja': '新しいバージョンをダウンロード中...', 
        'zh': '下载新版本...', 
        'ko': '새 버전 다운로드 중...', 
        'ar': 'تحميل الإصدار الجديد...', 
        'tr': 'Yeni sürüm indiriliyor...', 
        'pl': 'Pobieranie nowej wersji...', 
        'nl': 'Nieuwe versie downloaden...', 
        'sv': 'Laddar ner ny version...', 
        'da': 'Downloader ny version...', 
        'fi': 'Lataa uusi versio...', 
        'no': 'Laster ned ny versjon...', 
        'cs': 'Stahování nové verze...', 
        'hu': 'Új verzió letöltése...', 
        'el': 'Λήψη νέας έκδοσης...', 
        'he': 'הורדת גרסה חדשה...'
    })
    EXTRACTING=(1,{
        'en': 'Extracting files...', 
        'es': 'Extrayendo archivos...', 
        'fr': 'Extraction des fichiers...', 
        'pt': 'Extraindo arquivos...', 
        'it': 'Estrazione dei file...', 
        'de': 'Extrahieren von Dateien...', 
        'ru': 'Извлечение файлов...', 
        'ja': 'ファイルを抽出中...', 
        'zh': '提取文件...', 
        'ko': '파일 추출 중...', 
        'ar': 'استخراج الملفات...', 
        'tr': 'Dosyalar çıkarılıyor...', 
        'pl': 'Wypakowywanie plików...', 
        'nl': 'Bestanden uitpakken...', 
        'sv': 'Packa upp filer...', 
        'da': 'Udpakning af filer...', 
        'fi': 'Pakkaa tiedostoja...', 
        'no': 'Pakker ut filer...', 
        'cs': 'Rozbalování souborů...', 
        'hu': 'Fájlok kicsomagolása...', 
        'el': 'Εξαγωγή αρχείων...', 
        'he': 'חילוץ קבצים...'
        })
    MOVING=(0,{
        'en': 'Moving files...', 
        'es': 'Moviendo archivos...', 
        'fr': 'Déplacement des fichiers...', 
        'pt': 'Movendo arquivos...', 
        'it': 'Spostamento dei file...', 
        'de': 'Verschieben von Dateien...', 
        'ru': 'Перемещение файлов...', 
        'ja': 'ファイルを移動中...', 
        'zh': '移动文件...', 
        'ko': '파일 이동 중...', 
        'ar': 'نقل الملفات...', 
        'tr': 'Dosyalar taşınıyor...', 
        'pl': 'Przenoszenie plików...', 
        'nl': 'Bestanden verplaatsen...', 
        'sv': 'Flyttar filer...', 
        'da': 'Flytter filer...', 
        'fi': 'Siirtää tiedostoja...', 
        'no': 'Flytter filer...', 
        'cs': 'Přesun souborů...', 
        'hu': 'Fájlok mozgatása...', 
        'el': 'Μετακίνηση αρχείων...', 
        'he': 'העברת קבצים...'
        })

class ExceptionMessage():
    CLOSE_WINDOW = {
        'en': "An error has occurred and the game could not be updated. You may now close this window.",
        'es': 'Se ha producido un error y no se ha podido actualizar el juego. Ahora puede cerrar esta ventana.',
        'fr': "Une erreur s'est produite et le jeu n'a pas pu être mis à jour. Vous pouvez maintenant fermer cette fenêtre.",
        'pt': 'Ocorreu um erro e o jogo não pôde ser atualizado. Você pode fechar esta janela agora.',
        'it': "Si è verificato un errore e il gioco non è stato aggiornato. Puoi chiudere questa finestra ora.",
        'de': 'Ein Fehler ist aufgetreten und das Spiel konnte nicht aktualisiert werden. Sie können dieses Fenster jetzt schließen.',
        'ru': 'Произошла ошибка и игра не была обновлена. Теперь вы можете закрыть это окно.',
        'ja': 'エラーが発生し、ゲームを更新できませんでした。このウィンドウを閉じることができます。',
        'zh': '发生错误，无法更新游戏。您现在可以关闭此窗口。',
        'ko': '오류가 발생하여 게임을 업데이트 할 수 없습니다. 이제이 창을 닫을 수 있습니다.',
        'ar': 'حدث خطأ وتعذر تحديث اللعبة. يمكنك الآن إغلاق هذه النافذة.',
        'tr': 'Bir hata oluştu ve oyun güncellenemedi. Şimdi bu pencereyi kapatabilirsiniz.',
        'pl': 'Wystąpił błąd i nie można zaktualizować gry. Teraz możesz zamknąć to okno.',
        'nl': 'Er is een fout opgetreden en het spel kon niet worden bijgewerkt. U kunt dit venster nu sluiten.',
        'sv': 'Ett fel har uppstått och spelet kunde inte uppdateras. Du kan nu stänga det här fönstret.',
        'da': 'Der opstod en fejl, og spillet kunne ikke opdateres. Du kan nu lukke dette vindue.',
        'fi': 'Virhe ilmeni, eikä peliä voitu päivittää. Voit nyt sulkea tämän ikkunan.',
        'no': 'Det oppstod en feil, og spillet kunne ikke oppdateres. Du kan nå lukke dette vinduet.',
        'cs': 'Došlo k chybě a hra nemohla být aktualizována. Nyní můžete toto okno zavřít.',
        'hu': 'Hiba történt, és a játékot nem lehetett frissíteni. Most bezárhatja ezt az ablakot.',
        'el': 'Προέκυψε σφάλμα και το παιχνίδι δεν μπόρεσε να ενημερωθεί. Μπορείτε τώρα να κλείσετε αυτό το παράθυρο.',
        'he': 'אירעה שגיאה ולא ניתן היה לעדכן את המשחק. עכשיו אתה יכול לסגור את החלון הזה.'
    }
    NO_NEW_VERSION= {
        'en': 'No new version available or initial version has not been set up',
        'es': 'No hay una nueva versión disponible o la versión inicial no se ha configurado',
        'fr': "Aucune nouvelle version disponible ou la version initiale n'a pas été configurée",
        'pt': 'Nenhuma nova versão disponível ou a versão inicial não foi configurada',
        'it': 'Nessuna nuova versione disponibile o la versione iniziale non è stata configurata',
        'de': 'Keine neue Version verfügbar oder die anfängliche Version wurde nicht eingerichtet',
        'ru': 'Нет новой версии или начальная версия не настроена',
        'ja': '新しいバージョンが利用できないか、初期バージョンが設定されていません',
        'zh': '没有新版本可用或未设置初始版本',
        'ko': '새 버전을 사용할 수 없거나 초기 버전이 설정되지 않았습니다',
        'ar': 'لا يوجد إصدار جديد متاح أو لم يتم إعداد الإصدار الأولي',
        'tr': 'Yeni bir sürüm yok veya ilk sürüm yapılandırılmadı',
        'pl': 'Brak nowej wersji lub nie skonfigurowano wersji początkowej',
        'nl': 'Geen nieuwe versie beschikbaar of initiële versie is niet ingesteld',
        'sv': 'Ingen ny version tillgänglig eller initial version har inte ställts in',
        'da': 'Ingen ny version tilgængelig eller den indledende version er ikke sat op',
        'fi': 'Uutta versiota ei ole saatavana tai alkuperäistä versiota ei ole määritetty',
        'no': 'Ingen ny versjon tilgjengelig eller startversjonen er ikke satt opp',
        'cs': 'Žádná nová verze není k dispozici nebo nebyla nastavena počáteční verze',
        'hu': 'Nincs új verzió vagy az elsődleges verzió nincs beállít',
        'el': 'Δεν υπάρχει νέα έκδοση διαθέσιμη ή η αρχική έκδοση δεν έχει ρυθμιστεί',
        'he': 'אין גרסה חדשה זמינה או שהגרסה הראשונית לא הוגדרה'
        }
    NO_PASTEBIN_URL={
        'en': 'Could not find pastebin url in settings file', 
        'es': 'No se pudo encontrar la url de pastebin en el archivo de configuración', 
        'fr': "Impossible de trouver l'URL de pastebin dans le fichier de paramètres", 
        'pt': 'Não foi possível encontrar o url do pastebin no arquivo de configuração', 
        'it': "Impossibile trovare l'url di pastebin nel file delle impostazioni",
        'de': 'Konnte die Pastebin-URL nicht in der Einstellungsdatei finden',
        'ru': 'Не удалось найти URL-адрес pastebin в файле настроек',
        'ja': '設定ファイルでpastebinのURLが見つかりませんでした',
        'zh': '在设置文件中找不到pastebin网址',
        'ko': '설정 파일에서 pastebin url을 찾을 수 없습니다',
        'ar': 'تعذر العثور على عنوان url للصق في ملف الإعدادات',
        'tr': 'Ayarlar dosyasında pastebin url bulunamadı',
        'pl': 'Nie można znaleźć adresu url pastebin w pliku ustawień',
        'nl': 'Kan pastebin-url niet vinden in instellingenbestand',
        'sv': 'Kunde inte hitta pastebin-url i inställningsfilen',
        'da': 'Kunne ikke finde pastebin url i indstillingsfil',
        'fi': 'Pastebin-osoitetta ei löytynyt asetustiedostosta',
        'no': 'Kunne ikke finne pastebin url i innstillingsfil',
        'cs': 'V souboru se nastavení nepodařilo najít adresu url pastebin',
        'hu': 'Nem található a pastebin url a beállítási fájlban',
        'el': 'Δεν ήταν δυνατή η εύρεση του url pastebin στο αρχείο ρυθμίσεων',
        'he': 'לא ניתן למצוא כתובת אתר של Pastebin' 
        }
    PASTEBIN_NOT_RAW_URL={
        'en': 'Configured Pastebin URL is not RAW format. Game file cannot be retrieved.',
        'es': 'La URL de Pastebin configurada no es RAW. No se puede recuperar el archivo del juego.',
        'fr': "L'URL Pastebin configurée n'est pas au format RAW. Le fichier de jeu ne peut pas être récupéré.",
        'pt': 'A URL do Pastebin configurada não é RAW. O arquivo do jogo não pode ser recuperado.',
        'it': "L'URL di Pastebin configurata non è RAW. Il file di gioco non può essere recuperato.",
        'de': 'Die konfigurierte Pastebin-URL ist nicht im RAW-Format. Die Spieldatei kann nicht abgerufen werden.',
        'ru': 'Настроенный URL-адрес Pastebin не в формате RAW. Невозможно получить файл игры.',
        'ja': '設定されたPastebin URLはRAW形式ではありません。ゲームファイルを取得できません。',
        'zh': '配置的Pastebin网址不是RAW格式。无法检索游戏文件。',
        'ko': '구성된 Pastebin URL이 RAW 형식이 아닙니다. 게임 파일을 검색 할 수 없습니다.',
        'ar': 'عنوان URL للصق المكون ليس بتنسيق RAW. لا يمكن استرداد ملف اللعبة.',
        'tr': 'Yapılandırılmış Pastebin URL, RAW biçiminde değil. Oyun dosyası alınamıyor.',
        'pl': 'Skonfigurowany adres URL Pastebin nie jest w formacie RAW. Nie można pobrać pliku gry.',
        'nl': 'Geconfigureerde Pastebin-URL is niet in RAW-indeling. Game-bestand kan niet worden opgehaald.',
        'sv': 'Konfigurerad Pastebin URL är inte i RAW-format. Spelfil kan inte hämtas.',
        'da': 'Konfigureret Pastebin URL er ikke i RAW-format. Spilfil kan ikke hentes.',
        'fi': 'Määritetty Pastebin-URL ei ole RAW-muodossa. Pelitiedostoa ei voi noutaa.',
        'no': 'Konfigurert Pastebin URL er ikke i RAW-format. Spillfil kan ikke hentes.',
        'cs': 'Konfigurovaná adresa URL Pastebin není ve formátu RAW. Soubor hry nelze získat.',
        'hu': 'A konfigurált Pastebin URL nem RAW formátumú. A játékfájl nem tölthető le.',
        'el': 'Η διαμορφωμένη διεύθυνση URL Pastebin δεν είναι σε μορφή RAW. Δεν είναι δυνατή η ανάκτηση του αρχείου παιχνιδιού.',
        'he': 'כתובת ה-URL שהוגדרה של Pastebin אינה בפורמט RAW. לא ניתן לאחזר את קובץ המשחק.'
    }
    NO_FILE_HOST={
        'en': 'File host not supported', 
        'es': 'Host de archivos no soportado', 
        'fr': 'Hébergeur de fichiers non pris en charge',
        'pt': 'Host de arquivos não suportado',
        'it': 'Host file non supportato',
        'de': 'Datei-Host nicht unterstützt',
        'ru': 'Файл хост не поддерживается',
        'ja': 'ファイルホストはサポートされていません',
        'zh': '文件主机不受支持',
        'ko': '파일 호스트가 지원되지 않습니다',
        'ar': 'مضيف الملفات غير مدعوم',
        'tr': 'Dosya barındırma desteklenmiyor',
        'pl': 'Host plików nie jest obsługiwany',
        'nl': 'Bestandshost niet ondersteund',
        'sv': 'Filvärd stöds inte',
        'da': 'Filvært understøttes ikke',
        'fi': 'Tiedostojen isäntää ei tueta',
        'no': 'Filvert støttes ikke',
        'cs': 'Host souborů není podporován',
        'hu': 'A fájlházigazda nem támogatott',
        'el': 'Οικοδεσπότης αρχείων δεν υποστηρίζεται',
        'he': 'מארח הקובץ אינו נתמך'
        }
    NO_PASTEBIN_CONTENT={
        'en': 'Could not get pastebin content', 
        'es': 'No se pudo obtener el contenido de pastebin', 
        'fr': "Impossible d'obtenir le contenu de pastebin", 
        'pt': 'Não foi possível obter o conteúdo do pastebin', 
        'it': "Impossibile ottenere il contenuto di pastebin", 
        'de': 'Konnte den Inhalt von Pastebin nicht abrufen', 
        'ru': 'Не удалось получить содержимое pastebin', 
        'ja': 'pastebinのコンテンツを取得できませんでした', 
        'zh': '无法获取pastebin内容', 
        'ko': 'pastebin 콘텐츠를 가져올 수 없습니다', 
        'ar': 'تعذر الحصول على محتوى pastebin', 
        'tr': 'Pastebin içeriği alınamadı', 
        'pl': 'Nie można uzyskać zawartości pastebin', 
        'nl': 'Kan pastebin-inhoud niet ophalen', 
        'sv': 'Kunde inte hämta pastebin-innehåll', 
        'da': 'Kunne ikke få pastebin-indhold', 
        'fi': 'Pastebin-sisältöä ei saatu', 
        'no': 'Kunne ikke få pastebin-innhold', 
        'cs': 'Obsah pastebin nelze získat', 
        'hu': 'Nem sikerült a pastebin tartalmát', 
        'el': 'Δεν ήταν δυνατή η λήψη του περιεχομένου του pastebin', 
        'he': 'לא ניתן לקבל את תוכן ה-Pastebin'
        }
    NO_VALID_FILE_FOUND={
        'en': 'Could not find a valid file to extract',
        'es': 'No se pudo encontrar un archivo válido para extraer',
        'fr': "Impossible de trouver un fichier valide à extraire",
        'pt': 'Não foi possível encontrar um arquivo válido para extrair',
        'it': "Impossibile trovare un file valido da estrarre",
        'de': 'Konnte keine gültige Datei zum Extrahieren finden',
        'ru': 'Не удалось найти действительный файл для извлечения',
        'ja': '有効なファイルを見つけることができませんでした',
        'zh': '找不到有效的文件进行提取',
        'ko': '유효한 파일을 찾을 수 없습니다',
        'ar': 'تعذر العثور على ملف صالح لاستخراجه',
        'tr': 'Geçerli bir dosya bulunamadı',
        'pl': 'Nie można znaleźć prawidłowego pliku do wypakowania',
        'nl': 'Kan geen geldig bestand vinden om uit te pakken',
        'sv': 'Kunde inte hitta en giltig fil att packa upp',
        'da': 'Kunne ikke finde en gyldig fil til udpakning',
        'fi': 'Kelvollista tiedostoa ei löytynyt purkamiseen',
        'no': 'Kunne ikke finne en gyldig fil for å pakke ut',
        'cs': 'Nepodařilo se najít platný soubor k extrakci',
        'hu': 'Nem található érvényes fájl a kicsomagoláshoz',
        'el': 'Δεν ήταν δυνατή η εύρεση ενός έγκυρου αρχείου για εξαγωγή',
        'he': 'לא ניתן למצוא קובץ תקין לחילוץ'
        }
    DOWNLOAD_ERROR={
        'en': 'An error has occurred while downloading the new version',
        'es': 'Se ha producido un error al descargar la nueva versión',
        'fr': "Une erreur s'est produite lors du téléchargement de la nouvelle version",
        'pt': 'Ocorreu um erro ao baixar a nova versão',
        'it': "Si è verificato un errore durante il download della nuova versione",
        'de': 'Beim Herunterladen der neuen Version ist ein Fehler aufgetreten',
        'ru': 'Произошла ошибка при загрузке новой версии',
        'ja': '新しいバージョンのダウンロード中にエラーが発生しました',
        'zh': '下载新版本时发生错误',
        'ko': '새 버전을 다운로드하는 중에 오류가 발생했습니다',
        'ar': 'حدث خطأ أثناء تنزيل الإصدار الجديد',
        'tr': 'Yeni sürüm indirilirken bir hata oluştu',
        'pl': 'Podczas pobierania nowej wersji wystąpił błąd',
        'nl': 'Er is een fout opgetreden bij het downloaden van de nieuwe versie',
        'sv': 'Ett fel uppstod vid hämtning av den nya versionen',
        'da': 'Der opstod en fejl under download af den nye version',
        'fi': 'Uutta versiota ladattaessa tapahtui virhe',
        'no': 'Det oppstod en feil under nedlasting av den nye versjonen',
        'cs': 'Při stahování nové verze došlo k chybě',
        'hu': 'Hiba történt az új verzió letöltése közben',
        'el': 'Προέκυψε σφάλμα κατά τη λήψη της νέας έκδοσης',
        'he': 'אירעה שגיאה בעת הורדת הגרסה החדשה'
        }
    DOWNLOAD_ERROR_MEGA={
        'en': 'Allowed transfer quota exceeded or download limit reached try again later',
        'es': 'Se superó la cuota de transferencia permitida o se alcanzó el límite de descarga, inténtelo de nuevo más tarde',
        'fr': "Le quota de transfert autorisé a été dépassé ou la limite de téléchargement a été atteinte, réessayez plus tard",
        'pt': 'A cota de transferência permitida foi excedida ou o limite de download foi atingido, tente novamente mais tarde',
        'it': "La quota di trasferimento consentita è stata superata o è stato raggiunto il limite di download, riprova più tardi",
        'de': 'Das zulässige Übertragungskontingent wurde überschritten oder das Download-Limit wurde erreicht. Versuchen Sie es später erneut',
        'ru': 'Превышена разрешенная квота передачи или достигнут лимит загрузки, повторите попытку позже',
        'ja': '許可された転送クォータを超えたか、ダウンロード制限に達しました。後でもう一度やり直してください',
        'zh': '超过允许的传输配额或达到下载限制，请稍后再试',
        'ko': '허용 된 전송 할당량을 초과하거나 다운로드 제한에 도달하여 나중에 다시 시도하십시오',
        'ar': 'تجاوز حصة التحويل المسموح بها أو تم الوصول إلى الحد المسموح به للتنزيل ، حاول مرة أخرى في وقت لاحق',
        'tr': 'İzin verilen aktarım kotası aşıldı veya indirme sınırına ulaşıldı, daha sonra tekrar deneyin',
        'pl': 'Przekroczono dozwoloną kwotę transferu lub osiągnięto limit pobierania, spróbuj ponownie później',
        'nl': 'Toegestane overdrachtsquotum overschreden of downloadlimiet bereikt, probeer het later opnieuw',
        'sv': 'Tillåtet överföringskvot överskriden eller nedladdningsgräns nådd, försök igen senare',
        'da': 'Den tilladte overførselskvota er overskredet, eller downloadgrænsen er nået, prøv igen senere',
        'fi': 'Sallittu siirtokiintiö ylitetty tai latausraja saavutettu, yritä myöhemmin uudelleen',
        'no': 'Tillatt overføringskvote overskredet eller nedlastingsgrense nådd, prøv igjen senere',
        'cs': 'Překročena povolená kvóta přenosu nebo dosažen limit stahování, zkuste to znovu později',
        'hu': 'A megengedett átviteli kvóta túllépte vagy a letöltési korlátot elérték, próbálja meg később újra',
        'el': 'Υπερβαίνεται η επιτρεπόμενη ποσόστωση μεταφοράς ή έχει επιτευχθεί το όριο λήψης, δοκιμάστε ξανά αργότερα',
        'he': 'חריגה קוטה ההעברה המותרת או הגעת לגבול ההורדה, נסה שוב מאוחר יותר'
        }
    NO_VALID_FOLDER_FOUND={
        'en': 'Could not find a valid folder to retrieve data from',
        'es': 'No se pudo encontrar una carpeta válida para recuperar datos',
        'fr': "Impossible de trouver un dossier valide pour récupérer les données",
        'pt': 'Não foi possível encontrar uma pasta válida para recuperar dados',
        'it': "Impossibile trovare una cartella valida per recuperare i dati",
        'de': 'Konnte keinen gültigen Ordner zum Abrufen von Daten finden',
        'ru': 'Не удалось найти действительную папку для извлечения данных',
        'ja': 'データを取得する有効なフォルダが見つかりませんでした',
        'zh': '找不到有效的文件夹以检索数据',
        'ko': '데이터를 검색할 수있는 유효한 폴더를 찾을 수 없습니다',
        'ar': 'تعذر العثور على مجلد صالح لاسترداد البيانات منه',
        'tr': 'Verileri almak için geçerli bir klasör bulunamadı',
        'pl': 'Nie można znaleźć prawidłowego folderu do pobrania danych',
        'nl': 'Kan geen geldige map vinden om gegevens uit te halen',
        'sv': 'Kunde inte hitta en giltig mapp för att hämta data från',
        'da': 'Kunne ikke finde en gyldig mappe til at hente data fra',
        'fi': 'Kelvollista kansiota ei löytynyt tietojen noutamiseksi',
        'no': 'Kunne ikke finne en gyldig mappe for å hente data fra',
        'cs': 'Nepodařilo se najít platnou složku pro načtení dat',
        'hu': 'Nem található érvényes mappa az adatok lekéréséhez',
        'el': 'Δεν ήταν δυνατή η εύρεση ενός έγκυρου φακέλου για την ανάκτηση δεδομένων',
        'he': 'לא ניתן למצוא תיקייה תקינה לאחזור נתונים'
        }
    UNEXPECTED_ERROR= {
        'en': 'An unexpected error has occurred',
        'es': 'Se ha producido un error inesperado',
        'fr': "Une erreur inattendue s'est produite",
        'pt': 'Ocorreu um erro inesperado',
        'it': 'Si è verificato un errore imprevisto',
        'de': 'Ein unerwarteter Fehler ist aufgetreten',
        'ru': 'Произошла непредвиденная ошибка',
        'ja': '予期しないエラーが発生しました',
        'zh': '发生意外错误',
        'ko': '예기치 않은 오류가 발생했습니다',
        'ar': 'حدث خطأ غير متوقع',
        'tr': 'Beklenmeyen bir hata oluştu',
        'pl': 'Wystąpił nieoczekiwany błąd',
        'nl': 'Er is een onverwachte fout opgetreden',
        'sv': 'Ett oväntat fel inträffade',
        'da': 'Der opstod en uventet fejl',
        'fi': 'Odottamaton virhe tapahtui',
        'no': 'Det oppstod en uventet feil',
        'cs': 'Došlo k neočekávané chybě',
        'hu': 'Váratlan hiba történt',
        'el': 'Προέκυψε απρόσμενο σφάλμα',
        'he': 'אירעה שגיאה לא צפויה'
        }
    DO_NOT_CLOSE = {
        'en': "DO NOT CLOSE THIS WINDOW UNTIL THE GAME LAUNCHES, OTHERWISE YOU MAY HAVE TO REDOWNLOAD THE GAME",
        'es': 'NO CIERRE ESTA VENTANA HASTA QUE SE INICIE EL JUEGO, DE LO CONTRARIO PUEDE TENER QUE VOLVER A DESCARGAR EL JUEGO',
        'fr': "NE FERMEZ PAS CETTE FENÊTRE JUSQU'À CE QUE LE JEU SE LANCE, SINON VOUS POUVEZ DEVOIR RE-TÉLÉCHARGER LE JEU",
        'pt': 'NÃO FECHE ESTA JANELA ATÉ QUE O JOGO SEJA INICIADO, CASO CONTRÁRIO, VOCÊ PODE TER QUE BAIXAR O JOGO NOVAMENTE',
        'it': "NON CHIUDERE QUESTA FINESTRA FINO AL LANCIO DEL GIOCO, ALTRIMENTI POTRESTI DOVER RISCARICARE IL GIOCO",
        'de': 'SCHLIESSEN SIE DIESES FENSTER NICHT, BIS DAS SPIEL GESTARTET WIRD, SONST MÜSSEN SIE DAS SPIEL ERNEUT HERUNTERLADEN',
        'ru': 'НЕ ЗАКРЫВАЙТЕ ЭТО ОКНО ДО ЗАПУСКА ИГРЫ, ИНАЧЕ ВАМ ПРИДЕТСЯ ПЕРЕЗАГРУЖАТЬ ИГРУ',
        'ja': 'ゲームが起動するまでこのウィンドウを閉じないでください。そうしないと、ゲームを再ダウンロードする必要がある場合があります',
        'zh': '在游戏启动之前，请不要关闭此窗口，否则您可能需要重新下载游戏',
        'ko': '게임이 시작 될 때까지이 창을 닫지 마십시오. 그렇지 않으면 게임을 다시 다운로드해야 할 수 있습니다',
        'ar': 'لا تقم بإغلاق هذه النافذة حتى يتم تشغيل اللعبة ، وإلا قد تضطر إلى إعادة تنزيل اللعبة',
        'tr': 'OYUN BAŞLATILANA KADAR BU PENCEREYİ KAPATMAYIN, AYRICA OYUNU YENİDEN İNDİRMENİZ GEREKEBİLİR',
        'pl': 'NIE ZAMYKAJ TEGO OKNA, AŻ GRA SIĘ URUCHOMI, W PRZECIWNYM RAZIE MOŻE BYĆ KONIECZNE PONOWNIE POBRANIE GRY',
        'nl': 'SLUIT DIT VENSTER NIET TOTDAT HET SPEL WORDT GESTART, ANDERS MOET U HET SPEL OPNIEUW DOWNLOADEN',
        'sv': 'STÄNG INTE DETTA FÖNSTER TILLS SPELET STARTAR, ANNARS MÅSTE DU LADDA NER SPELET IGEN',
        'da': 'LAD IKKE DETTE VINDUE, FØR SPILLET STARTER, ELLERS KAN DU MÅSKE DOWNLOADE SPILLET IGEN',
        'fi': 'ÄLÄ SULJE TÄTÄ IKKUNAA, KUNNES PELI KÄYNNISTYY, MUUTEN SINUN ON LADATTAVA PELI UUDELLEEN',
        'no': 'IKKE LUKK DETTE VINDUET FØR SPILLET STARTER, ELLERS KAN DU MÅTTE LASTE NED SPILLET IGJEN',
        'cs': 'NEZAVÍREJTE TOTO OKNO, DOKUD SE HRA NEZAPNE, JINAK BUDETE MUSÍT HRU ZNOVU STÁHNOUT',
        'hu': 'NE ZÁRJA BE AZT AZ ABLAKOT, AMÍG A JÁTÉK ELINDUL, KÜLÖNBEN ÚJRA LETÖLTENIE A JÁTÉKOT',
        'el': 'ΜΗΝ ΚΛΕΙΣΕΤΕ ΑΥΤΟ ΤΟ ΠΑΡΑΘΥΡΟ ΜΕΧΡΙ ΝΑ ΞΕΚΙΝΗΣΕΙ ΤΟ ΠΑΙΧΝΙΔΙ, ΔΙΑΦΟΡΕΤΙΚΑ ΜΠΟΡΕΙ ΝΑ ΧΡΕΙΑΣΤΕΙ ΝΑ ΚΑΤΕΒΑΣΕΤΕ ΞΑΝΑ ΤΟ ΠΑΙΧΝΙΔΙ',
        'he': 'אל תסגור חלון זה עד שהמשחק מתחיל, אחרת עליך להוריד את המשחק שוב'
        }
    FILE_NOT_ACCESSIBLE = {
        'en': 'File could not be accessed or does not exist. Contact the game developer for more information.',
        'es': 'El archivo no está disponible. Póngase en contacto con el desarrollador del juego para obtener más información.',
        'fr': "Le fichier n'a pas pu être consulté ou n'existe pas. Contactez le développeur du jeu pour plus d'informations.",
        'pt': 'O arquivo não pôde ser acessado ou não existe. Entre em contato com o desenvolvedor do jogo para obter mais informações.',
        'it': "Il file non è stato accessibile o non esiste. Contatta lo sviluppatore del gioco per maggiori informazioni.",
        'de': 'Die Datei konnte nicht abgerufen oder nicht gefunden werden. Kontaktieren Sie den Spieleentwickler für weitere Informationen.',
        'ru': 'Не удалось получить доступ к файлу или он не существует. Свяжитесь с разработчиком игры для получения дополнительной информации.',
        'ja': 'ファイルにアクセスできないか、存在しません。詳細については、ゲーム開発者にお問い合わせください。',
        'zh': '无法访问文件或文件不存在。有关更多信息，请联系游戏开发人员。',
        'ko': '파일에 액세스 할 수 없거나 파일이 없습니다. 자세한 내용은 게임 개발자에게 문의하십시오.',
        'ar': 'تعذر الوصول إلى الملف أو لا يوجد. اتصل بمطور اللعبة لمزيد من المعلومات.',
        'tr': 'Dosyaya erişilemedi veya mevcut değil. Daha fazla bilgi için oyun geliştirici ile iletişime geçin.',
        'pl': 'Nie można uzyskać dostępu do pliku lub nie istnieje. Skontaktuj się z twórcą gry, aby uzyskać więcej informacji.',
        'nl': 'Het bestand kon niet worden geopend of bestaat niet. Neem contact op met de game-ontwikkelaar voor meer informatie.',
        'sv': 'Filen kunde inte nås eller finns inte. Kontakta spelutvecklaren för mer information.',
        'da': 'Filen kunne ikke få adgang til eller eksisterer ikke. Kontakt spiludvikleren for mere information.',
        'fi': 'Tiedostoa ei voitu käyttää tai sitä ei ole. Ota yhteyttä pelin kehittäjään lisätietojen saamiseksi.',
        'no': 'Filen kunne ikke åpnes eller eksisterer ikke. Kontakt spillutvikleren for mer informasjon.',
        'cs': 'Soubor nebylo možné otevřít nebo neexistuje. Pro více informací kontaktujte vývojáře hry.',
        'hu': 'A fájlhoz nem lehet hozzáférni, vagy nem létezik. További információért lépjen kapcsolatba a játékfejlesztővel.',
        'el': 'Το αρχείο δεν ήταν προσβάσιμο ή δεν υπάρχει. Επικοινωνήστε με τον προγραμματιστή του παιχνιδιού για περισσότερες πληροφορίες.',
        'he': 'לא ניתן לגשת לקובץ או שהוא לא קיים. צור קשר עם מפתח המשחק לקבלת מידע נוסף.'
    }

class ProgressLabel():
    UNKNOWN_TIME = {
        'en':'Unknown remaining time',
        'es':'Tiempo restante desconocido',
        'fr':'Temps restant inconnu',
        'pt':'Tempo restante desconhecido',
        'it':'Tempo rimanente sconosciuto',
        'de':'Verbleibende Zeit unbekannt',
        'ru':'Оставшееся время неизвестно',
        'ja':'残り時間不明',
        'zh':'剩余时间未知',
        'ko':'남은 시간을 알 수 없습니다',
        'ar':'الوقت المتبقي غير معروف',
        'tr':'Kalan süre bilinmiyor',
        'pl':'Pozostały czas nieznany',
        'nl':'Onbekende resterende tijd',
        'sv':'Okänd återstående tid',
        'da':'Ukendt resterende tid',
        'fi':'Jäljellä oleva aika tuntematon',
        'no':'Ukjent gjenværende tid',
        'cs':'Zbývající čas není znám',
        'hu':'Ismeretlen hátralévő idő',
        'el':'Άγνωστος υπόλοιπος χρόνος',
        'he':'זמן שנותר לא ידוע'
    }
    A_FEW_SECONDS = {
        'en': 'A few seconds remaining',
        'es': 'Quedan unos segundos',
        'fr': 'Quelques secondes restantes',
        'pt': 'Alguns segundos restantes',
        'it': 'Alcuni secondi rimanenti',
        'de': 'Einige Sekunden verbleiben',
        'ru': 'Осталось несколько секунд',
        'ja': '残りわずかな秒',
        'zh': '剩下几秒',
        'ko': '몇 초 남음',
        'ar': 'بضع ثوانٍ متبقية',
        'tr': 'Birkaç saniye kaldı',
        'pl': 'Pozostało kilka sekund',
        'nl': 'Nog een paar seconden',
        'sv': 'Några sekunder kvar',
        'da': 'Nogle få sekunder tilbage',
        'fi': 'Muutama sekunti jäljellä',
        'no': 'Noen få sekunder igjen',
        'cs': 'Zbývají několik sekund',
        'hu': 'Néhány másodperc van hátra',
        'el': 'Λίγα δευτερόλεπτα παραμένουν',
        'he': 'נשארו כמה שניות'
    }
    DONE = {
        'en': 'Done! Launching game in ',
        'es': '¡Hecho! Iniciando el juego en ',
        'fr': 'Terminé! Lancement du jeu dans ',
        'pt': 'Feito! Iniciando o jogo em ',
        'it': 'Fatto! Avvio del gioco in ',
        'de': 'Fertig! Das Spiel startet in ',
        'ru': 'Готово! Запуск игры в ',
        'ja': '完了！ゲームを起動中 ',
        'zh': '完成！正在启动游戏 ',
        'ko': '완료! 게임 시작 ',
        'ar': 'تم! تشغيل اللعبة في ',
        'tr': 'Bitti! Oyun başlatılıyor ',
        'pl': 'Gotowe! Uruchamianie gry w ',
        'nl': 'Klaar! Game starten in ',
        'sv': 'Klart! Startar spelet i ',
        'da': 'Færdig! Starter spillet i ',
        'fi': 'Valmis! Käynnistetään peli ',
        'no': 'Ferdig! Starter spillet i ',
        'cs': 'Hotovo! Spuštění hry v ',
        'hu': 'Kész! Játék indítása ',
        'el': 'Έγινε! Εκκίνηση παιχνιδιού σε ',
        'he': 'סיים! משחק ההשקה ב '
    }
    SECONDS = {
        'en': ' seconds...',
        'es': ' segundos...',
        'fr': ' secondes...',
        'pt': ' segundos...',
        'it': ' secondi...',
        'de': ' Sekunden...',
        'ru': ' секунд...',
        'ja': ' 秒...',
        'zh': ' 秒...',
        'ko': ' 초...',
        'ar': ' ثواني...',
        'tr': ' saniye...',
        'pl': ' sekund...',
        'nl': ' seconden...',
        'sv': ' sekunder...',
        'da': ' sekunder...',
        'fi': ' sekuntia...',
        'no': ' sekunder...',
        'cs': ' sekund...',
        'hu': ' másodperc...',
        'el': ' δευτερόλεπτα...',
        'he': ' שניות...'
    }
    NO_INTERNET = {
        'es': 'No hay conexión a internet',
        'fr': 'Pas de connexion internet',
        'pt': 'Sem conexão à internet',
        'it': 'Nessuna connessione a Internet',
        'de': 'Keine Internetverbindung',
        'ru': 'Нет подключения к интернету',
        'ja': 'インターネットに接続されていません',
        'zh': '没有网络连接',
        'ko': '인터넷에 연결되어 있지 않습니다',
        'ar': 'لا يوجد اتصال بالإنترنت',
        'tr': 'İnternet bağlantısı yok',
        'pl': 'Brak połączenia z Internetem',
        'nl': 'Geen internetverbinding',
        'sv': 'Ingen internetanslutning',
        'da': 'Ingen internetforbindelse',
        'fi': 'Ei internet-yhteyttä',
        'no': 'Ingen internettilkobling',
        'cs': 'Žádné internetové připojení',
        'hu': 'Nincs internetkapcsolat',
        'el': 'Δεν υπάρχει σύνδεση στο internet',
        'he': 'אין חיבור לאינטרנט',
        'en': 'No internet connection'
    }