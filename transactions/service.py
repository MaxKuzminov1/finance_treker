import hashlib
from .models import Category, Counterparty, User, AppSettings, CategoryType, UserStatus
from .repository import ReferencesRepository

class ReferencesService:
    def __init__(self, repo: ReferencesRepository):
        self.repo = repo

    # ---------- Категории ----------
    def get_category_tree(self):
        all_cats = self.repo.get_all_categories()
        cat_map = {c.id: c for c in all_cats}
        roots = []
        for c in all_cats:
            if c.parent_id and c.parent_id in cat_map:
                cat_map[c.parent_id].children.append(c)
            else:
                c.parent_id = None
                roots.append(c)
        # Убираем детей из корневого списка, если они уже вложены
        return [c for c in roots if c.parent_id is None]

    def validate_category(self, cat: Category):
        if not cat.name.strip():
            raise ValueError("Название категории обязательно")
        if cat.parent_id == cat.id:
            raise ValueError("Категория не может быть родителем сама себе")

    def create_category(self, cat: Category):
        self.validate_category(cat)
        new_id = self.repo.create_category(cat)
        self.repo.log_action("category", new_id, "create")
        return new_id

    def update_category(self, cat: Category):
        self.validate_category(cat)
        self.repo.update_category(cat)
        self.repo.log_action("category", cat.id, "update")

    def delete_category(self, cat_id: int):
        if self.repo.is_category_used(cat_id):
            raise ValueError("Невозможно удалить категорию, она используется в операциях")
        self.repo.delete_category(cat_id)
        self.repo.log_action("category", cat_id, "delete")

    # ---------- Контрагенты ----------
    def validate_counterparty(self, cp: Counterparty):
        if not cp.name.strip():
            raise ValueError("Название контрагента обязательно")

    def create_counterparty(self, cp: Counterparty):
        self.validate_counterparty(cp)
        new_id = self.repo.create_counterparty(cp)
        self.repo.log_action("counterparty", new_id, "create")
        return new_id

    def update_counterparty(self, cp: Counterparty):
        self.validate_counterparty(cp)
        self.repo.update_counterparty(cp)
        self.repo.log_action("counterparty", cp.id, "update")

    def delete_counterparty(self, cp_id: int):
        self.repo.delete_counterparty(cp_id)
        self.repo.log_action("counterparty", cp_id, "delete")

    # ---------- Пользователи ----------
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_user(self, user: User):
        if not user.login.strip():
            raise ValueError("Логин обязателен")
        # проверка уникальности логина при создании (реализуется в контроллере)

    def create_user(self, user: User, plain_password: str):
        self.validate_user(user)
        user.password_hash = self.hash_password(plain_password)
        new_id = self.repo.create_user(user)
        self.repo.log_action("user", new_id, "create")
        return new_id

    def update_user(self, user: User, plain_password: str = None):
        self.validate_user(user)
        if plain_password:
            user.password_hash = self.hash_password(plain_password)
        else:
            user.password_hash = ""  # не менять
        self.repo.update_user(user)
        self.repo.log_action("user", user.id, "update")

    def delete_user(self, uid: int):
        if not self.repo.delete_user(uid):
            raise ValueError("Невозможно удалить пользователя, у него есть транзакции")
        self.repo.log_action("user", uid, "delete")

    # ---------- Настройки ----------
    def get_settings(self) -> AppSettings:
        return self.repo.load_settings()

    def save_settings(self, settings: AppSettings):
        self.repo.save_settings(settings)
        self.repo.log_action("settings", 0, "update")

    # ---------- Роли ----------
    def get_roles(self):
        return self.repo.get_all_roles()