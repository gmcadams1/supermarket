import sys
from src.Driver import *

__author__ = "Gregory McAdams"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Gregory McAdams"
__email__ = "gmcadams1@comcast.net"
__status__ = "Prototype"

if __name__ == '__main__':
    if len(sys.argv) > 3:
        print("Usage: <Scheme.txt> (<input_file.txt>)")
        sys.exit()
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        # Pass Scheme file to Driver
        main = Driver(sys.argv[1])
        # If Items from input file
        if len(sys.argv) == 3:
            # Run custom scenario
            main.run(sys.argv[2])
        # Internal test scenario
        else:
            main.run()

    # Run default
    else:
        main = Driver('input\Scheme.txt')
        main.run()