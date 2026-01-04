
from app import db
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, Enum, Integer
from sqlalchemy.dialects.mysql import BIGINT, TIMESTAMP

class Products(db.Model):
    __tablename__ = 'products'

    id = Column(BIGINT(unsigned=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(8,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    image = Column(String(255))
    category = Column(Enum('Dog Food', 'Cat Food'), default=None, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now())
    updated_at = Column(TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    stock_status = Column(String(255), nullable=True)  # To show "Low Stock" or "In Stock"

    # Define stock threshold
    STOCK_THRESHOLD = 5

    def __init__(self, name, description, price, quantity, image=None, category=None):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.image = image
        self.category = category

    def update_stock_status(self):
        if self.quantity <= 0:
            self.is_active = 0  # Set product to inactive
            self.stock_status = "Out of Stock"
        elif self.quantity <= self.STOCK_THRESHOLD:
            self.is_active = 1  # Keep it active
            self.stock_status = "Low Stock"
        else:
            self.is_active = 1  # Keep it active
            self.stock_status = "In Stock"
