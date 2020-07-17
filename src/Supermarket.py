import re
import numexpr
from collections import Counter
from abc import ABC

__author__ = "Gregory McAdams"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Gregory McAdams"
__email__ = "gmcadams1@comcast.net"
__status__ = "Prototype"

class Checkout:
    """
    A class representing an object whose functionality 
        is to scan items and calculate their total cost.
        
    Attributes:
    scheme (Scheme): An object representing item pricing/incentives
    pending_items (list): List of Items that have been scanned, 
        but have potential price adjustments depending on future Items
    total (float): Current running total of all items scanned
        including price adjustments
        
    Methods:
    scan(id)
        Scans an item and adds its price to the total.
    getTotal()
        Gets current running total.
    """
    
    def __init__(self, scheme):
        self._scheme = Scheme(scheme)
        # Contains items that may be price-adjusted at some point
        self._pending_items = []
        # Current total price
        self._total = 0
    
    def scan(self, id):
        """
        Scans an item and adds its price to the total.
        
        All items that have potential price adjustments, depending on 
        subsequent items that may be scanned in the future, are stored
        until a price adjustment is applied. The item(s) are removed
        once a price adjustment is made (cannot double discount).
        
        Parameters:
        id (str): Unique id of next item being scanned
        
        >>> c.scan('123') #doctest: +ELLIPSIS
        Scanning 123
        123 not found in Scheme!
        >>> c.scan('8873') #doctest: +ELLIPSIS
        Scanning 8873
        Price 2.49
        >>> c.scan('1983') #doctest: +ELLIPSIS
        Scanning 1983
        Price 1.99
        """
        
        print("Scanning " + id)
        # Get item info from our Scheme
        # If it doesn't exist, exit gracefully
        if (item := self._scheme.get_item(id)) is None:
            return
        # If a Product, print price and add to total
        if isinstance(item,Product):
            print("Price " + str(item.get_value()))
            self._total = round(self._total+item.get_value(),2)
        # If a Coupon, print discount
        # Do not apply to running total
        elif isinstance(item,Coupon):
            print(item.get_percentage() + " off coupon")
        # Add item to pending items if a rule exists that includes it
        # Also get the rule that may or may not meet the criteria yet
        if self._scheme.get_item(item):
            self._pending_items.append(item)
            rule = self._scheme.get_rule(self._pending_items)
        
        # If a rule may apply to the latest item
        if rule:
            self.__apply_rule(rule)
    
    def __apply_rule(self, rule):
        """
        Applies a rule to one or more pending Items that have been scanned.
        
        Parameters:
        rule (Rule): Rule to apply
        """
        
        # Remove items from list only if multiple items exist in rule
        # Single items might be adjusted individually and used later
        if len(rule.get_items()) > 1:
            for item in rule.get_items():
                self._pending_items.remove(item)
        # Adjust total price
        self._total = round(self._total+rule.get_diff(),2)
        print("Adjustment " + rule.get_name() 
                + " " + str(rule.get_diff())
                + " applied!")
    
    def getTotal(self):
        """
        Gets total value of all scannned items plus/minus adjustments applied
        
        Returns:
        str: Total current value
        
        >>> c.getTotal()
        0
        >>> c.scan('8873') #doctest: +ELLIPSIS
        Scanning 8873
        Price 2.49
        >>> c.getTotal()
        2.49
        
        """
        
        return self._total

