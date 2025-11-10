from __future__ import annotations
import os
from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import re

# Import your existing services
from services.intent_search import IntentSearchEngine
from services.walmart_adapter import WalmartSparePartsAdapter, parse_free_text

# ============================================
# APP INITIALIZATION
# ============================================

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///searchiq.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Instantiate your existing engines
intent_engine = IntentSearchEngine()
walmart = WalmartSparePartsAdapter()

# ============================================
# DATABASE MODELS
# ============================================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

# ============================================
# VALIDATION HELPERS
# ============================================

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Valid"

# ============================================
# PAGE ROUTES
# ============================================

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.get("/signup")
def signup_page():
    return render_template("signup.html")

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.post("/api/auth/signup")
def signup():
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password and create user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create JWT token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': 'Account created successfully!',
            'access_token': access_token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.post("/api/auth/login")
def login():
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        email_or_username = (data.get('email_or_username') or '').strip().lower()
        password = data.get('password') or ''
        
        if not email_or_username or not password:
            return jsonify({'error': 'Email/Username and password are required'}), 400
        
        # Find user by email or username
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful!',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get("/api/auth/me")
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# PROTECTED API ROUTES (Your existing logic)
# ============================================

@app.post("/api/search")
@jwt_required()
def intent_search():
    data = request.get_json(force=True, silent=True) or {}
    query = (data.get("query") or "").strip()
    max_results = int(data.get("max_results") or 10)
    
    if not query:
        return jsonify({"detail": "Query is required"}), 400
    
    results = intent_engine.search(query, max_results=max_results)
    return jsonify(results)

@app.post("/spare-parts/parse")
@jwt_required()
def parse_text():
    data = request.get_json(force=True, silent=True) or {}
    message = (data.get("message") or "").strip()
    
    parsed = parse_free_text(message)
    cands = walmart.candidate_orders(
        parsed.get("brand"), 
        parsed.get("category"),
        parsed.get("year"), 
        parsed.get("month"), 
        None
    )
    
    return jsonify({"parsed": parsed, "candidates": cands[:10]})

@app.post("/spare-parts/recommend")
@jwt_required()
def recommend_by_invoice():
    data = request.get_json(force=True, silent=True) or {}
    inv = (data.get("invoice_number") or "").strip()
    fault = (data.get("fault_keyword") or "").strip()
    topn = int(data.get("max_results") or 5)
    
    if not inv:
        return jsonify({"detail": "invoice_number is required"}), 400
    
    recs = walmart.recommend_with_invoice(inv, fault, top_n=topn)
    return jsonify(recs)

@app.post("/spare-parts")
@jwt_required()
def direct_spares():
    data = request.get_json(force=True, silent=True) or {}
    device_model = (data.get("device_model") or "").strip()
    issue_description = (data.get("issue_description") or "").strip()
    brand = (data.get("brand") or "").strip()
    topn = int(data.get("max_results") or 10)
    
    if not device_model or not brand:
        return jsonify({"detail": "device_model and brand required"}), 400
    
    recs = walmart.recommend_without_invoice(brand, device_model, issue_description, top_n=topn)
    return jsonify(recs)

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health():
    return jsonify({
        "status": "healthy", 
        "items": len(intent_engine.df), 
        "orders_loaded": True,
        "users_count": User.query.count()
    })

# ============================================
# RUN APP
# ============================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)