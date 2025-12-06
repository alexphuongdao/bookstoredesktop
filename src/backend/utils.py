from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import SENDGRID_API_KEY


def hash_password(plain: str) -> str:
    """Hash password using werkzeug (compatible with Flask)"""
    return generate_password_hash(plain, method='pbkdf2:sha256')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        return check_password_hash(hashed, plain)
    except:
        return False


def generate_bill(order, user):
    """Generate bill dictionary per FR4.1"""
    items = []
    for item in order.items:
        items.append({
            "book_id": item.book_id,
            "title": item.book.title,
            "author": item.book.author,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_total": item.quantity * item.unit_price,
        })
    
    bill = {
        "order_id": order.id,
        "order_type": order.kind.upper(),
        "customer": {
            "username": user.username,
            "email": user.email,
        },
        "items": items,
        "total": order.total,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
    }
    return bill


def save_bill(bill, folder="bills"):
    """Save bill as JSON"""
    os.makedirs(folder, exist_ok=True)
    filename = f"bill_{bill['order_id']}.json"
    path = os.path.join(folder, filename)
    with open(path, "w") as f:
        json.dump(bill, f, indent=2)
    return path


def send_bill_email(bill, to_email, smtp_config):
    """Send bill via email using SendGrid per FR4.2"""
    try:
        api_key = SENDGRID_API_KEY
        print(f"[DEBUG] SENDGRID_API_KEY present: {bool(api_key)}")
        print(f"[DEBUG] Sending email to: {to_email}")
        
        if not api_key:
            print("ERROR: SENDGRID_API_KEY not set")
            return False
        
        from_email = 'daoduyphuong2005@gmail.com'
        subject = f"Order Receipt #{bill['order_id']}"
        
        
        html_content = f"""
<html>
<body>
<p>Dear {bill['customer']['username']},</p>
<p>Thank you for your order!</p>
<p><strong>Order ID:</strong> {bill['order_id']}</p>
<p><strong>Type:</strong> {bill['order_type']}</p>
<p><strong>Total:</strong> ${bill['total']:.2f}</p>
<p><strong>Status:</strong> {bill['status']}</p>
<p><strong>Items:</strong></p>
<ul>
"""
        for item in bill["items"]:
            html_content += f"<li>{item['title']} x{item['quantity']} @ ${item['unit_price']:.2f}</li>\n"
        
        html_content += """
</ul>
<p>Best regards,<br>Bookstore Team</p>
</body>
</html>
"""
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"[SUCCESS] Email sent to {to_email}! Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"[ERROR] Email send failed: {e}")
        import traceback
        traceback.print_exc()
        return False
