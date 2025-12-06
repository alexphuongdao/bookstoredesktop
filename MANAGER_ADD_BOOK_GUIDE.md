# Manager: How to Add Books (Input Guide)

## Login as Manager First

**Username:** `manager`  
**Password:** `manager123`

---

## Add Book Form Fields

When you see the "Add Book" tab in the Manager screen, fill in exactly:

### **Title** (Required)
- Book name/title
- Examples: `The Pragmatic Programmer`, `Clean Code`, `Python Cookbook`
- Any text allowed, spaces are OK

### **Author** (Required)
- Author name
- Examples: `David Thomas & Andrew Hunt`, `Robert C. Martin`, `David Beazley`
- Any text allowed, spaces are OK

### **Buy Price** (Required)
- Price to purchase the book
- Must be a **number** (can have decimals)
- Examples: `29.99`, `49.95`, `15`, `39.99`
- **Do NOT use:** `$29.99`, `$`, commas, or letters

### **Rent Price** (Required)
- Price to rent the book per unit
- Must be a **number** (can have decimals)
- Examples: `5.99`, `7.50`, `9.99`, `12`
- **Do NOT use:** `$9.99`, `$`, commas, or letters

---

## Example Input

| Field | Value |
|-------|-------|
| **Title** | The Art of Computer Programming |
| **Author** | Donald E. Knuth |
| **Buy Price** | 179.99 |
| **Rent Price** | 19.99 |

Then click **"Add"** button.

---

## Common Errors & Fixes

### ❌ "Invalid price - must be numbers"
**Cause:** You entered `$29.99` or `29,99` or non-numeric text  
**Fix:** Remove `$` sign and use `.` for decimals. Enter: `29.99`

### ❌ "Fill all fields: Title, Author, Buy Price, Rent Price"
**Cause:** One or more fields are empty  
**Fix:** Make sure all 4 fields have values

### ❌ "Failed: Manager only"
**Cause:** You logged in as a customer, not manager  
**Fix:** Logout and login with `manager` / `manager123`

### ❌ "Connection error"
**Cause:** Backend API is not running  
**Fix:** Make sure Terminal 2 (backend) is running and shows `🚀 Bookstore API running...`

---

## After Adding a Book

✅ Success dialog will appear  
✅ Form fields will clear automatically  
✅ Book is now in database (visible in search)  
✅ Check database: `SELECT * FROM book;` in MySQL

---

## Tips

- **Prices:** Can be `5` (integer) or `5.99` (decimal) — both work
- **Names:** Can include spaces, quotes, special characters
- **Multiple books:** Just fill and add again, no need to logout
- **Verify:** Go to Customer side → Search → Your book should appear

