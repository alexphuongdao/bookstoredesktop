
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import os

API_URL = os.getenv("BOOKSTORE_API", "http://127.0.0.1:5001")


class BookstoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bookstore Client")
        self.geometry("900x600")
        self.token = None
        self.user = None
        self.books_cache = []
        self.cart = []  
        self.show_login()

    def show_login(self):
        """Login/Register screen"""
        self.clear()
        
        f = ttk.Frame(self)
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(f, text="Bookstore", font=("Arial", 20, "bold")).pack(pady=20)

        lf = ttk.LabelFrame(f, text="Login / Register", padding=20)
        lf.pack(fill=tk.X)

        ttk.Label(lf, text="Username").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.username = ttk.Entry(lf, width=30)
        self.username.grid(row=0, column=1, padx=5)

        ttk.Label(lf, text="Password").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.password = ttk.Entry(lf, width=30, show="*")
        self.password.grid(row=1, column=1, padx=5)

        ttk.Label(lf, text="Email (for register)").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.email = ttk.Entry(lf, width=30)
        self.email.grid(row=2, column=1, padx=5)

        bf = ttk.Frame(lf)
        bf.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(bf, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Register", command=self.register).pack(side=tk.LEFT, padx=5)

    def register(self):
        """Register new user"""
        u = self.username.get().strip()
        p = self.password.get().strip()
        e = self.email.get().strip()
        
        if not all([u, p, e]):
            messagebox.showwarning("Error", "Fill all fields")
            return
        
        try:
            r = requests.post(f"{API_URL}/auth/register", json={"username": u, "password": p, "email": e}, timeout=5)
            if r.status_code == 201:
                messagebox.showinfo("Success", "Registered! Please login.")
            else:
                messagebox.showerror("Error", r.json().get("error", "Failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def login(self):
        """Login user"""
        u = self.username.get().strip()
        p = self.password.get().strip()
        
        if not u or not p:
            messagebox.showwarning("Error", "Enter username and password")
            return
        
        try:
            r = requests.post(f"{API_URL}/auth/login", json={"username": u, "password": p}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.token = data["access_token"]
                self.user = data["user"]
                
                if self.user["role"] == "manager":
                    self.show_manager()
                else:
                    self.show_customer()
            else:
                messagebox.showerror("Error", r.json().get("error", "Failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_customer(self):
        """Customer interface"""
        self.clear()
        
        # Header
        hf = ttk.Frame(self)
        hf.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(hf, text=f"Welcome {self.user['username']}", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(hf, text="My Orders", command=self.show_my_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(hf, text="Logout", command=self.logout).pack(side=tk.RIGHT)

        # Search
        sf = ttk.LabelFrame(self, text="Search Books", padding=10)
        sf.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(sf, text="Query").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(sf, text="Search", command=self.search).pack(side=tk.LEFT)
        ttk.Button(sf, text="All Books", command=self.load_books).pack(side=tk.LEFT, padx=5)

        # Books list
        lf = ttk.LabelFrame(self, text="Books", padding=10)
        lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        sb = ttk.Scrollbar(lf)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.books_box = tk.Listbox(lf, yscrollcommand=sb.set)
        self.books_box.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self.books_box.yview)

        # Order
        of = ttk.LabelFrame(self, text="Add to Cart", padding=10)
        of.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(of, text="Qty").pack(side=tk.LEFT, padx=5)
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(of, textvariable=self.qty_var, width=5).pack(side=tk.LEFT)
        ttk.Button(of, text="Add Buy", command=lambda: self.add_to_cart("buy")).pack(side=tk.LEFT, padx=5)
        ttk.Button(of, text="Add Rent", command=lambda: self.add_to_cart("rent")).pack(side=tk.LEFT, padx=5)
        ttk.Button(of, text="View Cart", command=self.show_cart).pack(side=tk.LEFT, padx=5)

        self.load_books()

    def show_manager(self):
        """Manager interface"""
        self.clear()
        
        hf = ttk.Frame(self)
        hf.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(hf, text=f"Manager: {self.user['username']}", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(hf, text="Logout", command=self.logout).pack(side=tk.RIGHT)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # add book code
        abf = ttk.Frame(nb, padding=20)
        nb.add(abf, text="Add Book")
        
        ttk.Label(abf, text="Title").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.m_title = ttk.Entry(abf, width=40)
        self.m_title.grid(row=0, column=1)

        ttk.Label(abf, text="Author").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.m_author = ttk.Entry(abf, width=40)
        self.m_author.grid(row=1, column=1)

        ttk.Label(abf, text="Buy Price").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.m_buy = ttk.Entry(abf, width=40)
        self.m_buy.grid(row=2, column=1)

        ttk.Label(abf, text="Rent Price").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.m_rent = ttk.Entry(abf, width=40)
        self.m_rent.grid(row=3, column=1)

        ttk.Button(abf, text="Add Book", command=self.mgr_add_book).grid(row=4, column=0, columnspan=2, pady=20)

        # update book code
        ubf = ttk.Frame(nb, padding=20)
        nb.add(ubf, text="Update Book")
        
        ttk.Label(ubf, text="Book ID").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.m_book_id = ttk.Entry(ubf, width=40)
        self.m_book_id.grid(row=0, column=1)

        ttk.Label(ubf, text="Title (leave blank to keep)").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.m_upd_title = ttk.Entry(ubf, width=40)
        self.m_upd_title.grid(row=1, column=1)

        ttk.Label(ubf, text="Author (leave blank to keep)").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.m_upd_author = ttk.Entry(ubf, width=40)
        self.m_upd_author.grid(row=2, column=1)

        ttk.Label(ubf, text="Buy Price (leave blank to keep)").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.m_upd_buy = ttk.Entry(ubf, width=40)
        self.m_upd_buy.grid(row=3, column=1)

        ttk.Label(ubf, text="Rent Price (leave blank to keep)").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.m_upd_rent = ttk.Entry(ubf, width=40)
        self.m_upd_rent.grid(row=4, column=1)

        ttk.Label(ubf, text="Quantity (number of books in stock)").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.m_upd_quantity = ttk.Entry(ubf, width=40)
        self.m_upd_quantity.grid(row=5, column=1)

        bf = ttk.Frame(ubf)
        bf.grid(row=6, column=0, columnspan=2, pady=20)
        ttk.Button(bf, text="Update Book Info", command=self.mgr_update_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Add Books (Quantity)", command=lambda: self.mgr_add_quantity()).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Rent Return (Add Back)", command=lambda: self.mgr_rent_return()).pack(side=tk.LEFT, padx=5)

        # view orders code
        vof = ttk.Frame(nb, padding=10)
        nb.add(vof, text="Orders")

        ttk.Button(vof, text="Refresh", command=self.mgr_load_orders).pack(pady=10)

        self.mgr_tree = ttk.Treeview(vof, columns=("ID", "User", "Kind", "Total", "Status"), height=12, show="headings")
        for col in ("ID", "User", "Kind", "Total", "Status"):
            self.mgr_tree.column(col, width=100)
            self.mgr_tree.heading(col, text=col)
        self.mgr_tree.pack(fill=tk.BOTH, expand=True)

        uf = ttk.LabelFrame(vof, text="Update Status", padding=10)
        uf.pack(fill=tk.X, pady=10)
        ttk.Label(uf, text="Status").pack(side=tk.LEFT)
        self.m_status = tk.StringVar()
        ttk.Combobox(uf, textvariable=self.m_status, values=["Pending", "Paid", "Shipped", "Delivered"], width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(uf, text="Update", command=self.mgr_update).pack(side=tk.LEFT)

        self.mgr_load_orders()

    def load_books(self):
        """Load all books"""
        try:
            r = requests.get(f"{API_URL}/books", timeout=5)
            if r.status_code == 200:
                self.books_cache = r.json()
                self._show_books(self.books_cache)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search(self):
        """Search books"""
        q = self.search_var.get().strip()
        try:
            r = requests.get(f"{API_URL}/books", params={"q": q}, timeout=5)
            if r.status_code == 200:
                self.books_cache = r.json()
                self._show_books(self.books_cache)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_books(self, books):
        """Display books in listbox"""
        self.books_box.delete(0, tk.END)
        for b in books:
            self.books_box.insert(tk.END, f"[{b['id']}] {b['title']} by {b['author']} | Buy: ${b['price_buy']} | Rent: ${b['price_rent']}")

    def add_to_cart(self, kind):
        """Add book to cart (not to database yet)"""
        sel = self.books_box.curselection()
        if not sel:
            messagebox.showwarning("Error", "Select a book")
            return
        
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                messagebox.showwarning("Error", "Quantity must be > 0")
                return
        except ValueError:
            messagebox.showwarning("Error", "Invalid quantity")
            return

        book = self.books_cache[sel[0]]
        price = book["price_buy"] if kind == "buy" else book["price_rent"]
        
        # Add to cart
        self.cart.append({
            "book_id": book["id"],
            "title": book["title"],
            "author": book["author"],
            "kind": kind,
            "quantity": qty,
            "unit_price": price,
        })
        
        messagebox.showinfo("Success", f"Added '{book['title']}' ({kind}) x{qty} to cart!")
        self.qty_var.set("1")

    def show_cart(self):
        """Show cart and allow to place order (FR3.3)"""
        if not self.cart:
            messagebox.showwarning("Info", "Cart is empty!")
            return
        
        # my cart window
        cart_window = tk.Toplevel(self)
        cart_window.title("Shopping Cart - Place Order")
        cart_window.geometry("700x500")
        
        # my cart item display
        lf = ttk.LabelFrame(cart_window, text="Cart Items", padding=10)
        lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = scrolledtext.ScrolledText(lf, height=15)
        text.pack(fill=tk.BOTH, expand=True)
        
        total = 0.0
        for idx, item in enumerate(self.cart, 1):
            line_total = item["unit_price"] * item["quantity"]
            total += line_total
            text.insert(tk.END, f"{idx}. {item['title']} by {item['author']}\n")
            text.insert(tk.END, f"   Type: {item['kind'].upper()} | Qty: {item['quantity']} | Price: ${item['unit_price']:.2f}\n")
            text.insert(tk.END, f"   Line Total: ${line_total:.2f}\n")
            text.insert(tk.END, f"   [Remove] Button: Item {idx}\n")
            text.insert(tk.END, "-" * 60 + "\n")
        
        text.insert(tk.END, f"\nGRAND TOTAL: ${total:.2f}\n")
        text.config(state=tk.DISABLED)
        
        
        bf = ttk.Frame(cart_window, padding=10)
        bf.pack(fill=tk.X)
        
        ttk.Button(bf, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Place Order (Single Transaction)", command=self.place_order_final).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Close", command=cart_window.destroy).pack(side=tk.RIGHT, padx=5)

    def clear_cart(self):
        """Clear shopping cart"""
        self.cart = []
        messagebox.showinfo("Info", "Cart cleared!")

    def place_order_final(self):
        """FR3.3: Finalize order as single transaction with all cart items"""
        if not self.cart:
            messagebox.showwarning("Error", "Cart is empty!")
            return
        
        # group items by kind (all buys first, then all rents)
        buy_items = [item for item in self.cart if item["kind"] == "buy"]
        rent_items = [item for item in self.cart if item["kind"] == "rent"]
        
        # place orders
        orders_created = []
        
        # place BUY order if any
        if buy_items:
            items_payload = [{"book_id": item["book_id"], "quantity": item["quantity"]} for item in buy_items]
            if self._place_order_transaction("buy", items_payload):
                orders_created.append("buy")
        
        # place RENT order if any
        if rent_items:
            items_payload = [{"book_id": item["book_id"], "quantity": item["quantity"]} for item in rent_items]
            if self._place_order_transaction("rent", items_payload):
                orders_created.append("rent")
        
        if orders_created:
            self.cart = []
            messagebox.showinfo("Success", f"Order(s) placed successfully!\nCheck 'My Orders' to see details.")
        else:
            messagebox.showerror("Error", "Failed to place order")

    def _place_order_transaction(self, kind, items):
        """Helper: Send order to backend (actual database transaction)"""
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"kind": kind, "items": items}
        
        try:
            r = requests.post(f"{API_URL}/orders", json=payload, headers=headers, timeout=5)
            if r.status_code == 201:
                data = r.json()
                print(f"✓ {kind.upper()} Order #{data['order']['id']} created!")
                return True
            else:
                error_msg = r.json().get("error", "Failed")
                messagebox.showerror("Error", f"Failed to place {kind} order: {error_msg}")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            return False

    def show_my_orders(self):
        """Show customer's orders"""
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            r = requests.get(f"{API_URL}/orders", headers=headers, timeout=5)
            if r.status_code == 200:
                orders = r.json()
                w = tk.Toplevel(self)
                w.title("My Orders")
                w.geometry("600x400")
                
                text = scrolledtext.ScrolledText(w)
                text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                for o in orders:
                    text.insert(tk.END, f"\nOrder #{o['id']} ({o['kind'].upper()})\n")
                    text.insert(tk.END, f"Status: {o['status']} | Total: ${o['total']:.2f}\n")
                    text.insert(tk.END, "Items:\n")
                    for i in o.get("items", []):
                        text.insert(tk.END, f"  - {i['title']} x{i['quantity']} @ ${i['unit_price']:.2f}\n")
                    text.insert(tk.END, "-" * 50 + "\n")

                text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mgr_add_book(self):
        """Manager adds book"""
        title = str(self.m_title.get().strip())
        author = str(self.m_author.get().strip())
        try:
            buy = float(self.m_buy.get())
            rent = float(self.m_rent.get())
        except ValueError:
            messagebox.showwarning("Error", "Invalid price - must be numbers (e.g., 29.99)")
            return

        if not title or not author:
            messagebox.showwarning("Error", "Fill all fields: Title, Author, Buy Price, Rent Price")
            return

        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"title": title, "author": author, "price_buy": buy, "price_rent": rent}

        print(f"DEBUG: Sending payload: {payload}")
        print(f"DEBUG: Headers: {headers}")

        try:
            r = requests.post(f"{API_URL}/books", json=payload, headers=headers, timeout=5)
            print(f"DEBUG: Status code: {r.status_code}")
            print(f"DEBUG: Response text: {r.text}")
            
            if r.status_code == 201:
                messagebox.showinfo("Success", "Book added successfully!")
                self.m_title.delete(0, tk.END)
                self.m_author.delete(0, tk.END)
                self.m_buy.delete(0, tk.END)
                self.m_rent.delete(0, tk.END)
            else:
                try:
                    error_msg = r.json().get("error", f"Server error: {r.text}")
                except:
                    error_msg = f"Server error (status {r.status_code}): {r.text}"
                messagebox.showerror("Error", f"Failed: {error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def mgr_update_book(self):
        """Manager updates existing book (FR5.4)"""
        try:
            book_id = int(self.m_book_id.get().strip())
        except ValueError:
            messagebox.showwarning("Error", "Book ID must be a number")
            return

        if book_id <= 0:
            messagebox.showwarning("Error", "Book ID must be positive")
            return

        
        payload = {}
        
        title = self.m_upd_title.get().strip()
        if title:
            payload["title"] = title
        
        author = self.m_upd_author.get().strip()
        if author:
            payload["author"] = author
        
        buy_price = self.m_upd_buy.get().strip()
        if buy_price:
            try:
                payload["price_buy"] = float(buy_price)
            except ValueError:
                messagebox.showwarning("Error", "Buy Price must be a valid number")
                return
        
        rent_price = self.m_upd_rent.get().strip()
        if rent_price:
            try:
                payload["price_rent"] = float(rent_price)
            except ValueError:
                messagebox.showwarning("Error", "Rent Price must be a valid number")
                return

        if not payload:
            messagebox.showwarning("Error", "Fill at least one field to update")
            return

        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        try:
            r = requests.put(f"{API_URL}/books/{book_id}", json=payload, headers=headers, timeout=5)
            
            if r.status_code == 200:
                messagebox.showinfo("Success", "Book updated successfully!")
                self.m_book_id.delete(0, tk.END)
                self.m_upd_title.delete(0, tk.END)
                self.m_upd_author.delete(0, tk.END)
                self.m_upd_buy.delete(0, tk.END)
                self.m_upd_rent.delete(0, tk.END)
                self.m_upd_quantity.delete(0, tk.END)
            else:
                try:
                    error_msg = r.json().get("error", f"Server error: {r.text}")
                except:
                    error_msg = f"Server error (status {r.status_code}): {r.text}"
                messagebox.showerror("Error", f"Failed: {error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def mgr_add_quantity(self):
        """Add quantity to book stock (SET available field to exact number)"""
        try:
            book_id = int(self.m_book_id.get().strip())
            quantity = int(self.m_upd_quantity.get().strip())
        except ValueError:
            messagebox.showwarning("Error", "Book ID and Quantity must be numbers")
            return

        if book_id <= 0:
            messagebox.showwarning("Error", "Book ID must be positive")
            return

        if quantity < 0:
            messagebox.showwarning("Error", "Quantity must be 0 or positive")
            return

        payload = {"available": quantity}
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        try:
            r = requests.put(f"{API_URL}/books/{book_id}", json=payload, headers=headers, timeout=5)
            
            if r.status_code == 200:
                messagebox.showinfo("Success", f"Book ID {book_id} quantity set to {quantity}!")
                self.m_book_id.delete(0, tk.END)
                self.m_upd_quantity.delete(0, tk.END)
            else:
                try:
                    error_msg = r.json().get("error", f"Server error: {r.text}")
                except:
                    error_msg = f"Server error (status {r.status_code}): {r.text}"
                messagebox.showerror("Error", f"Failed: {error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def mgr_rent_return(self):
        """Return rented books - ADD to existing available inventory"""
        try:
            book_id = int(self.m_book_id.get().strip())
            quantity = int(self.m_upd_quantity.get().strip())
        except ValueError:
            messagebox.showwarning("Error", "Book ID and Quantity must be numbers")
            return

        if book_id <= 0:
            messagebox.showwarning("Error", "Book ID must be positive")
            return

        if quantity < 0:
            messagebox.showwarning("Error", "Quantity must be 0 or positive")
            return

        payload = {"quantity": quantity}
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        try:
            r = requests.patch(f"{API_URL}/books/{book_id}/add-quantity", json=payload, headers=headers, timeout=5)
            
            if r.status_code == 200:
                messagebox.showinfo("Success", f"Added {quantity} returned books to Book ID {book_id} inventory!")
                self.m_book_id.delete(0, tk.END)
                self.m_upd_quantity.delete(0, tk.END)
            else:
                try:
                    error_msg = r.json().get("error", f"Server error: {r.text}")
                except:
                    error_msg = f"Server error (status {r.status_code}): {r.text}"
                messagebox.showerror("Error", f"Failed: {error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def mgr_load_orders(self):
        """Load all orders for manager"""
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            r = requests.get(f"{API_URL}/orders", headers=headers, timeout=5)
            if r.status_code == 200:
                orders = r.json()
                self.mgr_tree.delete(*self.mgr_tree.get_children())
                for o in orders:
                    self.mgr_tree.insert("", "end", iid=o["id"], values=(
                        o["id"], o["user_id"], o["kind"].upper(), f"${o['total']:.2f}", o["status"]
                    ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mgr_update(self):
        """Manager updates order status"""
        sel = self.mgr_tree.selection()
        if not sel:
            messagebox.showwarning("Error", "Select an order")
            return

        status = self.m_status.get().strip()
        if not status:
            messagebox.showwarning("Error", "Select status")
            return

        order_id = sel[0]
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"status": status}

        try:
            r = requests.patch(f"{API_URL}/orders/{order_id}/status", json=payload, headers=headers, timeout=5)
            if r.status_code == 200:
                messagebox.showinfo("Success", "Status updated")
                self.mgr_load_orders()
            else:
                messagebox.showerror("Error", r.json().get("error", "Failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def logout(self):
        """Logout"""
        self.token = None
        self.user = None
        self.show_login()

    def clear(self):
        """Clear window"""
        for w in self.winfo_children():
            w.destroy()


if __name__ == "__main__":
    app = BookstoreApp()
    app.mainloop()
