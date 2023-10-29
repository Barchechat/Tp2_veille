from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100))
    classification_id = db.Column(db.Integer, db.ForeignKey('classification.id'))
    classification = db.relationship('Classification', backref='books')

class Classification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    book = db.relationship('Book', backref='loans')
    due_date = db.Column(db.DateTime, nullable=False)
    late_fee = db.Column(db.Float)

@app.route('/')
def index():
    books = Book.query.all()
    loans = Loan.query.all()
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', books=books, current_date=current_date, loans=loans)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    classification_id = request.form['classification_id']
    book = Book(title=title, author=author, classification_id=classification_id)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_loan', methods=['POST'])
def add_loan():
    book_id = request.form['book_id']
    due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')

    # Vérifiez si la date de retour est dépassée
    today = datetime.today()
    late_fee = 0.0
    if due_date < today:
        # Calculez les frais de retard (1$ par jour de retard)
        days_late = (today - due_date).days
        late_fee = days_late * 1.0

    loan = Loan(book_id=book_id, due_date=due_date, late_fee=late_fee)
    db.session.add(loan)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/remove_loan', methods=['POST'])
def remove_loan():
    loan_id = request.form['loan_id']
    loan = Loan.query.get(loan_id)

    if loan:
        db.session.delete(loan)
        db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
