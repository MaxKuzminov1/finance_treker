class Service:
    def __init__(self, repo):
        self.repo = repo

    def create(self, data):
        if data["amount"] <= 0:
            raise Exception("Сумма > 0")

        total = sum(c["amount"] for c in data["categories"])
        if abs(total - data["amount"]) > 0.01:
            raise Exception("Сумма категорий != общей")

        self.repo.create_transaction(data)

    def list(self):
        rows = self.repo.get_transactions()

        for r in rows:
            if r["paid"] >= r["total_amount"]:
                r["status"] = "Оплачено"
            elif r["paid"] > 0:
                r["status"] = "Частично"
            else:
                r["status"] = "Создана"

            r["remaining"] = r["total_amount"] - r["paid"]

        return rows

    def delete(self, tid):
        self.repo.delete(tid)

    def get_categories(self):
        return self.repo.get_categories()