import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import datetime, timedelta

DB_NAME = "library.db"
FINE_PER_DAY = 5

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    quantity INTEGER
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    course TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS issued (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student TEXT,
    book TEXT,
    issue_date TEXT,
    due_date TEXT
)''')

conn.commit()

# Default admin
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users(username,password) VALUES('admin','admin')")
    conn.commit()


# LOGIN SYSTEM
def login():
    u = username.get()
    p = password.get()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    if cursor.fetchone():
        login_window.destroy()
        main_app()
    else:
        messagebox.showerror("Error", "Invalid Login")

# MAIN APP
def main_app():
    global book_title, book_author, book_qty
    global student_name, student_course
    global issue_student, issue_book_name, result, search_box

    root = Tk()
    root.title("Advanced Library Management System")
    root.geometry("800x650")

    Label(root, text="LIBRARY MANAGEMENT SYSTEM", font=("Arial", 18, "bold")).pack(pady=10)

    # ADD BOOK
    f1 = LabelFrame(root, text="Add Book", padx=10, pady=10)
    f1.pack(fill="both", padx=10, pady=5)

    book_title = Entry(f1)
    book_author = Entry(f1)
    book_qty = Entry(f1)

    Label(f1, text="Title").grid(row=0, column=0)
    Label(f1, text="Author").grid(row=1, column=0)
    Label(f1, text="Quantity").grid(row=2, column=0)

    book_title.grid(row=0, column=1)
    book_author.grid(row=1, column=1)
    book_qty.grid(row=2, column=1)

    Button(f1, text="Add Book", command=add_book).grid(row=3, columnspan=2)

    # SEARCH
    f_search = LabelFrame(root, text="Search Book")
    f_search.pack(fill="both", padx=10, pady=5)

    search_box = Entry(f_search)
    search_box.grid(row=0, column=0)
    Button(f_search, text="Search", command=search_book).grid(row=0, column=1)

    # STUDENT
    f2 = LabelFrame(root, text="Add Student")
    f2.pack(fill="both", padx=10, pady=5)

    student_name = Entry(f2)
    student_course = Entry(f2)

    Label(f2, text="Name").grid(row=0, column=0)
    Label(f2, text="Course").grid(row=1, column=0)

    student_name.grid(row=0, column=1)
    student_course.grid(row=1, column=1)
    Button(f2, text="Add Student", command=add_student).grid(row=2, columnspan=2)

    # ISSUE
    f3 = LabelFrame(root, text="Issue / Return")
    f3.pack(fill="both", padx=10, pady=5)

    issue_student = Entry(f3)
    issue_book_name = Entry(f3)

    Label(f3, text="Student Name").grid(row=0, column=0)
    Label(f3, text="Book Title").grid(row=1, column=0)

    issue_student.grid(row=0, column=1)
    issue_book_name.grid(row=1, column=1)

    Button(f3, text="Issue Book", command=issue_book).grid(row=2, column=0)
    Button(f3, text="Return Book", command=return_book).grid(row=2, column=1)
    Button(f3, text="Report", command=show_report).grid(row=3, columnspan=2)

    result = Text(root, height=12)
    result.pack(fill="both", padx=10, pady=10)

    root.mainloop()

# FUNCTIONS

def add_book():
    cursor.execute("INSERT INTO books(title,author,quantity) VALUES(?,?,?)",
                   (book_title.get(), book_author.get(), book_qty.get()))
    conn.commit()
    messagebox.showinfo("Success", "Book Added")


def search_book():
    q = search_box.get()
    cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + q + '%',))
    result.delete(1.0, END)
    for r in cursor.fetchall():
        result.insert(END, str(r) + "\n")


def add_student():
    cursor.execute("INSERT INTO students(name,course) VALUES(?,?)",
                   (student_name.get(), student_course.get()))
    conn.commit()
    messagebox.showinfo("Success", "Student Added")


def issue_book():
    s = issue_student.get()
    b = issue_book_name.get()
    cursor.execute("SELECT quantity FROM books WHERE title=?", (b,))
    data = cursor.fetchone()

    if not data or data[0] <= 0:
        messagebox.showerror("Error", "Book not available")
        return

    issue = datetime.now()
    due = issue + timedelta(days=7)

    cursor.execute("UPDATE books SET quantity=quantity-1 WHERE title=?", (b,))
    cursor.execute("INSERT INTO issued(student,book,issue_date,due_date) VALUES(?,?,?,?)",
                   (s, b, issue.strftime('%Y-%m-%d'), due.strftime('%Y-%m-%d')))
    conn.commit()
    messagebox.showinfo("Success", f"Issued. Due: {due.date()}")


def return_book():
    s = issue_student.get()
    b = issue_book_name.get()

    cursor.execute("SELECT due_date FROM issued WHERE student=? AND book=?", (s, b))
    data = cursor.fetchone()

    if not data:
        messagebox.showerror("Error", "Record not found")
        return

    due = datetime.strptime(data[0], '%Y-%m-%d')
    today = datetime.now()
    late_days = (today - due).days
    fine = max(0, late_days * FINE_PER_DAY)

    cursor.execute("DELETE FROM issued WHERE student=? AND book=?", (s, b))
    cursor.execute("UPDATE books SET quantity=quantity+1 WHERE title=?", (b,))
    conn.commit()

    messagebox.showinfo("Returned", f"Fine = ₹{fine}")


def show_report():
    cursor.execute("SELECT * FROM issued")
    result.delete(1.0, END)
    result.insert(END, "Issued Books:\n")
    for r in cursor.fetchall():
        result.insert(END, str(r) + "\n")

        #LOGIN 

login_window = Tk()
login_window.title("Library Login")
login_window.geometry("300x200")

Label(login_window, text="Admin Login", font=("Arial", 14)).pack(pady=10)

username = Entry(login_window)
password = Entry(login_window, show="*")

Label(login_window, text="Username").pack()
username.pack()
Label(login_window, text="Password").pack()
password.pack()

Button(login_window, text="Login", command=login).pack(pady=10)
Label(login_window, text="Default: admin / admin").pack()

login_window.mainloop()
