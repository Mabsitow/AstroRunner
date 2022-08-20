@echo off
for %%i in (*.png) do pngcrush -ow -rem allb -reduce "%%i"