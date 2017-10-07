#!/usr/bin/env python3
"Simple proof (test?) of concept for grocery list auto sorting."

class Item(object):
    "An item to be ordered."

    def __init__(self, name):
        self.name = name
        self.avg = 0
        self.vals = []

    def __repr__(self):
        return "%-16s: %4d (%s)" % (self.name, self.avg, self.vals)

    def add_val(self, val):
        "Add another value."
        self.vals.append(val)
        if len(self.vals) > 4:
            self.vals = self.vals[-4:]

        _sum = 0
        for _val in self.vals:
            _sum += _val

        if _sum == 0:
            self.avg = 0
        else:
            self.avg = int(_sum / len(self.vals))
        return self.avg

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

    items = [milk, eggs, flour, salt, candy, macaronies, bread, sour_milk]

    shopping_trip([bread, milk, eggs])
    shopping_trip([milk, salt])
    shopping_trip([sour_milk, eggs, flour, macaronies])
    shopping_trip([bread, sour_milk, eggs, macaronies, candy])
    shopping_trip([sour_milk, eggs])
    shopping_trip([bread, milk, sour_milk, eggs, salt, macaronies])
    shopping_trip([milk, eggs, flour, salt, bread, candy])
    shopping_trip([bread, milk, sour_milk, macaronies])
    shopping_trip([bread, sour_milk, eggs, macaronies, salt])
    shopping_trip([sour_milk, milk, eggs, salt, candy])
    shopping_trip([bread, milk, eggs, flour, macaronies])
    shopping_trip([bread, sour_milk, eggs, macaronies, salt])
    shopping_trip([bread, sour_milk, eggs, macaronies, salt])

    items.sort(key=lambda x: x.avg)
    for item in items:
        print(item)

def shopping_trip(items):
    # todo: handle one or less items
    num_items = len(items)
    
    for index, item in enumerate(items):
        item.add_val(int((index + 1) * 1000 / (num_items + 1)))

        

if __name__ == "__main__":
    main()
