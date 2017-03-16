@echo off
for /L %%C in (0,10,200) do (
copy /Y "Results_SignalCost_LS=3\SignallingCost_%%C.dat" Courbes.dat
Signals.xls
ren i:\Signals.pdf Signals_SC%%C_LS3.pdf
copy /Y "Results_SignalCost_LS=5\SignallingCost_%%C.dat" Courbes.dat
Signals.xls
ren i:\Signals.pdf Signals_SC%%C_LS5.pdf
)
