@for /F "tokens=2-4 delims==\" %%A in ('ftype Magick.MVGFile') do @set MagickPath=%%A\%%B\%%C
REM %MagickPath%\convert.exe" -delay 3 *.png -loop 1 EvolifeMovie.gif
%MagickPath%\convert.exe" -delay 3 *.png -loop 1 EvolifeMovie.mpg

