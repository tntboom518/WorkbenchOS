import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import time
from datetime import datetime

# === ГЛАВНОЕ ОКНО (СИМУЛЯТОР ОС) ===
class PyOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Workbench OS")
        self.root.geometry("1000x600")
        self.root.state("zoomed")  # Полный экран
        self.root.configure(bg="#1e1e1e")

        # Стили
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("Taskbar.TButton", font=("Segoe UI", 9), padding=4)

        # Переменные
        self.open_windows = {}  # Для отслеживания открытых окон

        # === РАБОЧИЙ СТОЛ ===
        self.desktop_frame = tk.Frame(self.root, bg="black")
        self.desktop_frame.pack(fill="both", expand=True)

        # Фон
        self.wallpaper = tk.Label(self.desktop_frame, bg="#0f3b5f", text="Добро пожаловать в Workbench OS.", fg="white",
                                  font=("Consolas", 40, "bold"))
        self.wallpaper.place(relwidth=1, relheight=1)
        self.wallpaper.bind("<Double-Button-1>", lambda e: self.open_explorer())

        # === ПАНЕЛЬ ЗАДАЧ ===
        self.taskbar = tk.Frame(root, bg="#000000", height=40)
        self.taskbar.pack(side="bottom", fill="x")

        # Кнопка "Пуск"
        self.start_btn = ttk.Button(self.taskbar, text="🟢 Меню", command=self.toggle_start_menu)
        self.start_btn.pack(side="left", padx=2, pady=2)

        # Иконки быстрого запуска
        quick_launch_apps = [
            ("📁", "Проводник", self.open_explorer),
            ("📝", "Блокнот", self.open_notepad),
            ("🧮", "Калькулятор", self.open_calculator),
        ]
        for emoji, label, cmd in quick_launch_apps:
            b = ttk.Button(self.taskbar, text=emoji, width=3, command=cmd)
            b.pack(side="left", padx=1)

        # Часы
        self.clock_label = tk.Label(self.taskbar, text="", fg="white", bg="black", font=("Consolas", 10))
        self.clock_label.pack(side="right", padx=10)
        self.update_clock()

        # === МЕНЮ "ПУСК" ===
        self.start_menu = None

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def toggle_start_menu(self):
        if self.start_menu and self.start_menu.winfo_exists():
            self.start_menu.destroy()
            return

        self.start_menu = tk.Toplevel(self.root)
        self.start_menu.geometry("300x500")
        self.start_menu.overrideredirect(True)
        self.start_menu.configure(bg="#1e1e1e")
        x = self.root.winfo_x() + 10
        y = self.root.winfo_y() + self.root.winfo_height() - 550
        self.start_menu.geometry(f"+{x}+{y}")

        title = tk.Label(self.start_menu, text="Workbench OS", font=("Segoe UI", 16, "bold"),
                         bg="#1e1e1e", fg="white")
        title.pack(pady=10)

        apps = [
            ("📁 Проводник", self.open_explorer),
            ("📝 Блокнот", self.open_notepad),
            ("🧮 Калькулятор", self.open_calculator),
            ("⚙️ Настройки", self.open_settings),
            ("❓ О системе", self.about),
            ("🔴 Выход", self.shutdown),
        ]

        for text, cmd in apps:
            btn = tk.Button(self.start_menu, text=text, bg="#333", fg="white",
                            font=("Segoe UI", 12), border=0, anchor="w", padx=20,
                            command=cmd)
            btn.pack(fill="x", padx=10, pady=2)

        self.start_menu.bind("<FocusOut>", lambda e: self.start_menu.destroy())

    # === УНИВЕРСАЛЬНОЕ ОКНО ===
    def create_window(self, title, size="600x400"):
        if title in self.open_windows:
            self.open_windows[title].lift()
            return self.open_windows[title]

        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(size)
        window.configure(bg="#2d2d2d")
        window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(title))

        header = tk.Frame(window, bg="#1a1a1a", height=30)
        header.pack(fill="x")
        tk.Label(header, text=title, fg="white", bg="#1a1a1a", font=("Segoe UI", 10)).pack(side="left", padx=10)
        close_btn = tk.Button(header, text="✕", bg="red", fg="white", border=0,
                              command=lambda: self.close_window(title))
        close_btn.pack(side="right", padx=5)

        self.open_windows[title] = window
        return window

    def close_window(self, title):
        if title in self.open_windows:
            self.open_windows[title].destroy()
            del self.open_windows[title]

    # === ПРИЛОЖЕНИЯ ===
    def open_explorer(self):
        window = self.create_window("Проводник", "800x500")
        frame = tk.Frame(window, bg="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(frame, columns=("size",), show="tree headings")
        tree.heading("#0", text="Папки")
        tree.heading("size", text="Размер")
        tree.column("size", width=100)

        root_node = tree.insert("", "end", text=os.path.expanduser("~"), open=False)
        self.populate_tree(tree, root_node, os.path.expanduser("~"))

        tree.pack(side="left", fill="y", padx=(0, 10))

        open_file_btn = tk.Button(frame, text="📂 Открыть файл", command=self.browse_file)
        open_file_btn.pack(pady=10)

        tree.bind("<Double-1>", lambda e: self.on_tree_double_click(tree))

    def populate_tree(self, tree, parent, path):
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = tree.insert(parent, "end", text=item, open=False)
                    tree.insert(node, "end", text="...")  # placeholder
        except PermissionError:
            pass

    def on_tree_double_click(self, tree):
        selected = tree.focus()
        parent = tree.parent(selected)
        parent_path = tree.item(parent, 'text') if parent else os.path.expanduser("~")
        item = tree.item(selected, 'text')
        path = os.path.join(parent_path, item)

        if os.path.isdir(path):
            children = tree.get_children(selected)
            if len(children) == 1 and tree.item(children[0], 'text') == "...":
                for child in children:
                    tree.delete(child)
                self.populate_tree(tree, selected, path)
        else:
            self.launch_file(path)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.launch_file(file_path)

    def launch_file(self, path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def open_notepad(self):
        window = self.create_window("Блокнот", "700x500")
        
        # Панель инструментов
        toolbar = tk.Frame(window, bg="#333333", height=30)
        toolbar.pack(side="top", fill="x")

        save_btn = tk.Button(toolbar, text="💾 Сохранить", fg="white", bg="#007acc", font=("Segoe UI", 9),
                             command=lambda: self.save_text(text_area))
        save_btn.pack(side="left", padx=2, pady=2)

        save_as_btn = tk.Button(toolbar, text="另 Сохранить как", fg="white", bg="#10893e", font=("Segoe UI", 9),
                                command=lambda: self.save_text_as(text_area))
        save_as_btn.pack(side="left", padx=2, pady=2)

        # Текстовое поле
        text_area = tk.Text(window, bg="#1e1e1e", fg="white", insertbackground="white",
                            font=("Consolas", 11), wrap="word")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Добавляем возможность отслеживать, какой файл открыт
        text_area.file_path = None  # Привязываем путь к виджету

    def save_text_as(self, text_area):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text_area.get("1.0", tk.END).strip())
                text_area.file_path = file_path
                messagebox.showinfo("Успех", f"Файл сохранён:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def save_text(self, text_area):
        if text_area.file_path:
            try:
                with open(text_area.file_path, "w", encoding="utf-8") as f:
                    f.write(text_area.get("1.0", tk.END).strip())
                messagebox.showinfo("Сохранено", f"Файл обновлён:\n{text_area.file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")
        else:
            self.save_text_as(text_area)

    def open_calculator(self):
        window = self.create_window("Калькулятор", "300x400")
        calc = Calculator(window)

    def open_settings(self):
        window = self.create_window("Настройки", "500x400")
        tk.Label(window, text="Настройки Workbench OS.\nНедоступно. В релизе 2.0!", bg="#2d2d2d", fg="white",
                 font=("Segoe UI", 14)).pack(expand=True)

    def about(self):
        messagebox.showinfo("О системе", "Workbench OS v1.0\nОС для выполнения простых задач.\n© 2026")

    def shutdown(self):
        if messagebox.askyesno("Выход", "Завершить работу Workbench OS?"):
            self.root.quit()


# === КАЛЬКУЛЯТОР ===
class Calculator:
    def __init__(self, parent):
        self.exp = ""
        self.parent = parent

        self.display = tk.Entry(parent, font=("Arial", 18), borderwidth=5, relief="sunken")
        self.display.grid(row=0, column=0, columnspan=4, pady=10, padx=10)

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ]

        for (text, r, c) in buttons:
            if text == '=':
                b = tk.Button(parent, text=text, bg="#00aaff", fg="white", font=("Arial", 14),
                              command=self.calculate)
            else:
                b = tk.Button(parent, text=text, bg="#333", fg="white", font=("Arial", 14),
                              command=lambda t=text: self.append(t))
            b.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

        for i in range(5):
            parent.grid_rowconfigure(i, weight=1)
            if i < 4:
                parent.grid_columnconfigure(i, weight=1)

    def append(self, char):
        self.exp += str(char)
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.exp)

    def calculate(self):
        try:
            result = eval(self.exp.replace('×', '*').replace('÷', '/'))
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, result)
            self.exp = str(result)
        except:
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, "Ошибка")
            self.exp = ""


# === ЗАПУСК ===
if __name__ == "__main__":
    root = tk.Tk()
    app = PyOS(root)
    root.mainloop()