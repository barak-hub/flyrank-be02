from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]
    if count == 0:
        cur.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            [("Buy groceries", False), ("Walk the dog", False), ("Write README", False)]
        )
        conn.commit()
    conn.close()

init_db()

class Task(BaseModel):
    title: str
    done: bool = False

class TaskOut(Task):
    id: int

def row_to_dict(row):
    return {"id": row[0], "title": row[1], "done": bool(row[2])}

@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_dict(row)

@app.post("/tasks", status_code=201)
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, int(task.done))
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "title": task.title, "done": task.done}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task.title, int(task.done), task_id)
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "title": task.title, "done": task.done}

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return
