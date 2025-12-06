# Bookstore — Flask Backend + Tkinter Client

## Quick Start

### 1️⃣ Setup MySQL Database
```bash
mysql -u root -p -e "CREATE DATABASE bookstore;"
```

### 2️⃣ Configure Environment
```bash
cp .env.template .env
# Edit .env and fill in:
# - DATABASE_URL with your MySQL password
# - JWT_SECRET_KEY (generate random string)
# - SMTP settings if you want email (optional)
```

Generate JWT secret:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3️⃣ Install & Run Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.backend.app
```

Runs on `http://127.0.0.1:5000`

### 4️⃣ Run Client (another terminal)
```bash
source .venv/bin/activate
python -m src.client.gui
```

## Features Implemented (based on the instrucntion I was given in class)

✅ **FR1** — User registration & login (secure password hashing with bcrypt)  
✅ **FR2** — Book search by title/author, display with prices  
✅ **FR3** — Buy and rent orders (single transaction with multiple items)  
✅ **FR4** — Bill generation (JSON) and email notifications  
✅ **FR5** — Manager: view all orders, update payment status, create/update books  

## Test Your Data

Query MySQL to verify all requirements are met:

```sql
-- See all users
SELECT * FROM user;

-- See all books
SELECT * FROM book;

-- See all orders with customer and status
SELECT o.id, u.username, o.kind, o.status, o.total FROM order o JOIN user u ON o.user_id = u.id;

-- See order items (books ordered)
SELECT oi.*, b.title FROM order_item oi JOIN book b ON oi.book_id = b.id;
```

## Project Structure
```
src/
├── backend/
│   ├── app.py         ← Flask app + routes
│   ├── auth.py        ← Login/register
│   ├── models.py      ← SQLAlchemy ORM
│   ├── db.py          ← DB instance
│   ├── config.py      ← Configuration
│   └── utils.py       ← Email, bill generation
├── client/
│   └── gui.py         ← Tkinter desktop client

.env.template         ← Your config template
requirements.txt
```

## Default Manager
- Username: `manager`
- Password: `manager123`
(Set in `.env`)


