from .service import ReferencesService
from .repository import ReferencesRepository
from .models import Category, Counterparty, User, AppSettings, CategoryType

class ReferencesController:
    def __init__(self):
        self.repo = ReferencesRepository()
        self.service = ReferencesService(self.repo)

    # Категории
    def get_categories_tree(self):
        return self.service.get_category_tree()

    def get_all_categories(self):
        return self.repo.get_all_categories()

    def get_category_by_id(self, cat_id):
        return self.repo.get_category_by_id(cat_id)

    def add_category(self, name, cat_type, parent_id=None):
        cat = Category(name=name, type=cat_type, parent_id=parent_id)
        return self.service.create_category(cat)

    def update_category(self, cat_id, name, cat_type, parent_id=None):
        cat = Category(id=cat_id, name=name, type=cat_type, parent_id=parent_id)
        self.service.update_category(cat)

    def delete_category(self, cat_id):
        self.service.delete_category(cat_id)

    # Контрагенты
    def get_counterparties(self):
        return self.repo.get_all_counterparties()

    def get_counterparty_by_id(self, cp_id):
        return self.repo.get_counterparty_by_id(cp_id)

    def add_counterparty(self, data: dict):
        cp = Counterparty(**data)
        return self.service.create_counterparty(cp)

    def update_counterparty(self, cp_id, data: dict):
        cp = Counterparty(id=cp_id, **data)
        self.service.update_counterparty(cp)

    def delete_counterparty(self, cp_id):
        self.service.delete_counterparty(cp_id)

    # Пользователи
    def get_users(self):
        return self.repo.get_all_users()

    def get_user_by_id(self, uid):
        return self.repo.get_user_by_id(uid)

    def add_user(self, login, password, role_id, status):
        user = User(login=login, role_id=role_id, status=status)
        return self.service.create_user(user, password)

    def update_user(self, uid, login, role_id, status, password=None):
        user = User(id=uid, login=login, role_id=role_id, status=status)
        self.service.update_user(user, password)

    def delete_user(self, uid):
        self.service.delete_user(uid)

    def get_roles(self):
        return self.service.get_roles()

    # Настройки
    def get_settings(self) -> AppSettings:
        return self.service.get_settings()

    def save_settings(self, settings: AppSettings):
        self.service.save_settings(settings)

    # Экспорт/импорт
    def export_categories_to_csv(self, path):
        import csv
        cats = self.repo.get_all_categories()
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "type", "parent_id"])
            for c in cats:
                writer.writerow([c.id, c.name, c.type.value, c.parent_id or ""])

    def import_categories_from_csv(self, path):
        import csv
        from .models import CategoryType
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat = Category(
                    name=row['name'],
                    type=CategoryType(row['type']),
                    parent_id=int(row['parent_id']) if row.get('parent_id') and row['parent_id'] else None
                )
                self.repo.create_category(cat)

    def export_counterparties_to_csv(self, path):
        import csv
        data = self.get_counterparties()
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "type", "contact_info", "address", "requisites", "comment"])
            for cp in data:
                writer.writerow([cp.name, cp.type, cp.contact_info, cp.address, cp.requisites, cp.comment])

    def import_counterparties_from_csv(self, path):
        import csv
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cp = Counterparty(
                    name=row['name'],
                    type=row.get('type', ''),
                    contact_info=row.get('contact_info', ''),
                    address=row.get('address', ''),
                    requisites=row.get('requisites', ''),
                    comment=row.get('comment', '')
                )
                self.repo.create_counterparty(cp)

    # Пробросьте новые методы из сервиса:
    def merge_categories(self, source_id, target_id):
        self.service.merge_categories(source_id, target_id)

    def get_counterparties_tree(self):
        return self.service.get_counterparty_tree()

    def get_counterparty_summary(self, cp_id):
        return self.service.get_counterparty_summary(cp_id)

    # Обновите сигнатуры add/update
    def add_category(self, name, cat_type, parent_id=None, monthly_limit=0.0):
        cat = Category(name=name, type=cat_type, parent_id=parent_id, monthly_limit=monthly_limit)
        return self.service.create_category(cat)

    def update_category(self, cat_id, name, cat_type, parent_id=None, monthly_limit=0.0):
        cat = Category(id=cat_id, name=name, type=cat_type, parent_id=parent_id, monthly_limit=monthly_limit)
        self.service.update_category(cat)