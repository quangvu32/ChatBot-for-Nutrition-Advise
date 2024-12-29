import re

MeasurementConversions = [
    { "Name": "Tablespoon", "ValueInGrams": 14.79 },
    { "Name": "Ounce", "ValueInGrams": 28.35 },
    { "Name": "Cup", "ValueInGrams": 240 },
    { "Name": "Teaspoon", "ValueInGrams": 4.93 },
    { "Name": "Pound", "ValueInGrams": 453.59 },
    { "Name": "Liter", "ValueInGrams": 1000 },
    { "Name": "Gallon", "ValueInGrams": 3785 },
    { "Name": "Kilogram", "ValueInGrams": 1000}
]

def convert_to_grams(food_list):
    unit_to_grams = {unit["Name"].lower(): unit["ValueInGrams"] for unit in MeasurementConversions}
    
    converted_food_list = []

    for item in food_list:
        food_name = item['food']
        amount_str = item['amount']
        
        amount_parts = re.match(r"([0-9\.]+)\s*(\w+)", amount_str)
        
        if amount_parts:
            amount_value = float(amount_parts.group(1))  
            unit = amount_parts.group(2).lower()  
            
            if unit == "grams":
                converted_food_list.append({'food': food_name, 'amount': amount_value})
            elif unit == "milliliters" and "liter" in unit_to_grams:
                converted_food_list.append({'food': food_name, 'amount': amount_value * unit_to_grams["liter"] / 1000})
            elif unit in unit_to_grams:
                converted_food_list.append({'food': food_name, 'amount': amount_value * unit_to_grams[unit]})
            else:
                converted_food_list.append({'food': food_name, 'amount': amount_value})

    return converted_food_list

