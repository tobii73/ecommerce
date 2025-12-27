class ProductModel:
    def __init__(self, name, price, business_id, description=None):
        self.name = name
        self.price = price
        self.description = description
        self.business_id = business_id