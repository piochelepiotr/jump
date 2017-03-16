@for /F "tokens=2-4 delims==\" %%A in ('ftype Magick.MVGFile') do @set MagickPath=%%A\%%B\%%C
%MagickPath%\convert.exe" -delay 3 ___CF_0*.png -loop 1 EvolifeMovie.mpg
