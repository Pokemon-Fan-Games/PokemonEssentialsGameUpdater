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
     def validateVersion(url, update=false)
        internetOpen = Win32API.new(W,'InternetOpenA','plppl','l').call('',0,'','',0)
        open_url = IOU.call(internetOpen,url,nil,0,0x80000000,0)
        if open_url == 0
          Kernel.pbMessage("No hay conexión a internet o no se encontró una nueva versión.")
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
        
        newVersion = txt.split("\n")[0].strip.split("=")[1].strip.to_f
        if GameVersion::POKE_UPDATER_CONFIG
          if newVersion > GameVersion::POKE_UPDATER_CONFIG['CURRENT_GAME_VERSION']
            newVersionText = pbGetPokeUpdaterText('NEW_VERSION', newVersion)  
            
            Kernel.pbMessage(_INTL("#{newVersionText}"))
            if !GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE'] && !update
              if GameVersion::POKE_UPDATER_CONFIG['HAS_UPDATE_BUTTON'] 
                Kernel.pbMessage(_INTL("#{pbGetPokeUpdaterText('BUTTON_UPDATE')}"))
              else
                Kernel.pbMessage(_INTL("#{pbGetPokeUpdaterText('MANUAL_UPDATE')}"))
              end
              return
            end
            
            if GameVersion::POKE_UPDATER_CONFIG['FORCE_UPDATE'] || update
              Kernel.pbMessage(_INTL("#{pbGetPokeUpdaterText('UPDATE')}"))
              IO.popen(GameVersion::POKE_UPDATER_CONFIG['UPDATER_FILENAME'])
              Kernel.exit!
            end
          else
            Kernel.pbMessage(_INTL(pbGetPokeUpdaterText('NO_NEW_VERSION')))
          end 
        end
     end
   end
end