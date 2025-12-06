# Bookstore Project - Quick Start Guide

## Prerequisites (One-Time Setup)
- MySQL server installed and running
- Python 3.11+ installed
- Virtual environment created: `.venv/`
- Dependencies installed: `pip install -r requirements.txt`
- `.env` file configured with MySQL credentials

---

## Running the Project (3 Terminals)

### **Terminal 1: Start MySQL Server**
```bash
# Check if MySQL is running (it should be)
mysql -u root -p
# Enter your password: huong310705
# If connected, type: exit
```

✅ **MySQL is ready** - Keep it running in background

---

### **Terminal 2: Start Flask Backend API**
```bash
cd /Users/daoduyphuong/csce310project
source .venv/bin/activate
python -m src.backend.app
```

**Expected output:**
```
✓ Manager user created: manager
✓ Seeded 3 books

🚀 Bookstore API running on http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

✅ **Backend is ready** - Leave this terminal running

---

### **Terminal 3: Start Tkinter Desktop Client**
```bash
cd /Users/daoduyphuong/csce310project
source .venv/bin/activate
python -m src.client.gui
```

**Expected output:**
- A new window appears with "Bookstore" login screen
- GUI is ready to use

✅ **Client is ready** - GUI window is open

---

## Now You Can:

### **As a Customer:**
1. Click **Register** → Enter username, password, email → Create account
2. Click **Login** → Enter credentials → Access bookstore
3. **Search Books** → Enter keyword (title/author) → View results
4. **Place Order** → Select quantity → Click "Buy" or "Rent"
5. **View My Orders** → See order history and bills (saved in `bills/` folder)

### **As a Manager:**
1. Login with: `manager` / `manager123`
2. **Add Book** tab → Enter title, author, prices → Click "Add"
3. **Orders** tab → View all customer orders → Update payment status (Pending → Paid)

---

## Verify Data in MySQL

Open a **4th Terminal** to query the database:

```bash
mysql -u root -phuong310705 bookstore
```

Then run these queries:

```sql
-- See all users (customer & manager)
SELECT * FROM user;

-- See all books
SELECT * FROM book;

-- See all orders
SELECT o.id, u.username, o.kind, o.status, o.total, o.created_at 
FROM order o 
JOIN user u ON o.user_id = u.id;

-- See order items (what books were ordered)
SELECT oi.id, oi.order_id, b.title, oi.quantity, oi.unit_price 
FROM order_item oi 
JOIN book b ON oi.book_id = b.id;

-- See bills generated (JSON files)
-- Check: ls -la bills/
```

---

## Terminal Summary

| Terminal | Command | Purpose | Keep Running? |
|----------|---------|---------|---|
| **1** | `mysql -u root -p` | MySQL database | ✅ Yes |
| **2** | `python -m src.backend.app` | Flask REST API | ✅ Yes |
| **3** | `python -m src.client.gui` | Tkinter GUI | ✅ Yes |
| **4** | `mysql -u root -phuong310705 bookstore` | Test queries | ❌ Only when needed |

---

## Troubleshooting

### Backend won't start?
- Check `.env` file has correct MySQL password: `huong310705`
- Verify MySQL is running in Terminal 1
- Check if port 5000 is already in use

### GUI won't start?
- Verify backend is running (Terminal 2)
- Check virtual environment is activated
- Make sure Tkinter is installed: `brew install python-tk@3.13`

### MySQL connection error?
- Verify MySQL password is correct in `.env`
- Make sure `bookstore` database exists: `mysql -u root -phuong310705 -e "SHOW DATABASES;"`

### Bills not saving?
- Check `bills/` folder has write permissions
- Create if missing: `mkdir -p bills/`

---

## Project Structure

```
/Users/daoduyphuong/csce310project/
├── .env                    ← MySQL credentials (your config)
├── .env.template           ← Template reference
├── requirements.txt        ← Python packages
├── STEPS.md               ← This file
├── README.md              ← Project overview
├── instruction.md         ← Requirements document
│
├── src/
│   ├── backend/
│   │   ├── app.py         ← Flask API & routes
│   │   ├── auth.py        ← Login/Register
│   │   ├── models.py      ← Database models
│   │   ├── db.py          ← SQLAlchemy instance
│   │   ├── config.py      ← Load .env variables
│   │   └── utils.py       ← Email, bills, hashing
│   │
│   └── client/
│       └── gui.py         ← Tkinter desktop GUI
│
└── bills/                 ← Generated bill JSON files
```

---

## Quick Commands Cheat Sheet

```bash
# Activate virtual environment
source .venv/bin/activate

# Start backend (Terminal 2)
python -m src.backend.app

# Start client (Terminal 3)
python -m src.client.gui

# Query database (Terminal 4)
mysql -u root -phuong310705 bookstore

# View bill files
ls -la bills/
cat bills/bill_1.json

# Stop backend
# Press CTRL+C in Terminal 2

# Stop client
# Close the GUI window or CTRL+C in Terminal 3

# Exit MySQL
# Type: exit
```

---

## Next Steps

1. **Open 3 terminals** (MySQL running by default)
2. **Terminal 2**: Start Flask backend
3. **Terminal 3**: Start Tkinter client
4. **Test the app**: Register, search, buy/rent books
5. **Verify data**: Query MySQL to confirm all requirements met

🎉 **You're ready to go!**

Manager
"""
manager
manager123

Customer
"""
user alexdao
pass 123

