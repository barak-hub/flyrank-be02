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
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_dict(row)