class Scheme:
    """
    A class representing a scheme.
    
    A scheme is a series of Items with defined values, and Rules
        describing price changes for Items if certain criteria are met.
        
    Attributes:
    scheme_input (str): Raw input Scheme file location
    items (list): List of Items
    rules (list): List of Rules
        
    Methods:
    get_item()
        Get an item that exists in a rule
    get_rule()
        Get a Rule based on given items
    """
    
    def __init__(self, scheme_input):
        # Raw input Scheme file location
        self._scheme_input = scheme_input
        # Items with values ex. {8873} -> 2.49
        self._items = []
        # Rules ex. {Bundle} -> {6732}{4900}={B1}
        self._rules = []
        self.__read_scheme()
       
    def __read_scheme(self):
        """
        Process input Scheme file into a set of items and rules.
        """
        
        # Read the scheme
        contents = open(self._scheme_input, 'r')
        
        for line in contents:
            # If comment line or empty line
            if line.startswith('#') or not line.strip():
                continue
            try:
                (key, val) = line.split(' -> ')
            except ValueError:
                print("Bad scheme entry; not separated by ' -> ': " + line)
            try:
                self.__process_scheme(key, val)
            except (RuntimeError, SyntaxError, TypeError, KeyError, StopIteration):
                print("Issue with processing scheme item: " + line)
    
    def __process_scheme(self, key, val):
        """
        Process an individual Scheme entry.
        
        Parameters:
        key (str): Left-hand side of '->' in a Scheme entry
        val (str): Right-hand side of '->' in a Scheme entry
        """
        
        # Scheme entry is a Rule
        if '=' in val:
            (items, expression) = val.split('=')
            # Get all items required for this rule
            tot_items = self.__required_items(items)
            # Calculate total value adjustment for this rule
            tot_amount = self.__calc_expression(expression)
            self._rules.append(Rule(self.__get_within_brackets(key)[0],tot_items,tot_amount))
        # Scheme entry is an Item
        else:
            item = self.__get_within_brackets(key)[0]
            # Coupons start with 'C'
            if item.startswith('C'):
                self._items.append(Coupon(item,self.__safe_eval(val)))
            # Else a product
            else:
                self._items.append(Product(item,self.__safe_eval(val)))
    
    def __required_items(self, items):
        """
        Get all items required for this rule.
        
        Parameters:
        key (str): Left-hand side of '=' in a Rule
        
        Return:
        list: List of required Items
        """
        
        item_list = []
        
        # Get all items enclosed in brackets
        items = self.__get_within_brackets(items)
        for item in items:
            # Get each item required for the rule
            # Note: Items need to precede rules in Scheme
            try:
                item_list.append(next(filter(lambda i: i.get_id() == item, self._items)))
            except StopIteration:
                print("Item " + item + " not found in Scheme!")
            
        return item_list
    
    def __calc_expression(self, expression):
        """
        Calculate the value adjustment after applying the Rule.
        
        Parameters:
        expression (str): Right-hand side of '=' in a Rule
        
        Return:
        float: Calculated value of expression
        """
        
        # Get all items enclosed in brackets
        # Using set since we are replacing all occurences together
        items = set(self.__get_within_brackets(expression))
        
        for item in items:
            # Replace each item in expression with its value
            try:
                expression = expression.replace('{'+item+'}', 
                    str(next(filter(lambda i: i.get_id() == item, self._items)).get_value()))
            except StopIteration:
                print("Item " + item + " not found in Scheme!")
        
        return self.__safe_eval(expression)    
    
    def __get_within_brackets(self, input):
        """
        Gets all groups of characters found within  each { and }.
        
        Parameters:
        input (str): Input to evaluate
        
        Return:
        list: List of found groups
        """
        
        res = re.findall('\{([^}]+)', input)
        
        if len(res) == 0:
            raise RuntimeError("No expression inside {} for input: " + input)
        
        return res 
    
    def __safe_eval(self, expression):
        """
        Evaluate an arbirary mathemetical expression.
        
        Potential security risks minimized by using numexpr() over eval()
        
        Parameters:
        expression (str): Mathematical expression
        
        Return:
        float: Expression value
        
        Raise:
        SyntaxError, RuntimeError, KeyError, TypeError: Issue with expression
        """
        
        # Safer
        try:
            return numexpr.evaluate(expression).item()
        except (SyntaxError, RuntimeError, KeyError, TypeError):
            print("Issue with expression " + expression)
            raise
        # Less safe
        ##code = compile(expression, "<string>", "eval")
        ##if code.co_names:
            ##raise NameError("Use of names not allowed")
        ##return eval(code, {"__builtins__": {}}, {})
    
    def get_item(self, id):
        """
        Gets an item that exists in a rule based on its unique id
        
        Parameters:
        id (str): Unique id of item
        
        Returns:
        str: Item that exists in a rule
        
        >>> s.get_item('123')
        123 not found in Scheme!
        >>> s.get_item('8873') #doctest: +ELLIPSIS
        <__main__.Product object at 0x...>
        """
        
        try:
            return next(filter(lambda i: i.get_id() == id, self._items))
        except StopIteration:
            print(id + " not found in Scheme!")
       
    def get_rule(self, items):
        """
        Get the best rule to apply based on pending items in checkout.
        
        Parameters:
        items (list): List of pending items
        
        Returns:
        Rule: Rule to apply at checkout
        
        >>> s.get_rule([Product('123',123)])
        >>> s.get_rule([s.get_item('8873')])
        >>> s.get_rule([s.get_item('8873'),s.get_item('C1')]) #doctest: +ELLIPSIS
        <__main__.Rule object at 0x...>
        """
        
        # Keep track of the best rule to use
        best_rule = None
        best_count = float('inf')
        # Rule matches if it's items exist as a subset 
        #   to the total pending items in checkout.
        for rule in self._rules:
            # A valid rule will apply to latest item (optimization)
            if items[-1] not in rule.get_items():
                continue
            # Rule matches based on current pending items in checkout
            if not Counter(rule.get_items()) - Counter(items):
                # Get closest rule if multiple can apply
                # Closest = most matched items = lowest sum in the difference
                best_sum = sum((Counter(items)-Counter(rule.get_items())).values())
                if  best_sum < best_count:
                    best_rule = rule
                    best_count = best_sum
        
        return best_rule
        
