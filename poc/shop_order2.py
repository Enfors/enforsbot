#!/usr/bin/env python3
"Simple proof (test?) of concept for grocery list auto sorting."

class Item(object):
    "An item to be ordered."

    def __init__(self, name):
        self.name = name
        self.followers = []
        self.preceders = {}

    def __repr__(self):
        output = "%s, preceders: %d" % (self.name, len(self.preceders))
#        for follower in self.followers:
#            output += "\n- %s" % follower.name
        return output

    def add_follower(self, other_item):
        self.followers.append(other_item)

def main():
    "Test this stuff."

    bread = Item("1. bread")
    sour_milk = Item("2. sour milk")
    milk = Item("3. milk")
    eggs = Item("4. eggs")
    flour = Item("5. flour")
    macaronies = Item("6. macaronies")
    salt = Item("7. salt")
    candy = Item("8. candy")

#    items = [bread, sour_milk, milk, eggs, flour, macaronies, salt, candy]
    items = [milk, eggs, flour, salt, candy, macaronies, bread, sour_milk]

    shopping_trip([bread, milk, eggs])
    shopping_trip([milk, salt])
    shopping_trip([sour_milk, eggs, flour, macaronies])
    shopping_trip([bread, sour_milk, eggs, macaronies, candy])
    shopping_trip([sour_milk, eggs])
    shopping_trip([bread, milk, sour_milk, eggs, salt, macaronies])
    shopping_trip([milk, eggs, flour, salt, bread, candy])
    shopping_trip([bread, milk, sour_milk, macaronies])

    for item in items:
        count_preceders(item, start_item=None, already_visited=[])

    items.sort(key=lambda x: len(x.preceders))
    for item in items:
        print(item)

def shopping_trip(items):
    prev_item = None
    for item in items:
        if not prev_item:
            prev_item = item
            continue

        prev_item.add_follower(item)
        prev_item = item
        
def count_preceders(item, start_item=None, already_visited=[]):
    already_visited.append(item)
    
    if not start_item:
        start_item = item
    else:
        item.preceders[start_item] = True
        
    for follower in item.followers:
        if follower not in already_visited:
            count_preceders(follower, start_item, already_visited)
    

if __name__ == "__main__":
    main()
