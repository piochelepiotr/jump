@echo off
for /L %%C in (40,40,120) do (
for /L %%R in (20,20,60) do (
copy /Y "signallingcost_%%C_rankeffect=%%R.dat" Courbes.dat
Signals.xls
ren i:\Signals.pdf "Signals_SC=%%C_RE=%%R.pdf"
)
)