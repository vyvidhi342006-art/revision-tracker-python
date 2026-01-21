import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime,date

BG_COLOR = "#2b2b2b"     # dark background
FG_COLOR = "#ffffff"     # text color
FONT_MAIN = ("Segoe UI", 11)


# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_date TEXT,
    task TEXT,
    revision_date TEXT
)
""")
conn.commit()

# ---------------- TKINTER WINDOW ----------------
root = tk.Tk()
root.title("Revision Tracker")


root.geometry("1500x600")
root.configure(background=BG_COLOR)

# ---------------- GLOBAL LIST ----------------
task_ids = []  # stores DB ids in same order as listbox

# ---------------- FUNCTIONS ----------------

def save_task():
    study_date = study_entry.get().strip()
    task = task_entry.get().strip()
    revision_date = revision_entry.get().strip()

    if not study_date or not task or not revision_date:
        messagebox.showwarning("Error", "All fields are required")
        return

    # Date validation
    try:
        sd = datetime.strptime(study_date, "%d-%m-%Y")
        rd = datetime.strptime(revision_date, "%d-%m-%Y")
        if rd < sd:
            messagebox.showwarning("Error", "Revision date cannot be before study date")
            return
    except ValueError:
        messagebox.showwarning("Error", "Date must be in DD-MM-YYYY format")
        return

    today = date.today()
    # Check past dates
    if sd.date() < today:
            messagebox.showerror(
                "Invalid Date",
                "Study date cannot be before today"
            )
            return
    if rd.date() < today:
            messagebox.showerror(
                "Invalid Date",
                "Revision date cannot be before today"
            )
            return

    cursor.execute(
        "INSERT INTO tasks (study_date, task, revision_date,status) VALUES (?, ?, ?,?)",
        (study_date, task, revision_date,0)
    )
    conn.commit()

    clear_entries()
    load_tasks()


def load_tasks():
    task_listbox.delete(0, tk.END)
    task_ids.clear()

    cursor.execute("SELECT id, study_date, task, revision_date FROM tasks WHERE status = 0")
    rows = cursor.fetchall()

    for row in rows:
        task_id, study_date, task, revision_date = row
        display_text = f"{study_date} | {task} | Revise: {revision_date}"
        task_listbox.insert(tk.END, display_text)
        task_ids.append(task_id)

#--------CHECK DUE TASKS---------#
def check_due_tasks():
    today=datetime.today().strftime("%d-%m-%Y")
    cursor.execute("SELECT task FROM tasks where revision_date=? ", (today,))
    rows = cursor.fetchall()
    if rows:
        message="Tasks to revise today: \n\n"
        for row in rows:
            message+=f" {row[0]}\n"
            messagebox.showinfo("Revision Reminder",message)


def delete_task():
    selected = task_listbox.curselection()

    if not selected:
        messagebox.showwarning("Error", "No task selected")
        return

    index = selected[0]
    task_id = task_ids[index]

    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

    load_tasks()
def mark_completed():
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("Error", "No task selected")
        return
    index = selected[0]
    task_id = task_ids[index]

    cursor.execute("UPDATE tasks SET status = 1 WHERE id=?", (task_id,))
    conn.commit()
    load_tasks()
def load_completed_tasks():
    task_listbox.delete(0, tk.END)
    task_ids.clear()

    cursor.execute(
        "SELECT id, study_date, task, revision_date FROM tasks WHERE status = 1"
    )
    rows = cursor.fetchall()

    for row in rows:
        task_id, study_date, task, revision_date = row
        display_text = f"{study_date} | {task} | Completed on: {revision_date}"
        task_listbox.insert(tk.END, display_text)
        task_ids.append(task_id)



def clear_entries():
    study_entry.delete(0, tk.END)
    task_entry.delete(0, tk.END)
    revision_entry.delete(0, tk.END)

# ---------------- UI ----------------
BTN_PRIMARY = "#4a90e2"   # Save
BTN_SUCCESS = "#5cb85c"   # Mark Completed
BTN_DANGER = "#d9534f"    # Delete
BTN_NEUTRAL = "#6c757d"   # Show Pending / Completed


tk.Label(root, text="Study Date (DD-MM-YYYY)",bg=BG_COLOR,fg=FG_COLOR).grid(row=0, column=0, padx=5, pady=5)
study_entry = tk.Entry(root, width=20)
study_entry.grid(row=0, column=1, padx=5)

tk.Label(root, text="Task",bg=BG_COLOR,fg=FG_COLOR).grid(row=0, column=2, padx=5)
task_entry = tk.Entry(root, width=30)
task_entry.grid(row=0, column=3, padx=5)

tk.Label(root, text="Revision Date (DD-MM-YYYY)",bg=BG_COLOR,fg=FG_COLOR).grid(row=0, column=4, padx=5)
revision_entry = tk.Entry(root, width=20)
revision_entry.grid(row=0, column=5, padx=5)

# save_button = tk.Button(root, text="Save Task", command=save_task)
# save_button.grid(row=1, column=3, pady=10)
save_button = tk.Button(
    root,
    text="Save Task",
    bg=BTN_PRIMARY,
    fg="blue",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    padx=10,
    pady=5,
    command=save_task
)
save_button.grid(row=1, column=3, pady=10)


# delete_button = tk.Button(root, text="Delete Task", command=delete_task)
#delete_button.grid(row=1,column=4,pady=10)
delete_button = tk.Button(
    root,
    text="Delete Task",
    bg=BTN_DANGER,
    fg="red",
    font=("Segoe UI", 11),
    relief="flat",
    padx=10,
    pady=5,
    command=delete_task
 )
delete_button.grid(row=1,column=4,pady=10)

task_listbox = tk.Listbox(root, width=90, height=15)
task_listbox.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

#mark_button=tk.Button(root, text="Mark Task As Completed", command=mark_completed)
mark_button = tk.Button(
    root,
    text="Mark Completed",
    bg=BTN_SUCCESS,
    fg="green",
    font=("Segoe UI", 11),
    relief="flat",
    padx=10,
    pady=5,
    command=mark_completed
)

mark_button.grid(row=3,column=4,pady=10)

# show_completed_btn = tk.Button(
#     root,
#     text="Show Completed Tasks",
#     command=load_completed_tasks
# )
show_pending_btn = tk.Button(
    root,
    text="Show Pending Tasks",
    bg=BTN_NEUTRAL,
    fg="black",
    font=("Segoe UI", 11),
    relief="flat",
    padx=10,
    pady=5,
    command=load_tasks
)

show_completed_btn = tk.Button(
    root,
    text="Show Completed Tasks",
    bg=BTN_NEUTRAL,
    fg="black",
    font=("Segoe UI", 11),
    relief="flat",
    padx=10,
    pady=5,
    command=load_completed_tasks
)

show_completed_btn.grid(row=3, column=5, pady=10)

# show_pending_btn = tk.Button(
#     root,
#     text="Show Pending Tasks",
#     command=load_tasks
# )
show_pending_btn.grid(row=3, column=6, pady=10)



# Load saved tasks on startup
load_tasks()
check_due_tasks()

root.mainloop()
conn.close()