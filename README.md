# POS Journal Logger
<details>
  <summary>About POS Journal Logger</summary>
  The POS Journal Logger project started from being able to log the data sent from epson receipt printers on pos networks. This can be for receipt printers and order chit/kitchen printers. The use case of this can be applied in practically any POS system and gives you the ability to find out why something didn't print. I wrote this in Python as it wasn't too hard to "emulate" an Epson printer and make a POS system think it is a printer. You can then from the logger itself manipulate the print routings to the destinations. More details below on how this works.
</details>
<details>
  <summary>Windows</summary>
  
  1. Open Powershell/Terminal as an Administrator.
  
  2. Copy and paste this command:
  
  irm https://raw.githubusercontent.com/DCRS-Support/pos-journal-logger/refs/heads/main/scripts/windows.ps1 | iex
  
  3. The server/computer this is installed on will reboot at the end then you can test!
  
</details>

<details>
  <summary>Linux</summary>
  Documentation will be available soon..
</details>
