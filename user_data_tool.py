import sqlite3
from datetime import datetime, timedelta

def init_user_db():
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_reports (
                        [Main food] TEXT,
                        [WWEIA Category] TEXT,
                        [Energy (kcal)] TEXT,
                        [Protein (g)] TEXT,
                        [Carbohydrate (g)] TEXT,
                        [Sugars, total (g)] TEXT,
                        [Fiber, total dietary (g)] TEXT,
                        [Total Fat (g)] TEXT,
                        [Fatty acids, total saturated (g)] TEXT,
                        [Fatty acids, total monounsaturated (g)] TEXT,
                        [Fatty acids, total polyunsaturated (g)] TEXT,
                        [Cholesterol (mg)] TEXT,
                        [Retinol (mcg)] TEXT,
                        [Vitamin A, RAE (mcg_RAE)] TEXT,
                        [Carotene, alpha (mcg)] TEXT,
                        [Carotene, beta (mcg)] TEXT,
                        [Cryptoxanthin, beta (mcg)] TEXT,
                        [Lycopene (mcg)] TEXT,
                        [Lutein + zeaxanthin (mcg)] TEXT,
                        [Thiamin (mg)] TEXT,
                        [Riboflavin (mg)] TEXT,
                        [Niacin (mg)] TEXT,
                        [Vitamin B-6 (mg)] TEXT,
                        [Folic acid (mcg)] TEXT,
                        [Folate, food (mcg)] TEXT,
                        [Folate, DFE (mcg_DFE)] TEXT,
                        [Folate, total (mcg)] TEXT,
                        [Choline, total (mg)] TEXT,
                        [Vitamin B-12 (mcg)] TEXT,
                        [Vitamin B-12, added (mcg)] TEXT,
                        [Vitamin C (mg)] TEXT,
                        [Vitamin D (D2 + D3) (mcg)] TEXT,
                        [Vitamin E (alpha-tocopherol) (mg)] TEXT,
                        [Vitamin E, added (mg)] TEXT,
                        [Vitamin K (phylloquinone) (mcg)] TEXT,
                        [Calcium (mg)] TEXT,
                        [Phosphorus (mg)] TEXT,
                        [Magnesium (mg)] TEXT,
                        [Iron (mg)] TEXT,
                        [Zinc (mg)] TEXT,
                        [Copper (mg)] TEXT,
                        [Selenium (mcg)] TEXT,
                        [Potassium (mg)] TEXT,
                        [Sodium (mg)] TEXT,
                        [Caffeine (mg)] TEXT,
                        [Theobromine (mg)] TEXT,
                        [Alcohol (g)] TEXT,
                        [Water (g)] TEXT,
                        [Amount (g)] TEXT,
                        [date] TEXT
                    )''')
    conn.commit()
    conn.close()

def insert_user_data(data: list, amount: float, date_adj=0):
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    # Get current date and time
    current_date = datetime.now()
    adjusted_date = current_date + timedelta(days=date_adj)
    adjusted_date_str = adjusted_date.strftime("%Y-%m-%d")

    scaled_data = [
        (float(value) * amount / 100 if i > 1 else value) 
        for i, value in enumerate(data)
    ]

    scaled_data.append(amount)
    scaled_data.append(adjusted_date_str)

    # Insert into table
    cursor.execute('''INSERT INTO user_reports (
                        [Main food], [WWEIA Category], [Energy (kcal)], [Protein (g)],
                        [Carbohydrate (g)], [Sugars, total (g)], [Fiber, total dietary (g)],
                        [Total Fat (g)], [Fatty acids, total saturated (g)],
                        [Fatty acids, total monounsaturated (g)],
                        [Fatty acids, total polyunsaturated (g)], [Cholesterol (mg)],
                        [Retinol (mcg)], [Vitamin A, RAE (mcg_RAE)], [Carotene, alpha (mcg)],
                        [Carotene, beta (mcg)], [Cryptoxanthin, beta (mcg)], [Lycopene (mcg)],
                        [Lutein + zeaxanthin (mcg)], [Thiamin (mg)], [Riboflavin (mg)],
                        [Niacin (mg)], [Vitamin B-6 (mg)], [Folic acid (mcg)],
                        [Folate, food (mcg)], [Folate, DFE (mcg_DFE)], [Folate, total (mcg)],
                        [Choline, total (mg)], [Vitamin B-12 (mcg)], [Vitamin B-12, added (mcg)],
                        [Vitamin C (mg)], [Vitamin D (D2 + D3) (mcg)],
                        [Vitamin E (alpha-tocopherol) (mg)], [Vitamin E, added (mg)],
                        [Vitamin K (phylloquinone) (mcg)], [Calcium (mg)], [Phosphorus (mg)],
                        [Magnesium (mg)], [Iron (mg)], [Zinc (mg)], [Copper (mg)],
                        [Selenium (mcg)], [Potassium (mg)], [Sodium (mg)],
                        [Caffeine (mg)], [Theobromine (mg)], [Alcohol (g)],
                        [Water (g)], [Amount (g)], [date]
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', tuple(scaled_data))

    conn.commit()
    conn.close()
    print('thank god')

def search_nutrition(ingredient):
    try:
        conn = sqlite3.connect("nutrition.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM 'nutrition' WHERE [Main food] LIKE ?", (f"%{ingredient}%",))
        result = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        result = []
    finally:
        conn.close()
    return result

# View all diet progress
def view_diet():
    try:
        conn = sqlite3.connect("nutrition.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_reports")
        results = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        results.insert(0, column_names)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        results = []
    finally:
        conn.close()
    return results