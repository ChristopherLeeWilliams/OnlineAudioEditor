#!c:\users\adrian\desktop\envs\cst205env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'sacad==2.1.1','console_scripts','sacad'
__requires__ = 'sacad==2.1.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('sacad==2.1.1', 'console_scripts', 'sacad')()
    )
