#!/usr/bin/env python
#!/usr/bin/env python
""" Execute this program once on Unix systems """


# Making Starter executable
import sys
import os
import stat
sys.path.append('Tools')
import Walk


def MakeExecutable(File):
	# Making file executable
	os.chmod(File, stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)

def MakePyExecutable(PythonFile):
	# Making python source file executable
	Content = open(PythonFile).read().replace('\r','')
	open(PythonFile,'w').write('#!/usr/bin/env python\n' + Content)
	MakeExecutable(PythonFile)

print('Fixing problems for Unix platforms\n\n')

print('Making python source files executable...')
Walk.Browse('.', MakePyExecutable, ['.*.py$'], 	Verbose=False)

print('\nMaking "starter" command files executable')
Walk.Browse('.', MakeExecutable, 'starter$', Verbose=True)

print('\nremoving CR chars from all python source files...')
Walk.SubstituteInTree('.', ['.*.py$', 'starter$', '.*.xml$', '.*.txt$', '.*.sh$'], '\\r', '', Verbose=False)

print('Making shell files executable...')
Walk.Browse('.', MakeExecutable, ['.*.sh$'], 	Verbose=True)

print('\nDone')


__author__ = 'Dessalles'
