"""
Written by Craig B.
https://github.com/Phatkone
           ,,,
          (. .)
-------ooO-(_)-Ooo-------
In Collaboration with Mills2000
"""

import vmanage
import time
import sys


def main(**kwargs):
    run = True
    while run:
        try: 
            vmanage.main()
            time.sleep(86400)
        except KeyboardInterrupt:
            run = False

if __name__ == '__main__':
    kwargs = dict(arg.split("=",1) for arg in sys.argv[1:])
    main(**kwargs)