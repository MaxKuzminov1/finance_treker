from .repository import Repository


class Controller:
    def __init__(self):
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