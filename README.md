# Supermarket POS System
Your team is starting a new project with Super Food, a chain of supermarkets across the 
country. Create a program for Super Food’s point of sale system that uses their pricing 
scheme to calculate the total price for a number of items. 

## Implementation
A given Scheme is defined by a number of "Items" with an id/value and "Rules" with expressions:
```
# Implementation of "Bundled" Scheme
# Items:
{6732} -> 2.49
{4900} -> 3.49
{B1} -> 4.99
...
...
# Rules:
{Bundle} -> {6732}{4900}={B1}
...
```
In the above example, the "Bundled" rule in the scheme is defined by two specific items scanned in the same transaction.  When this rule is applied, the new combined price of these scanned items is equal to _B1_.  By having this scheme file, one is able to add/modify items/rules dynamically without changing any code.

This concept is quite powerful because any arbitrary rule can be defined as long as it contains a mathematically valid expression on the right-hand side, and contains valid items on the left-hand side.  For example, suppose we wanted to add functionality for a coupon on a specific item:
```
# Items:
{8873} -> 2.49
{C1} -> .20

# Rules:
{Coupon} -> {8873}{C1}={8873}-({8873}*{C1})
```
In the above scenario, once item 8873 and coupon C1 is scanned, the price of item 8873 is reduced by 20% of its original price.

Other possible scenarios include reducing/changing tax, charging no/additional tax on specific items, buy X get Y free (or for another price), and so on.

## Assumptions
It is assumed that sales tax is already included in the price of all items (based on the output of the given test scenario).

## Running
Default Scheme file and scenario
```
python3 main.py
```
Custom Scheme file and scenario
```
python3 main.py input\Scheme.txt input\Scenario1.txt
```
_Note_: Requires package numexpr as currently implemented.
```
# Install numexpr
pip install numexpr
```
### Notes
Items need to be defined before Rules in a Scheme file.

Entries in a Scheme file should be formatted properly:
```
# Items - Simple {str} -> float
{str} -> float
# Rules - Left-side of '=' contains 1 or more {str} Items
#         Right-side of '=' can contain {str} Items and/or any valid math operators
{str} -> {str}...{str}=...
```
Certain Items require explicit naming conventions as currently implemented (i.e. Coupons should start with `C`).

Scheme file can have blank lines or comment lines (starting with a `#` character) that will be ignored.
