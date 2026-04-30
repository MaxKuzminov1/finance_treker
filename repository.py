import MySQLdb
from MySQLdb.cursors import DictCursor
from config import DB_CONFIG
from MySQLdb import OperationalError


class Repository:
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(
                cursorclass=DictCursor,
                autocommit=True,
                **DB_CONFIG
            )

        except OperationalError as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            print("Проверьте настройки в config.py")
            raise

    def create_transaction(self, data):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO transactions (date, type, total_amount, comment, user_id)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                data["date"],
                data["type"],
                data["total_amount"],
                data["comment"],
                data["user_id"]
            ))

            tid = cur.lastrowid

            for c in data["categories"]:
                cur.execute("""
                    INSERT INTO transaction_items (transaction_id, category_id, amount)
                    VALUES (%s,%s,%s)
                """, (tid, c["category_id"], c["amount"]))

            for p in data["payments"]:
                cur.execute("""
                    INSERT INTO payments (transaction_id, payment_date, amount)
                    VALUES (%s,%s,%s)
                """, (tid, p["date"], p["amount"]))

            self.conn.commit()
            return tid
        finally:
            cur.close()

    def update_transaction(self, tid, data):
        """Обновление существующей транзакции"""
        cur = self.conn.cursor()
        try:
            cur.execute("""
                UPDATE transactions 
                SET date=%s, type=%s, total_amount=%s, comment=%s
                WHERE id=%s
            """, (
                data["date"],
                data["type"],
                data["total_amount"],
                data["comment"],
                tid
            ))

            cur.execute("DELETE FROM transaction_items WHERE transaction_id=%s", (tid,))
            cur.execute("DELETE FROM payments WHERE transaction_id=%s", (tid,))

            for c in data["categories"]:
                cur.execute("""
                    INSERT INTO transaction_items (transaction_id, category_id, amount)
                    VALUES (%s,%s,%s)
                """, (tid, c["category_id"], c["amount"]))

            for p in data["payments"]:
                cur.execute("""
                    INSERT INTO payments (transaction_id, payment_date, amount)
                    VALUES (%s,%s,%s)
                """, (tid, p["date"], p["amount"]))

            self.conn.commit()
        finally:
            cur.close()

    def clear_all_transactions(self):
        """Очистка всех транзакций (для импорта)"""
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM transaction_items")
            cur.execute("DELETE FROM payments")
            cur.execute("DELETE FROM transactions")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
            return False
        finally:
            cur.close()

    def get_transactions(self):
        cur = None
        try:
            cur = self.conn.cursor()
            query = """
                SELECT 
                    t.id, t.date, t.type, t.total_amount, t.comment, t.user_id,
                    COALESCE(SUM(p.amount), 0) as paid,
                    (t.total_amount - COALESCE(SUM(p.amount), 0)) as remaining,
                    GROUP_CONCAT(DISTINCT c.name SEPARATOR ', ') as categories
                FROM transactions t
                LEFT JOIN payments p ON t.id = p.transaction_id
                LEFT JOIN transaction_items ti ON t.id = ti.transaction_id
                LEFT JOIN categories c ON ti.category_id = c.id
                GROUP BY t.id
                ORDER BY t.date DESC
            """
            cur.execute(query)
            transactions = cur.fetchall()

            for t in transactions:
                if t["paid"] >= t["total_amount"]:
                    t["status"] = "Оплачена"
                elif t["paid"] > 0:
                    t["status"] = "Частично"
                else:
                    t["status"] = "Не оплачена"

                if not t["categories"]:
                    t["categories"] = "Без категории"

            return transactions
        except Exception as e:
            print(f"Ошибка при получении транзакций: {e}")
            return []
        finally:
            if cur:
                cur.close()

    def get_transaction_by_id(self, tid):
        """Получение одной транзакции для редактирования"""
        cur = None
        try:
            cur = self.conn.cursor()

            cur.execute("""
                SELECT 
                    t.id, t.date, t.type, t.total_amount, t.comment, t.user_id,
                    COALESCE(SUM(p.amount), 0) as paid,
                    (t.total_amount - COALESCE(SUM(p.amount), 0)) as remaining
                FROM transactions t
                LEFT JOIN payments p ON t.id = p.transaction_id
                WHERE t.id = %s
                GROUP BY t.id
            """, (tid,))

            transaction = cur.fetchone()

            if transaction:
                cur2 = self.conn.cursor()
                try:
                    cur2.execute("""
                        SELECT ti.category_id, ti.amount, c.name
                        FROM transaction_items ti
                        JOIN categories c ON ti.category_id = c.id
                        WHERE ti.transaction_id = %s
                    """, (tid,))
                    transaction["categories"] = cur2.fetchall()
                finally:
                    cur2.close()

                cur3 = self.conn.cursor()
                try:
                    cur3.execute("""
                        SELECT id, payment_date as date, amount
                        FROM payments
                        WHERE transaction_id = %s
                        ORDER BY payment_date
                    """, (tid,))
                    transaction["payments"] = cur3.fetchall()
                finally:
                    cur3.close()

                if transaction["paid"] >= transaction["total_amount"]:
                    transaction["status"] = "Оплачена"
                elif transaction["paid"] > 0:
                    transaction["status"] = "Частично"
                else:
                    transaction["status"] = "Не оплачена"

            return transaction
        except Exception as e:
            print(f"Ошибка при получении транзакции {tid}: {e}")
            return None
        finally:
            if cur:
                cur.close()

    def delete(self, tid):
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM transaction_items WHERE transaction_id=%s", (tid,))
            cur.execute("DELETE FROM payments WHERE transaction_id=%s", (tid,))
            cur.execute("DELETE FROM transactions WHERE id=%s", (tid,))
            self.conn.commit()
        finally:
            cur.close()

    def get_categories(self):
        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            return []
        finally:
            if cur:
                cur.close()

    def import_transactions_batch(self, transactions):
        """Массовый импорт транзакций"""
        cur = self.conn.cursor()
        imported_count = 0
        errors = []

        print(f"Начинаем импорт {len(transactions)} транзакций")

        try:
            for idx, transaction in enumerate(transactions):
                try:
                    print(f"Импорт {idx + 1}: {transaction}")

                    # Вставляем транзакцию
                    cur.execute("""
                        INSERT INTO transactions (date, type, total_amount, comment, user_id)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (
                        transaction["date"],
                        transaction["type"],
                        transaction["total_amount"],
                        transaction.get("comment", ""),
                        1
                    ))

                    tid = cur.lastrowid
                    print(f"  Создана транзакция ID: {tid}")

                    # Вставляем категории
                    for cat in transaction.get("categories", []):
                        category_id = self.get_or_create_category(cat["name"], cur)
                        cur.execute("""
                            INSERT INTO transaction_items (transaction_id, category_id, amount)
                            VALUES (%s,%s,%s)
                        """, (tid, category_id, cat["amount"]))
                        print(f"  Добавлена категория: {cat['name']} (ID: {category_id})")

                    # Вставляем платежи
                    for payment in transaction.get("payments", []):
                        cur.execute("""
                            INSERT INTO payments (transaction_id, payment_date, amount)
                            VALUES (%s,%s,%s)
                        """, (tid, payment["date"], payment["amount"]))
                        print(f"  Добавлен платеж: {payment['date']} - {payment['amount']}")

                    imported_count += 1
                    print(f"✅ Импортирована транзакция {idx + 1}")

                except Exception as e:
                    error_msg = f"Транзакция {idx + 1}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
                    continue

            self.conn.commit()
            print(f"Импорт завершен. Успешно: {imported_count}, Ошибок: {len(errors)}")
            return imported_count, errors

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при импорте: {e}")
            return 0, [str(e)]
        finally:
            cur.close()

    def get_or_create_category(self, category_name, cursor):
        """Получить ID категории или создать новую"""
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
        result = cursor.fetchone()

        if result:
            return result["id"]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
            return cursor.lastrowid

    def refresh_connection(self):
        try:
            self.conn.close()
        except:
            pass
        self.conn = MySQLdb.connect(
            cursorclass=DictCursor,
            autocommit=True,
            **DB_CONFIG
        )
