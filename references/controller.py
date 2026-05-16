# references/controller.py
import MySQLdb
from .repository import Repository


class DBController:
    def __init__(self):
        self.conn = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="root",
            db="finance_db",
            charset="utf8mb4",
            autocommit=True  # ВАЖНО: Включаем автокоммит для этого подключения!
        )

    def execute(self, query, params=None, fetch=False):
        # Принудительно завершаем старые транзакции перед новым запросом,
        # чтобы сбросить снимок (snapshot) REPEATABLE READ в MySQL
        # и гарантированно получить самые свежие данные из других модулей.
        self.conn.commit()

        cursor = self.conn.cursor()
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result

        self.conn.commit()
        cursor.close()


class Controller(DBController):  # Наследуем от DBController
    def __init__(self):
        super().__init__()  # Инициализируем DBController
        self.repository = Repository()

    def create(self, data):
        return self.repository.create_transaction(data)

    def update(self, tid, data):
        return self.repository.update_transaction(tid, data)

    def get_all(self):
        return self.repository.get_transactions()

    def get_by_id(self, tid):
        return self.repository.get_transaction_by_id(tid)

    def delete(self, tid):
        return self.repository.delete(tid)

    def get_categories(self):
        return self.repository.get_categories()

    def clear_all_transactions(self):
        return self.repository.clear_all_transactions()

    def import_transactions(self, transactions):
        return self.repository.import_transactions_batch(transactions)

    def refresh_db(self):
        return self.repository.refresh_connection()