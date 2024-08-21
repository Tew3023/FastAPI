from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust this as needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def get_time_interval(dt: datetime, interval_minutes: int):
    """Return the start of the time interval for the given datetime."""
    discard_minutes = dt.minute % interval_minutes
    discard_seconds = dt.second
    discard_microseconds = dt.microsecond
    return dt - timedelta(
        minutes=discard_minutes, seconds=discard_seconds, microseconds=discard_microseconds
    )

@app.get("/fetch_stock_data/")
def fetch_stock_data(db: Session = Depends(get_db)):
    try:
        sql_query = text("""
            SELECT * FROM stocksm_tickmatchs WHERE Symbol IN (
                'USDF22', 'USDF23', 'USDF24', 'USDG22', 'USDG23', 'USDG24',
                'USDH22', 'USDH23', 'USDH24', 'USDJ22', 'USDJ23', 'USDJ24',
                'USDK22', 'USDK23', 'USDK24', 'USDM22', 'USDM23', 'USDM24',
                'USDN22', 'USDN23', 'USDN24', 'USDQ22', 'USDQ23', 'USDU21',
                'USDU22', 'USDU23', 'USDU24', 'USDV21', 'USDV22', 'USDV23',
                'USDX21', 'USDX22', 'USDX23', 'USDZ21', 'USDZ22', 'USDZ23'
            )
            ORDER BY DtMinOfRec
        """)
        result = db.execute(sql_query)
        
        rows = result.fetchall()
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]

        # Group data into 30-minute intervals
        grouped_data = {}
        for record in data:
            dt = record['DtMinOfRec']  # DtMinOfRec is already a datetime object
            interval_start = get_time_interval(dt, 30)
            interval_key = interval_start.strftime("%Y-%m-%d %H:%M:%S")
            if interval_key not in grouped_data:
                grouped_data[interval_key] = []
            grouped_data[interval_key].append(record)
        
        # Initialize cumulative flow
        cumulative_flow = 0
        
        # Create result with volumes, times, last prices, and highest last value within each 30-minute interval
        result = []
        for interval, records in grouped_data.items():
            volumes = [record['Vol'] for record in records]
            times = [record['Time'] for record in records]
            lasts = [record['Last'] for record in records]
            high = max(lasts)
            low = min(lasts)
            last_time = max(times)
            total_vol = sum(volumes)
            _open = lasts[0]  
            _close = lasts[-1]  
            price_change = _close - _open  
            flow = total_vol * price_change  
            cumulative_flow += flow
            result.append({
                "interval": interval,
                "vol": total_vol,
                "Time": last_time,
                "high": high,
                "low": low,
                "open": _open,
                "close": _close,
                "flow": flow,
                "flow_accum": cumulative_flow
            })

        return {"usd_data": result}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
