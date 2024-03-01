import io
import subprocess
import sys
import os

icon = 'icon.ico'

venv = os.environ.get('VIRTUAL_ENV')
if venv:
	# pyinstaller ignores virtual environment so we need to add the packages manually
	packagesDir = venv + r'\Lib\site-packages'

	# it also does not follow egg-links
	try:
		with io.open(packagesDir + r'\easy-install.pth', 'rt') as reqs:
			paths = ';'.join([packagesDir] + reqs.read().splitlines())
	except:
		paths = packagesDir

subprocess.run(['pyinstaller', '--onefile', '--icon', icon, '--paths', paths if venv else '', 'main.py', '-n', 'SubLeecher'],
               stdout=sys.stdout,
               stderr=sys.stderr)
