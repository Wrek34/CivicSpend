"""Enhanced CivicSpend Dashboard with History & Analysis."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from civicspend.db.connection import get_connection
from civicspend.ui.demo_data import ensure_demo_data

st.set_page_config(
    page_title="CivicSpend - Public Spending Transparency",
    page_icon="🏛️",
    layout="wide"
)

try:
    run_id = ensure_demo_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

conn = get_connection()

st.title("🏛️ CivicSpend: Public Spending Transparency")
st.markdown("**Detecting meaningful changes in public spending with evidence-based analysis**")
st.markdown("---")

# Sidebar
st.sidebar.header("📊 Data Selection")
runs = conn.execute("SELECT run_id, created_at FROM run_manifest ORDER BY created_at DESC").fetchall()

if not runs:
    st.error("No data available")
    st.stop()

run_options = {f"{r[0][:8]}... ({r[1]})": r[0] for r in runs}
selected_run = st.sidebar.selectbox("Select Run", list(run_options.keys()))
run_id = run_options[selected_run]

# Summary stats
stats = conn.execute("""
    SELECT COUNT(DISTINCT vendor_id) as vendors,
           COUNT(*) as vendor_months,
           SUM(obligation_sum) as total_spend
    FROM monthly_vendor_spend WHERE run_id = ?
