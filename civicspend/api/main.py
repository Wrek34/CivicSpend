"""FastAPI application for CivicSpend API."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import date
import pandas as pd

from civicspend.db.connection import get_connection

app = FastAPI(
    title="CivicSpend API",
    description="Public Spending Transparency API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = get_connection()


@app.get("/")
def root():
    return {
        "name": "CivicSpend API",
        "version": "0.1.0",
        "endpoints": {
            "/runs": "List all runs",
            "/vendors": "List vendors",
            "/vendors/{vendor_id}/timeline": "Vendor timeline",
            "/vendors/{vendor_id}/history": "Vendor history",
            "/anomalies": "List anomalies",
            "/spending/summary": "Spending summary",
            "/spending/trends": "Spending trends"
        }
    }


@app.get("/runs")
def list_runs():
    query = "SELECT run_id, created_at, state, record_count FROM run_manifest ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn)
    return df.to_dict(orient="records")


@app.get("/vendors")
def list_vendors(run_id: Optional[str] = None, limit: int = Query(100, le=1000)):
    query = """
        SELECT ve.vendor_id, ve.canonical_name,
               COUNT(DISTINCT mvs.month) as months_active,
               SUM(mvs.obligation_sum) as total_spending
        FROM vendor_entities ve
        JOIN monthly_vendor_spend mvs ON ve.vendor_id = mvs.vendor_id
    """
    if run_id:
        query += f" WHERE mvs.run_id = '{run_id}'"
    query += " GROUP BY ve.vendor_id, ve.canonical_name ORDER BY total_spending DESC LIMIT ?"
    
    df = pd.read_sql_query(query, conn, params=[limit])
    return df.to_dict(orient="records")


@app.get("/vendors/{vendor_id}/timeline")
def vendor_timeline(vendor_id: str, run_id: Optional[str] = None):
    query = """
        SELECT month, obligation_sum, award_count, rolling_3m_avg
        FROM monthly_vendor_spend WHERE vendor_id = ?
    """
    params = [vendor_id]
    if run_id:
        query += " AND run_id = ?"
        params.append(run_id)
    query += " ORDER BY month"
    
    df = pd.read_sql_query(query, conn, params=params)
    if df.empty:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return df.to_dict(orient="records")


@app.get("/vendors/{vendor_id}/history")
def vendor_history(vendor_id: str, run_id: Optional[str] = None, limit: int = Query(50, le=500)):
    query = """
        SELECT ra.award_id, ra.total_obligation, ra.action_date,
               ra.awarding_agency_name, ra.award_description
        FROM raw_awards ra
        JOIN award_vendor_map avm ON ra.award_id = avm.award_id
        WHERE avm.vendor_id = ?
    """
    params = [vendor_id]
    if run_id:
        query += " AND ra.run_id = ?"
        params.append(run_id)
    query += " ORDER BY ra.action_date DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    if df.empty:
        raise HTTPException(status_code=404, detail="No awards found")
    return df.to_dict(orient="records")


@app.get("/anomalies")
def list_anomalies(run_id: Optional[str] = None, limit: int = Query(100, le=1000)):
    query = """
        SELECT ve.vendor_id, ve.canonical_name as vendor_name,
               mvs.month, mvs.obligation_sum, mvs.award_count,
               CASE 
                   WHEN mvs.obligation_sum > mvs.rolling_3m_avg * 3 THEN 'critical'
                   WHEN mvs.obligation_sum > mvs.rolling_3m_avg * 2 THEN 'high'
                   ELSE 'medium'
               END as severity
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.rolling_3m_avg IS NOT NULL
    """
    params = []
    if run_id:
        query += " AND mvs.run_id = ?"
        params.append(run_id)
    query += " ORDER BY mvs.obligation_sum DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    return df.to_dict(orient="records")


@app.get("/spending/summary")
def spending_summary(run_id: Optional[str] = None):
    query = """
        SELECT COUNT(DISTINCT vendor_id) as total_vendors,
               SUM(obligation_sum) as total_spending,
               AVG(obligation_sum) as avg_monthly_spending,
               SUM(award_count) as total_awards
        FROM monthly_vendor_spend
    """
    if run_id:
        query += f" WHERE run_id = '{run_id}'"
    
    result = conn.execute(query).fetchone()
    return {
        "total_vendors": result[0],
        "total_spending": float(result[1]) if result[1] else 0,
        "avg_monthly_spending": float(result[2]) if result[2] else 0,
        "total_awards": result[3]
    }


@app.get("/spending/trends")
def spending_trends(run_id: Optional[str] = None):
    query = """
        SELECT month, SUM(obligation_sum) as total_spending,
               COUNT(DISTINCT vendor_id) as active_vendors
        FROM monthly_vendor_spend WHERE 1=1
    """
    params = []
    if run_id:
        query += " AND run_id = ?"
        params.append(run_id)
    query += " GROUP BY month ORDER BY month"
    
    df = pd.read_sql_query(query, conn, params=params)
    return df.to_dict(orient="records")


@app.get("/health")
def health_check():
    try:
        conn.execute("SELECT 1").fetchone()
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
