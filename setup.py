from distutils.core import setup
exec(open('trulyendlesssky/version.py').read())
setup(
  name = 'trulyendlesssky',         # How you named your package folder (MyLib)
  packages = ['trulyendlesssky'],   # Chose the same as "name"
  version=__version__, # this is dynamic!
  license='GPL3',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Truly Endless Sky, helpers to aide in procedural generation of game content for the game "Endless Sky"',   # Give a short description about your library
  author = 'Abram Hindle',                   # Type in your name
  author_email = 'abram.hindle@softwareprocess.es',      # Type in your E-Mail
  url = 'https://github.com/abramhindle/truly-endless-sky',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/abramhindle/truly-endless-sky/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['endlesssky', 'procedural generation', 'endless sky'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'scipy>=1.3.3',
          'forceatlas2>=1,<2',
          'networkx>=2.4',
          'matplotlib>=3.1.2',
          'lark-parser>=0.7.8'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Games/Entertainment',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
