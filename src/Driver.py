from src.Supermarket import Checkout

__author__ = "Gregory McAdams"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Gregory McAdams"
__email__ = "gmcadams1@comcast.net"
__status__ = "Prototype"

class Driver:
    def __init__(self, todaysScheme):
        self.checkout = Checkout(todaysScheme)
    
    def run(self, input_file=None):
        """
        Run our Supermarket
        """
        if input_file:
            scenario = open(input_file, 'r')
            for item in scenario:
                self.checkout.scan(item.rstrip())

        else:
            self.checkout.scan("1983") # toothbrush
            self.checkout.scan("4900") # salsa
            self.checkout.scan("8873") # milk
            self.checkout.scan("6732") # chips
            self.checkout.scan("0923") # wine
            self.checkout.scan("1983") # toothbrush
            self.checkout.scan("1983") # toothbrush
            self.checkout.scan("1983") # toothbrush
            
        cents = self.checkout.get_total()
        print("Total: " + str(cents))