""", [run_id]).fetchone()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Vendors Tracked", f"{stats[0]:,}")
with col2:
    st.metric("Vendor-Months", f"{stats[1]:,}")
with col3:
    st.metric("Total Spending", f"${stats[2]:,.0f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Anomaly Detection",
    "📈 Vendor Analysis", 
    "📋 Evidence Explorer",
    "📜 Award History",
    "📊 Spending Analysis"
])

# TAB 1: Anomaly Detection
with tab1:
    st.header("🔍 Detected Spending Anomalies")
    
    anomalies_df = pd.read_sql_query("""
        SELECT ve.canonical_name as vendor_name, mvs.month,
               mvs.obligation_sum as value, mvs.award_count,
               CASE 
                   WHEN mvs.obligation_sum > mvs.rolling_3m_avg * 3 THEN 'critical'
                   WHEN mvs.obligation_sum > mvs.rolling_3m_avg * 2 THEN 'high'
                   ELSE 'medium'
               END as severity
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.run_id = ? AND mvs.rolling_3m_avg IS NOT NULL
        ORDER BY mvs.obligation_sum DESC LIMIT 50
    """, conn, params=[run_id])
    
    if not anomalies_df.empty:
        fig = px.scatter(anomalies_df, x='month', y='value', color='severity',
                        size='value', hover_data=['vendor_name', 'award_count'],
                        title='Spending Anomalies Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(anomalies_df.style.format({'value': '${:,.2f}'}), use_container_width=True)

# TAB 2: Vendor Analysis
with tab2:
    st.header("📈 Vendor Spending Analysis")
    
    vendors = conn.execute("""
        SELECT DISTINCT ve.vendor_id, ve.canonical_name
        FROM vendor_entities ve
        JOIN monthly_vendor_spend mvs ON ve.vendor_id = mvs.vendor_id
        WHERE mvs.run_id = ? ORDER BY ve.canonical_name
    """, [run_id]).fetchall()
    
    vendor_options = {v[1]: v[0] for v in vendors}
    selected_vendor_name = st.selectbox("Select Vendor", list(vendor_options.keys()))
    selected_vendor_id = vendor_options[selected_vendor_name]
    
    timeline_df = pd.read_sql_query("""
        SELECT month, obligation_sum, award_count, rolling_3m_avg
        FROM monthly_vendor_spend
        WHERE run_id = ? AND vendor_id = ? ORDER BY month
    """, conn, params=[run_id, selected_vendor_id])
    
    if not timeline_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timeline_df['month'], y=timeline_df['obligation_sum'],
                                mode='lines+markers', name='Monthly Spending'))
        fig.add_trace(go.Scatter(x=timeline_df['month'], y=timeline_df['rolling_3m_avg'],
                                mode='lines', name='3-Month Average', line=dict(dash='dash')))
        fig.update_layout(title=f'{selected_vendor_name} - Spending Timeline',
                         xaxis_title='Month', yaxis_title='Spending ($)')
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Monthly", f"${timeline_df['obligation_sum'].mean():,.0f}")
        with col2:
            st.metric("Max Month", f"${timeline_df['obligation_sum'].max():,.0f}")
        with col3:
            st.metric("Total Awards", f"{timeline_df['award_count'].sum():,}")

# TAB 3: Evidence Explorer
with tab3:
    st.header("📋 Evidence & Award Details")
    
    top_months = pd.read_sql_query("""
        SELECT ve.canonical_name as vendor_name, ve.vendor_id,
               mvs.month, mvs.obligation_sum, mvs.award_count
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.run_id = ? ORDER BY mvs.obligation_sum DESC LIMIT 10
    """, conn, params=[run_id])
    
    for idx, row in top_months.iterrows():
        with st.expander(f"{row['vendor_name']} - {row['month']}: ${row['obligation_sum']:,.2f}"):
            awards = pd.read_sql_query("""
                SELECT ra.award_id, ra.total_obligation, ra.action_date,
                       ra.awarding_agency_name, ra.award_description
                FROM raw_awards ra
                JOIN award_vendor_map avm ON ra.award_id = avm.award_id
                WHERE avm.vendor_id = ? AND ra.run_id = ?
                  AND strftime('%Y-%m', ra.action_date) = ?
                ORDER BY ra.total_obligation DESC LIMIT 5
            """, conn, params=[row['vendor_id'], run_id, row['month'][:7]])
            
            if not awards.empty:
                for _, award in awards.iterrows():
                    st.markdown(f"""
                    - **${award['total_obligation']:,.2f}** - {award['awarding_agency_name']}
                      - Date: {award['action_date']}
                      - Award ID: `{award['award_id']}`
                    """)

# TAB 4: Award History
with tab4:
    st.header("📜 Complete Award History")
    
    st.subheader("Search Awards")
    col1, col2 = st.columns(2)
    with col1:
        search_vendor = st.selectbox("Filter by Vendor", ["All"] + list(vendor_options.keys()), key="history_vendor")
    with col2:
        min_amount = st.number_input("Min Amount ($)", value=0, step=10000)
    
    query = """
        SELECT ra.award_id, ra.total_obligation, ra.action_date,
               ve.canonical_name as vendor_name,
               ra.awarding_agency_name, ra.award_description
        FROM raw_awards ra
        JOIN award_vendor_map avm ON ra.award_id = avm.award_id
        JOIN vendor_entities ve ON avm.vendor_id = ve.vendor_id
        WHERE ra.run_id = ? AND ra.total_obligation >= ?
    """
    params = [run_id, min_amount]
    
    if search_vendor != "All":
        query += " AND ve.vendor_id = ?"
        params.append(vendor_options[search_vendor])
    
    query += " ORDER BY ra.action_date DESC LIMIT 100"
    
    history_df = pd.read_sql_query(query, conn, params=params)
    
    if not history_df.empty:
        st.dataframe(
            history_df.style.format({'total_obligation': '${:,.2f}'}),
            use_container_width=True
        )
        st.caption(f"Showing {len(history_df)} awards")

# TAB 5: Spending Analysis
with tab5:
    st.header("📊 In-Depth Spending Analysis")
    
    # Spending trends
    st.subheader("Monthly Spending Trends")
    trends_df = pd.read_sql_query("""
        SELECT month, SUM(obligation_sum) as total_spending,
               COUNT(DISTINCT vendor_id) as active_vendors,
               SUM(award_count) as total_awards
        FROM monthly_vendor_spend
        WHERE run_id = ? GROUP BY month ORDER BY month
    """, conn, params=[run_id])
    
    if not trends_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=trends_df['month'], y=trends_df['total_spending'],
                            name='Total Spending'))
        fig.update_layout(title='Monthly Spending Trends', xaxis_title='Month',
                         yaxis_title='Total Spending ($)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Top vendors
    st.subheader("Top 10 Vendors by Total Spending")
    top_vendors_df = pd.read_sql_query("""
        SELECT ve.canonical_name, SUM(mvs.obligation_sum) as total_spending,
               COUNT(DISTINCT mvs.month) as months_active
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.run_id = ?
        GROUP BY ve.vendor_id, ve.canonical_name
        ORDER BY total_spending DESC LIMIT 10
    """, conn, params=[run_id])
    
    if not top_vendors_df.empty:
        fig = px.bar(top_vendors_df, x='canonical_name', y='total_spending',
                    title='Top 10 Vendors', labels={'total_spending': 'Total Spending ($)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Agency distribution
    st.subheader("Spending by Agency")
    agency_df = pd.read_sql_query("""
        SELECT awarding_agency_name, SUM(total_obligation) as total_spending,
               COUNT(*) as award_count
        FROM raw_awards
        WHERE run_id = ?
        GROUP BY awarding_agency_name
        ORDER BY total_spending DESC LIMIT 10
    """, conn, params=[run_id])
    
    if not agency_df.empty:
        fig = px.pie(agency_df, values='total_spending', names='awarding_agency_name',
                    title='Top 10 Agencies by Spending')
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
**About CivicSpend**: Detects meaningful changes in public spending using robust statistics and ML.
Every finding is traceable to specific source awards.

⚠️ **Important**: This is NOT fraud detection. We identify changes and outliers - not intent or wrongdoing.
""")
