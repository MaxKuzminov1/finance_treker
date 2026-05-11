import MySQLdb
from MySQLdb.cursors import DictCursor
from references.config import DB_CONFIG
from .models import Category, Counterparty, User, Role, AppSettings, CategoryType, UserStatus
from typing import Optional, List

class ReferencesRepository:
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(cursorclass=DictCursor, autocommit=True, **DB_CONFIG)
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            raise

    # ---------- Категории ----------
    def get_all_categories(self) -> list:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT id, name, type, parent_id, monthly_limit FROM categories ORDER BY name")
            return [Category(**row) for row in cur.fetchall()]
        finally:
            cur.close()

    def get_category_by_id(self, cat_id: int) -> Optional[Category]:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT id, name, type, parent_id, monthly_limit FROM categories WHERE id=%s", (cat_id,))
            row = cur.fetchone()
            return Category(**row) if row else None
        finally:
            cur.close()

    def create_category(self, cat: Category) -> int:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO categories (name, type, parent_id, monthly_limit) VALUES (%s,%s,%s,%s)",
                (cat.name, cat.type.value, cat.parent_id, cat.monthly_limit)
            )
            return cur.lastrowid
        finally:
            cur.close()

    def update_category(self, cat: Category):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "UPDATE categories SET name=%s, type=%s, parent_id=%s, monthly_limit=%s WHERE id=%s",
                (cat.name, cat.type.value, cat.parent_id, cat.monthly_limit, cat.id)
            )
        finally:
            cur.close()

    def delete_category(self, cat_id: int) -> bool:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) as cnt FROM transaction_items WHERE category_id=%s", (cat_id,))
            if cur.fetchone()["cnt"] > 0: return False
            cur.execute("DELETE FROM categories WHERE id=%s", (cat_id,))
            return True
        finally:
            cur.close()

    def merge_categories(self, source_id: int, target_id: int):
        cur = self.conn.cursor()
        try:
            # Перепривязываем транзакции
            cur.execute("UPDATE transaction_items SET category_id=%s WHERE category_id=%s", (target_id, source_id))
            # Перепривязываем дочерние категории
            cur.execute("UPDATE categories SET parent_id=%s WHERE parent_id=%s", (target_id, source_id))
            # Удаляем старую
            cur.execute("DELETE FROM categories WHERE id=%s", (source_id,))
        finally:
            cur.close()

    # ---------- Контрагенты ----------
    def get_all_counterparties(self) -> list:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT id, name, type, contact_info, address, requisites, comment, parent_id FROM counterparties ORDER BY name")
            return [Counterparty(**row) for row in cur.fetchall()]
        finally:
            cur.close()

    def get_counterparty_by_id(self, cp_id: int) -> Optional[Counterparty]:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT id, name, type, contact_info, address, requisites, comment, parent_id FROM counterparties WHERE id=%s", (cp_id,))
            row = cur.fetchone()
            return Counterparty(**row) if row else None
        finally:
            cur.close()

    def create_counterparty(self, cp: Counterparty) -> int:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO counterparties (name, type, contact_info, address, requisites, comment, parent_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (cp.name, cp.type, cp.contact_info, cp.address, cp.requisites, cp.comment, cp.parent_id)
            )
            return cur.lastrowid
        finally:
            cur.close()

    def update_counterparty(self, cp: Counterparty):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "UPDATE counterparties SET name=%s, type=%s, contact_info=%s, address=%s, requisites=%s, comment=%s, parent_id=%s WHERE id=%s",
                (cp.name, cp.type, cp.contact_info, cp.address, cp.requisites, cp.comment, cp.parent_id, cp.id)
            )
        finally:
            cur.close()

    def delete_counterparty(self, cp_id: int) -> bool:
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM counterparties WHERE id=%s", (cp_id,))
            return True
        finally:
            cur.close()

    def get_counterparty_summary(self, cp_id: int) -> dict:
        cur = self.conn.cursor()
        try:
            # Заглушка запроса к таблице транзакций (замените названия полей под вашу БД)
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_paid,
                    SUM(CASE WHEN type='income' THEN amount ELSE -amount END) as current_debt,
                    MAX(date) as last_date
                FROM transactions 
                WHERE counterparty_id=%s
            """, (cp_id,))
            row = cur.fetchone()
            return {
                "total_paid": row.get("total_paid") or 0.0,
                "current_debt": row.get("current_debt") or 0.0,
                "last_date": row.get("last_date")
            }
        except:
            return {"total_paid": 0.0, "current_debt": 0.0, "last_date": None}
        finally:
            cur.close()

    # (Методы пользователей, ролей и настроек остаются без изменений)
    # ---------- Пользователи ----------
    def get_all_users(self) -> list:
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT u.id, u.login, u.password_hash, u.role_id, u.status, r.name as role_name
                FROM users u
                JOIN roles r ON u.role_id = r.id
                ORDER BY u.login
            """)
            return [User(**row) for row in cur.fetchall()]
        finally:
            cur.close()

    def get_user_by_id(self, uid: int) -> Optional[User]:
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT u.id, u.login, u.password_hash, u.role_id, u.status, r.name as role_name
                FROM users u JOIN roles r ON u.role_id = r.id
                WHERE u.id=%s
            """, (uid,))
            row = cur.fetchone()
            return User(**row) if row else None
        finally:
            cur.close()

    def create_user(self, user: User) -> int:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (login, password_hash, role_id, status) VALUES (%s,%s,%s,%s)",
                (user.login, user.password_hash, user.role_id, user.status.value)
            )
            return cur.lastrowid
        finally:
            cur.close()

    def update_user(self, user: User):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET login=%s, role_id=%s, status=%s WHERE id=%s",
                (user.login, user.role_id, user.status.value, user.id)
            )
            if user.password_hash:
                cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (user.password_hash, user.id))
        finally:
            cur.close()

    def delete_user(self, uid: int) -> bool:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id=%s", (uid,))
            if cur.fetchone()["cnt"] > 0:
                return False
            cur.execute("DELETE FROM users WHERE id=%s", (uid,))
            return True
        finally:
            cur.close()

    # ---------- Роли ----------
    def get_all_roles(self) -> list:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT id, name FROM roles ORDER BY name")
            return [Role(**row) for row in cur.fetchall()]
        finally:
            cur.close()

    # ---------- Настройки ----------
    def load_settings(self) -> AppSettings:
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT `key`, `value` FROM settings")
            rows = cur.fetchall()
            settings_dict = {r['key']: r['value'] for r in rows}
        except:
            settings_dict = {}
        finally:
            cur.close()
        s = AppSettings()
        if settings_dict:
            s.theme = settings_dict.get("theme", s.theme)
            s.date_format = settings_dict.get("date_format", s.date_format)
            s.auto_refresh = settings_dict.get("auto_refresh", "0") == "1"
            s.recurring_enabled = settings_dict.get("recurring_enabled", "0") == "1"
            s.logging_enabled = settings_dict.get("logging_enabled", "1") == "1"
        return s

    def save_settings(self, settings: AppSettings):
        cur = self.conn.cursor()
        try:
            data = {
                "theme": settings.theme,
                "date_format": settings.date_format,
                "auto_refresh": "1" if settings.auto_refresh else "0",
                "recurring_enabled": "1" if settings.recurring_enabled else "0",
                "logging_enabled": "1" if settings.logging_enabled else "0",
            }
            for key, val in data.items():
                cur.execute("""
                    INSERT INTO settings (`key`, `value`) VALUES (%s,%s)
                    ON DUPLICATE KEY UPDATE `value`=%s
                """, (key, val, val))
        finally:
            cur.close()

    # Логирование
    def log_action(self, entity, entity_id, action, user_id=1):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO history_logs (entity, entity_id, action, user_id) VALUES (%s,%s,%s,%s)",
                (entity, entity_id, action, user_id)
            )
        finally:
            cur.close()