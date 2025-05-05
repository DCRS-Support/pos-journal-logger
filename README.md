# POS Journal Logger
<details>
  <summary>About POS Journal Logger</summary>
  The POS Journal Logger project started from being able to log the data sent from epson receipt printers on pos networks. This can be for receipt printers and order chit/kitchen printers. The use case of this can be applied in practically any POS system and gives you the ability to find out why something didn't print. I wrote this in Python as it wasn't too hard to "emulate" an Epson printer and make a POS system think it is a printer. You can then from the logger itself manipulate the print routings to the destinations. More details below on how this works.
</details>
<details>
  <summary>Windows</summary>
  1. Open cmd.exe as an Administrator.
  
  2. Copy and paste this command:
  curl -L https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/scripts/windows.bat > C:\windows.bat
  3. Press Enter and the windows bat file to set the POS Journal Logger will download to the root of your C drive.
  4. Open File Explorer and navigate to the root of your C drive.
  5. Right click the windows.bat file and run it as Administrator.
</details>

<details>
  <summary>Linux</summary>
  Documentation will be available soon..
</details>
