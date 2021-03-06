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
        Run our Supermarket scenario.
        
        Parameters:
        input_file (str): Raw Scenario input file location
        """
        
        # Custom scenario
        if input_file:
            with open(input_file, 'r') as scenario:
                for item in scenario:
                    self.checkout.scan(item.rstrip())

        # Default scenario
        else:
            self.checkout.scan("1983") # toothbrush
            self.checkout.scan("4900") # salsa
            self.checkout.scan("8873") # milk
            self.checkout.scan("6732") # chips
            self.checkout.scan("0923") # wine
            self.checkout.scan("1983") # toothbrush
            self.checkout.scan("1983") # toothbrush
            self.checkout.scan("1983") # toothbrush
            
        # Get our final total
        cents = self.checkout.getTotal()
        print("Total: " + str(cents))