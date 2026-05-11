
def calculate_total(quantity, price):
    """Calculate the total price for a given quantity and unit price."""
    return quantity * price

def format_currency(amount):
    """Format a number as currency."""
    return f'${amount:,.2f}'