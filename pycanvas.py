import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
import pickle

# MySQL setup
# Run this SQL code separately in your MySQL database to create the necessary tables
"""
CREATE DATABASE pycanvas_palettes;
USE pycanvas_palettes;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE gallery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    artwork_name VARCHAR(100),
    file_path VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

class PyCanvasPalettes:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Yuvraj@123',
            database='pycanvas_palettes'
        )
        self.cursor = self.conn.cursor()
        self.root = tk.Tk()
        self.root.title('PyCanvas Palettes')
        self.username = None
        self.create_login_widgets()
        self.root.mainloop()

    def create_login_widgets(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password").pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.login_frame, text="Register", command=self.register).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.cursor.execute('SELECT id FROM users WHERE username=%s AND password=%s', (username, password))
        user = self.cursor.fetchone()
        if user:
            self.user_id = user[0]
            self.username = username
            self.login_frame.destroy()
            self.create_canvas_widgets()
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        self.conn.commit()
        messagebox.showinfo('Info', 'User registered successfully')

    def create_canvas_widgets(self):
        self.canvas = tk.Canvas(self.root, bg='white', width=500, height=500)
        self.canvas.pack(pady=20)
        self.canvas.bind('<B1-Motion>', self.paint)

        self.save_button = tk.Button(self.root, text='Save Artwork', command=self.save_artwork)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.load_button = tk.Button(self.root, text='Load Artwork', command=self.load_artwork)
        self.load_button.pack(side=tk.LEFT, padx=10)

        self.load_gallery_button = tk.Button(self.root, text='Load Gallery', command=self.load_gallery)
        self.load_gallery_button.pack(side=tk.LEFT, padx=10)

    def paint(self, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.canvas.create_oval(x1, y1, x2, y2, fill='black', width=2)

    def save_artwork(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.pkl', filetypes=[('Pickle files', '*.pkl')])
        if file_path:
            artwork_name = file_path.split('/')[-1].replace('.pkl', '')
            self.cursor.execute('INSERT INTO gallery (user_id, artwork_name, file_path) VALUES (%s, %s, %s)',
                                (self.user_id, artwork_name, file_path))
            self.conn.commit()
            artwork = self.canvas.find_all()
            with open(file_path, 'wb') as file:
                pickle.dump(artwork, file)
            messagebox.showinfo('Info', 'Artwork saved successfully')

    def load_artwork(self):
        file_path = filedialog.askopenfilename(filetypes=[('Pickle files', '*.pkl')])
        if file_path:
            self.canvas.delete('all')
            with open(file_path, 'rb') as file:
                artwork = pickle.load(file)
                for item in artwork:
                    self.canvas.addtag_withtag('loaded', item)
            messagebox.showinfo('Info', 'Artwork loaded successfully')

    def load_gallery(self):
        self.cursor.execute('SELECT artwork_name, file_path FROM gallery WHERE user_id=%s', (self.user_id,))
        gallery_items = self.cursor.fetchall()
        gallery_window = tk.Toplevel(self.root)
        gallery_window.title('Gallery')
        gallery_window.geometry('300x200')
        for item in gallery_items:
            artwork_name, file_path = item
            tk.Button(gallery_window, text=artwork_name,
                      command=lambda fp=file_path: self.load_artwork_from_path(fp)).pack(pady=5)

    def load_artwork_from_path(self, file_path):
        self.canvas.delete('all')
        with open(file_path, 'rb') as file:
            artwork = pickle.load(file)
            for item in artwork:
                self.canvas.addtag_withtag('loaded', item)
        messagebox.showinfo('Info', 'Artwork loaded successfully')


if __name__ == '__main__':
    PyCanvasPalettes().solution()