class Rule:
    """
    A class representing a rule in a scheme.
        
    Attributes:
    name (str): Unique name
    items (list): List of Items used in this Rule
    amount (float): Value of the expression
    diff (float): Price difference between the normal 
        price of all Items and the Rule's expression value
    """
    
    def __init__(self, name, items, amount):
        # Unique name of rule
        self._name = name
        # Required items
        self._items = items # [Item1, Item2, ...]
        # Amount adjusted
        self._amount = amount # Float
        self._diff = self.__price_diff()
      
    def __str__(self):
        return self._name
      
    def __price_diff(self):
        """
        Calculate amount to adjust current checkout total.
        
        Returns:
        float: Amount to adjust
        """
        
        tot = 0
        # Adjust price of each previously scanned Product
        # Does not apply to Coupons since they were not
        #   added to checkout total originally
        for item in self._items:
            if isinstance(item,Product):
                tot += item.get_value()
          
        # Round to nearest cent
        return round(self._amount-tot,2)

    def get_name(self):
        return self._name
    
    def get_items(self):
        return self._items
    
    def get_diff(self):
        return self._diff

class Item(ABC):
    """
    A class representing an abstract item.
        
    Attributes:
    id (str): Unique id
    value (float): Value of Item
    """
    
    def __init__(self, id, value):
        # Unique id of Item
        self._id = id # '1234'
        # Value of Item
        self._value = value # float
        
    def __eq__(self, other_id):
        return self._id == other_id
    
    def __hash__(self):
        return hash((self._id, self._value))
        
    def __str__(self):
        return str(self._id) + "," + str(self._value)
        
    def get_id(self):
        return self._id
        
    def get_value(self):
        return self._value

class Product(Item):
    """
    A class representing a Product item.
    """
    
    def __init__(self, id, price):
        Item.__init__(self, id, price)

class Coupon(Item):
    """
    A class representing a Coupon item.
    
    Methods:
    get_percentage()
        Get percentage to print
    """
    
    def __init__(self, id, discount):
        Item.__init__(self, id, discount)
        
    def get_percentage(self):
        """
        Returns formatted percentage
        
        Returns:
        str: Formatted output
        
        >>> cou.get_percentage()
        '50.0%'
        """
        
        return str(round(self._value*100,2))+"%"
        
if __name__ == '__main__':
    import doctest
    doctest.testmod(extraglobs={'s': Scheme('input\TestScheme.txt'), 
                                'cou': Coupon('CT',0.5),
                                'c': Checkout('input\TestScheme.txt')})