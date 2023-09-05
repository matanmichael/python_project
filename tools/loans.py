import sqlite3
from datetime import datetime, timedelta
from flask import request

class Loan:
    def __init__(self):
        self.con=sqlite3.connect("library.db",check_same_thread=False)
        self.cur=self.con.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS loans(
                id INTEGER PRIMARY KEY,
                LoanDate TEXT,
                ReturnDate TEXT,
                CustID INTEGER,
                BookID INTEGER,
                FOREIGN KEY (CustID) REFERENCES customers(id),
                FOREIGN KEY (BookID) REFERENCES books(id)
            )
        ''')
    def displayAllLoans(self):
        self.cur.execute('''SELECT * FROM loans ''')
        all_loans=self.cur.fetchall()
        return all_loans

    def loan_book(self):
        if request.method=='POST':
            cust_id=request.form.get('cust_id')
            book_id =request.form.get('book_id')
        # Input from the user
            loan_date = datetime.now().strftime('%Y-%m-%d')  # Get the current date
            # Retrieve book type from the database
            self.cur.execute("SELECT Type FROM books WHERE Id=?", (book_id,))
            book_record = self.cur.fetchone()
            if book_record is None:
                print(f"Book with ID {book_id} not found.")
                return
            book_type = int(book_record[0])
            # Set return date based on book type
            if book_type == 1:
                return_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
            elif book_type == 2:
                return_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
            elif book_type == 3:
                return_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            else:
                return
            self.cur.execute('''
                INSERT INTO loans (CustID, BookID, Loandate, Returndate)
                VALUES (?, ?, ?, ?)
            ''', (cust_id, book_id, loan_date, return_date))
            self.con.commit()

    def return_book(self):
        book_id =request.form.get('book_id')
        # Check if the book is currently on loan and has a non-null return date
        self.cur.execute("SELECT * FROM loans WHERE BookID=? AND ReturnDate IS NOT NULL", (book_id,))
        loan_record = self.cur.fetchone()
        if not loan_record:
            return
        # Delete the loan record for the returned book
        self.cur.execute("DELETE FROM loans WHERE BookID=?", (book_id,))
        self.con.commit()
    
    def display_late_loans(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.cur.execute("SELECT * FROM loans WHERE ReturnDate < ? AND ReturnDate IS NOT NULL", (current_date,))
        late_loans = self.cur.fetchall()
        return late_loans

