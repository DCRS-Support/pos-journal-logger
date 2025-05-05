@echo off

TASKKILL /f /im "pythonservice.exe*"

timeout 2

sc start pos-journal-logger
