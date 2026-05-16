import sys
import traceback
import MySQLdb
from PyQt6.QtWidgets import QApplication, QMessageBox

# Импорты конфигурации и модулей программы
from references.config import DB_CONFIG
from references.controller import Controller
from main_view import View

# =========================================================
# ЧИСТАЯ СТРУКТУРА БД ДЛЯ РЕЛИЗА
# =========================================================
INIT_SQL = """
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    status ENUM('active', 'blocked') NOT NULL DEFAULT 'active',
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_users_role_id ON users(role_id);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    parent_id INT NULL,
    monthly_limit FLOAT DEFAULT 0.0,
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE INDEX idx_categories_parent ON categories(parent_id);

CREATE TABLE counterparties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50),
    contact_info TEXT,
    address VARCHAR(255),
    requisites VARCHAR(255),
    comment TEXT,
    parent_id INT NULL
);

CREATE TABLE settings (
    `key` VARCHAR(100) PRIMARY KEY,
    `value` TEXT NOT NULL
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    comment TEXT,
    user_id INT NOT NULL,
    counterparty_id INT NULL,
    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_counterparty FOREIGN KEY (counterparty_id) REFERENCES counterparties(id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_user ON transactions(user_id);

CREATE TABLE transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_items_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_items_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_items_category ON transaction_items(category_id);

CREATE TABLE attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    CONSTRAINT fk_attachments_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    CONSTRAINT fk_payments_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);

CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    planned_amount DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_budgets_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX idx_budgets_category ON budgets(category_id);

CREATE TABLE history_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE INDEX idx_history_entity ON history_logs(entity, entity_id);
CREATE INDEX idx_history_user ON history_logs(user_id);

-- ================= ИНИЦИАЛИЗАЦИЯ СИСТЕМНЫХ ДАННЫХ =================
INSERT INTO roles (id, name) VALUES (1, 'Администратор');
INSERT INTO users (id, login, password_hash, role_id, status) VALUES 
(1, 'admin', 'pbkdf2:sha256:150000$dummyhash1', 1, 'active');
INSERT INTO settings (`key`, `value`) VALUES ('theme', 'light'), ('date_format', 'yyyy-MM-dd'), ('currency', 'RUB');
"""


def initialize_database():
    try:
        conn = MySQLdb.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            passwd=DB_CONFIG['passwd'],
            charset="utf8mb4"
        )
        cur = conn.cursor()
        db_name = DB_CONFIG['db']

        cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cur.execute(f"USE {db_name};")

        cur.execute("SHOW TABLES LIKE 'users';")
        if not cur.fetchone():
            statements = INIT_SQL.split(';')
            for statement in statements:
                stmt = statement.strip()
                if stmt:
                    cur.execute(stmt)
            conn.commit()
            print("БД создана!")

        cur.close()
        conn.close()
        return True, ""
    except Exception as e:
        error_trace = traceback.format_exc()
        return False, str(e)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 1. Проверяем и создаем БД
    success, error_msg = initialize_database()
    if not success:
        QMessageBox.critical(
            None,
            "Критическая ошибка базы данных",
            f"Не удалось подключиться к MySQL или создать базу данных.\n\n"
            f"Проверьте, запущен ли сервер MySQL и верны ли данные.\n\nДетали:\n{error_msg}"
        )
        sys.exit(1)

    # 2. Запуск окна
    try:
        controller = Controller()
        view = View(controller)
        view.show()
        sys.exit(app.exec())

    except Exception as e:
        traceback.print_exc()
        QMessageBox.critical(None, "Ошибка", f"Произошла ошибка:\n\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()