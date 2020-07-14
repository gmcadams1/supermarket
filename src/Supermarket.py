import re
from collections import Counter

class Driver:
    def __init__(self, todaysScheme):
        self.checkout = Checkout(todaysScheme)
    
    def run(self):
        self.checkout.scan("1983") # toothbrush
        self.checkout.scan("4900") # salsa
        self.checkout.scan("8873") # milk
        self.checkout.scan("6732") # chips
        self.checkout.scan("0923") # wine
        self.checkout.scan("1983") # toothbrush
        self.checkout.scan("1983") # toothbrush
        self.checkout.scan("1983") # toothbrush
        cents = self.checkout.getTotal();
        print("Total: " + str(cents))

class Scheme:
    def __init__(self, scheme_input):
        self.scheme_input = scheme_input
        self.items = []
        self.rules = []
        self.read_scheme()
        
    def get_item(self, id):
        return next(filter(lambda i: i.id == id, self.items))
        
    # Get a rule to apply based on items in checkout
    def get_rule(self, items):
        # Rule matches if it's items exist as a subset
        # Get first rule if multiple can apply
        for rule in self.rules:
            # Rule matches
            if not Counter(rule.items) - Counter(items):
                return rule
     
    def read_scheme(self):
        # Read the scheme
        contents = open(self.scheme_input, 'r')
        
        for line in contents:
            (key, val) = line.split('->')
            self.process_scheme(key, val)
            
    def process_scheme(self, key, val):
        # Scheme entry is a Rule
        if '=' in val:
            (items, expression) = val.split('=')
            tot_items = self.get_items(items)
            tot_amount = self.get_expression(expression)
            self.rules.append(Rule(key,tot_items,tot_amount))
        # Scheme entry is an Item
        else:
            item = re.search('\{([^}]+)', key).group(1)
            self.items.append(Item(item,float(eval(val))))
                
    def get_items(self, items):
        item_list = []
        
        items = re.findall('\{([^}]+)', items)
        for item in items:
            item_list.append(next(filter(lambda i: i.id == item, self.items)))
            
        return item_list
    
    def get_expression(self, expression):
        items = set(re.findall('\{([^}]+)', expression))
        
        for item in items:          
            expression = expression.replace('{'+item+'}', 
                str(next(filter(lambda i: i.id == item, self.items)).price))
        
        return eval(expression)
        
class Rule:
    def __init__(self, name, items, amount):
        self.name = name
        self.items = items # [Item1, Item2, ...]
        self.amount = amount # Float
        self.diff = self.price_diff()
        
    def price_diff(self):
        tot = 0
        for item in self.items:
            tot += item.price
            
        return round(self.amount-tot,2)
    
class Item:
    def __init__(self, id, price):
        self.id = id # '1234'
        self.price = price # Float
        
    def __eq__(self, other_id):
        return self.id == other_id
    
    def __hash__(self):
        return hash((self.id, self.price))
        
    def __str__(self):
        return "Item: " + str(self.id) + " " + str(self.price)
    
class Checkout:
    def __init__(self, scheme):
        self.scheme = Scheme(scheme)
        self.items = []
        self.total = 0
      
    def scan(self, id):
        print("Scanning " + id)
        item = self.scheme.get_item(id)
        print("Price " + str(item.price))
        self.total = round(self.total+item.price,2)
        self.items.append(item)
        rule = self.scheme.get_rule(self.items)
        
        if rule:
            # Remove items from list
            for item in rule.items:
                self.items.remove(item)
            # Adjust total price
            self.total = round(self.total+rule.diff,2)
            print("Adjustment " +rule.name+" applied!")
    
    def getTotal(self):
        return self.total
        
if __name__ == '__main__':
    main = Driver('Scheme.txt')
    main.run()