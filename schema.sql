-- ============================================================
--  IT Helpdesk Ticket System — MySQL Schema
--  Run: mysql -u root -p helpdesk < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS helpdesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE helpdesk;

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100)  NOT NULL,
    email      VARCHAR(150)  NOT NULL UNIQUE,
    password   VARCHAR(255)  NOT NULL,
    role       ENUM('user','admin') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed: default admin account (password: Admin@123)
INSERT INTO users (name, email, password, role) VALUES
('IT Admin', 'admin@helpdesk.local',
 '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',   -- Admin@123
 'admin')
ON DUPLICATE KEY UPDATE id=id;

-- ── Tickets ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tickets (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id     VARCHAR(20)  NOT NULL UNIQUE,
    user_id       INT          NOT NULL,
    assigned_to   INT,
    title         VARCHAR(200) NOT NULL,
    category      ENUM('Network','Hardware','Software','Email','Password','Other') NOT NULL,
    priority      ENUM('Low','Medium','High','Critical') NOT NULL DEFAULT 'Medium',
    description   TEXT         NOT NULL,
    auto_response TEXT,
    resolution    TEXT,
    status        ENUM('Open','In Progress','Resolved','Closed') NOT NULL DEFAULT 'Open',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)     REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- ── Comments / Thread ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id  INT  NOT NULL,
    user_id    INT  NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)   REFERENCES users(id)
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX idx_tickets_status   ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_user     ON tickets(user_id);
