@echo off
for /L %%f in (1,1,9) do (
if EXIST Evolife_schema%%f.dot (
"C:\Program Files (x86)\Graphviz2.24\bin\dot" -Tgif -o Evolife_schema%%f.gif Evolife_schema%%f.dot 
echo Evolife_schema%%f.gif
))

rem dot -Tgif -o Evolife_schema1.gif Evolife_schema1.dot
rem echo Evolife_schema1.gif
