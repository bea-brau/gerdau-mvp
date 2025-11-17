from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import sqlite3
import pandas as pd
import io
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data.db")

app = FastAPI(title="GERDAU Decision System - MVP (FastAPI)")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        periodo TEXT,
        centro_custo TEXT,
        tipo_custo TEXT,
        valor REAL
    );
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Invalid file type. Use .xlsx, .xls or .csv")
    contents = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading spreadsheet: {e}")
    # Expect columns: periodo, centro_custo, tipo_custo, valor
    expected = {"periodo", "centro_custo", "tipo_custo", "valor"}
    if not expected.issubset(set(map(str.lower, df.columns))):
        # try lowercasing columns
        df.columns = [c.lower() for c in df.columns]
    if not expected.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Spreadsheet must contain columns: {expected}")
    # keep only expected columns
    df = df[list(expected)]
    # save to sqlite (append)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("costs", conn, if_exists="append", index=False)
    conn.close()
    return JSONResponse({"status": "ok", "rows": len(df)})

@app.get("/kpis")
def kpis():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM costs", conn)
    conn.close()
    if df.empty:
        return {"kpis": {}, "top5": [], "evolution": []}
    total = float(df["valor"].sum())
    # variation vs previous period simple calc: latest period vs previous (assumes period sortable)
    periods = df.groupby("periodo")["valor"].sum().reset_index().sort_values("periodo")
    if len(periods) >= 2:
        last = float(periods.iloc[-1]["valor"])
        prev = float(periods.iloc[-2]["valor"])
        variation = round((last - prev) / prev * 100, 2) if prev != 0 else None
    else:
        last = float(periods.iloc[-1]["valor"])
        prev = 0.0
        variation = None
    top5 = df.groupby("tipo_custo")["valor"].sum().reset_index().sort_values("valor", ascending=False).head(5).to_dict(orient="records")
    evolution = periods.to_dict(orient="records")
    return {"kpis": {"total": total, "last_period_value": last, "variation_pct_vs_prev": variation}, "top5": top5, "evolution": evolution}

@app.get("/download-db")
def download_db():
    # for demo/debug: allow download of sqlite db
    db = os.path.abspath(DB_PATH)
    return FileResponse(db, filename="data.db")
