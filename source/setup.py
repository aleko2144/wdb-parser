
from cx_Freeze import setup, Executable

executables = [Executable('parserWDB.py', targetName='wdb-parser.exe')]

excludes = ['logging', 'unittest', 'email', 'html', 'http', 'urllib',
            'xml', 'pydoc', 'doctest', 'subprocess', 'pickle', 'calendar',
            'tokenize', 'base64', 'bz2', 'fnmatch', 'getopt',
			'quopri', 'imp', 'linecache']

zip_include_packages = ['struct', 'sys', 'argparse', 'os', 'collections', 'encodings', 'importlib']

options = {
    'build_exe': {
        'include_msvcr': True,
		'excludes' : excludes,
        'zip_include_packages': zip_include_packages,
        'build_exe': 'build_windows',
    }
}

setup(name='wdb-parser',
      version='0.0.3',
      description='RnR wdb file parser and converter',
      executables=executables,
      options=options)