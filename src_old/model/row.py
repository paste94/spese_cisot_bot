class Row:
    def __init__(self, price: float, description: str, split: bool = False):
        self.price = price
        self.description = description
        self.split = split

    def __str__(self):
        return f"{self.price} {self.user} {self.description} {'(diviso)' if self.split else ''}"

    def __repr__(self):
        return self.__str__()
        