"""CivicSpend Dashboard - Standalone Version."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
from pathlib import Path

st.set_page_config(
    page_title="CivicSpend - Public Spending Transparency",
    page_icon="🏛️",
    layout="wide"
)

# Initialize database
db_path = Path("data/civicspend.duckdb")
db_path.parent.mkdir(exist_ok=True)

try:
    conn = duckdb.connect(str(db_path))
    
    # Check if tables exist
    tables = conn.execute("SHOW TABLES").fetchall()
    if not tables:
        st.warning("No data available. Generating demo data...")
        
        # Create minimal schema
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vendor_entities (
                vendor_id VARCHAR PRIMARY KEY,
                canonical_name VARCHAR
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monthly_vendor_spend (
                vendor_id VARCHAR,
                month DATE,
                obligation_sum DECIMAL(18,2),
                award_count INTEGER,
                rolling_3m_avg DECIMAL(18,2)
            )
        """)
        
        # Insert demo data
        conn.execute("""
            INSERT INTO vendor_entities VALUES 
            ('v1', '3M Company'),
            ('v2', 'Ecolab Inc'),
            ('v3', 'Target Corporation')
        """)
        
        conn.execute("""
            INSERT INTO monthly_vendor_spend VALUES 
            ('v1', '2024-01-01', 5000000, 10, 4500000),
            ('v1', '2024-02-01', 6000000, 12, 5000000),
            ('v2', '2024-01-01', 3000000, 8, 2800000),
            ('v2', '2024-02-01', 9000000, 15, 4000000),
            ('v3', '2024-01-01', 2000000, 5, 1800000)
        """)
        
        st.success("Demo data created!")
        st.rerun()

except Exception as e:
    st.error(f"Database error: {e}")
    st.info("Using in-memory demo data instead")
    conn = duckdb.connect(":memory:")
    
    conn.execute("""
        CREATE TABLE vendor_entities (
            vendor_id VARCHAR,
            canonical_name VARCHAR
        )
    """)
    
    conn.execute("""
        CREATE TABLE monthly_vendor_spend (
            vendor_id VARCHAR,
            month DATE,
            obligation_sum DECIMAL(18,2),
            award_count INTEGER,
            rolling_3m_avg DECIMAL(18,2)
        )
    """)
    
    conn.execute("""
        INSERT INTO vendor_entities VALUES 
        ('v1', '3M Company'),
        ('v2', 'Ecolab Inc'),
        ('v3', 'Target Corporation')
    """)
    
    conn.execute("""
        INSERT INTO monthly_vendor_spend VALUES 
        ('v1', '2024-01-01', 5000000, 10, 4500000),
        ('v1', '2024-02-01', 6000000, 12, 5000000),
        ('v2', '2024-01-01', 3000000, 8, 2800000),
        ('v2', '2024-02-01', 9000000, 15, 4000000),
        ('v3', '2024-01-01', 2000000, 5, 1800000)
    """)

st.title("🏛️ CivicSpend: Public Spending Transparency")
st.markdown("**Detecting meaningful changes in public spending**")
st.markdown("---")

# Summary stats
try:
    stats = conn.execute("""
        SELECT COUNT(DISTINCT vendor_id) as vendors,
               SUM(obligation_sum) as total_spend,
               SUM(award_count) as total_awards
        FROM monthly_vendor_spend
    """).fetchone()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Vendors", f"{stats[0]:,}")
    with col2:
        st.metric("Total Spending", f"${stats[1]:,.0f}")
    with col3:
        st.metric("Total Awards", f"{stats[2]:,}")
except Exception as e:
    st.error(f"Error loading stats: {e}")

st.markdown("---")

# Tabs
tab1, tab2 = st.tabs(["📊 Spending Overview", "📈 Vendor Analysis"])

with tab1:
    st.header("Spending Overview")
    
    try:
        df = pd.read_sql_query("""
            SELECT ve.canonical_name, mvs.month, mvs.obligation_sum, mvs.award_count
            FROM monthly_vendor_spend mvs
            JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
            ORDER BY mvs.month, mvs.obligation_sum DESC
        """, conn)
        
        if not df.empty:
            fig = px.bar(df, x='month', y='obligation_sum', color='canonical_name',
                        title='Monthly Spending by Vendor',
                        labels={'obligation_sum': 'Spending ($)', 'month': 'Month'})
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df.style.format({'obligation_sum': '${:,.2f}'}), 
                        use_container_width=True)
        else:
            st.info("No data available")
    except Exception as e:
        st.error(f"Error loading data: {e}")

with tab2:
    st.header("Vendor Analysis")
    
    try:
        vendors = conn.execute("""
            SELECT DISTINCT ve.vendor_id, ve.canonical_name
            FROM vendor_entities ve
            ORDER BY ve.canonical_name
        """).fetchall()
        
        if vendors:
            vendor_options = {v[1]: v[0] for v in vendors}
            selected_vendor = st.selectbox("Select Vendor", list(vendor_options.keys()))
            vendor_id = vendor_options[selected_vendor]
            
            timeline_df = pd.read_sql_query("""
                SELECT month, obligation_sum, award_count, rolling_3m_avg
                FROM monthly_vendor_spend
                WHERE vendor_id = ?
                ORDER BY month
            """, conn, params=[vendor_id])
            
            if not timeline_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timeline_df['month'], 
                    y=timeline_df['obligation_sum'],
                    mode='lines+markers', 
                    name='Monthly Spending'
                ))
                if timeline_df['rolling_3m_avg'].notna().any():
                    fig.add_trace(go.Scatter(
                        x=timeline_df['month'], 
                        y=timeline_df['rolling_3m_avg'],
                        mode='lines', 
                        name='3-Month Average',
                        line=dict(dash='dash')
                    ))
                fig.update_layout(
                    title=f'{selected_vendor} - Spending Timeline',
                    xaxis_title='Month',
                    yaxis_title='Spending ($)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Avg Monthly", f"${timeline_df['obligation_sum'].mean():,.0f}")
                with col2:
                    st.metric("Total Awards", f"{timeline_df['award_count'].sum():,}")
            else:
                st.info("No data for selected vendor")
        else:
            st.info("No vendors available")
    except Exception as e:
        st.error(f"Error loading vendor data: {e}")

st.markdown("---")
st.markdown("""
**About CivicSpend**: Detects meaningful changes in public spending using robust statistics and ML.

⚠️ **Important**: This is NOT fraud detection. We identify changes and outliers - not intent.
""")
