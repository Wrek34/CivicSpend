"""CivicSpend Dashboard - Public Spending Transparency."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from civicspend.db.connection import get_connection
from civicspend.explain.evidence import EvidenceBuilder

st.set_page_config(
    page_title="CivicSpend - Public Spending Transparency",
    page_icon="🏛️",
    layout="wide"
)

# Initialize
conn = get_connection()
evidence_builder = EvidenceBuilder()

# Header
st.title("🏛️ CivicSpend: Public Spending Transparency")
st.markdown("**Detecting meaningful changes in public spending with evidence-based analysis**")
st.markdown("---")

# Sidebar - Run Selection
st.sidebar.header("📊 Data Selection")
runs = conn.execute("SELECT run_id, run_timestamp FROM run_manifest ORDER BY run_timestamp DESC").fetchall()

if not runs:
    st.error("No data available. Please run ingestion first.")
    st.stop()

run_options = {f"{r[0][:8]}... ({r[1]})": r[0] for r in runs}
selected_run = st.sidebar.selectbox("Select Run", list(run_options.keys()))
run_id = run_options[selected_run]

# Get summary stats
stats = conn.execute("""
    SELECT 
        COUNT(DISTINCT vendor_id) as vendor_count,
        COUNT(*) as vendor_months,
        SUM(obligation_sum) as total_spend
    FROM monthly_vendor_spend
    WHERE run_id = ?
""", [run_id]).fetchone()

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Vendors Tracked", f"{stats[0]:,}")
with col2:
    st.metric("Vendor-Months", f"{stats[1]:,}")
with col3:
    st.metric("Total Spending", f"${stats[2]:,.0f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Anomaly Detection", "📈 Vendor Analysis", "📋 Evidence Explorer"])

# TAB 1: Anomaly Detection
with tab1:
    st.header("🔍 Detected Spending Anomalies")
    
    # Get anomalies from both methods
    baseline_query = """
        SELECT 
            ve.canonical_name as vendor_name,
            mvs.year_month,
            mvs.obligation_sum as value,
            'baseline' as method,
            'high' as severity
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.run_id = ?
        ORDER BY mvs.obligation_sum DESC
        LIMIT 20
    """
    
    anomalies_df = pd.read_sql_query(baseline_query, conn, params=[run_id])
    
    if anomalies_df.empty:
        st.info("No anomalies detected. Try running detection with lower thresholds.")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            severity_filter = st.multiselect(
                "Severity", 
                ['critical', 'high', 'medium', 'low'],
                default=['critical', 'high']
            )
        with col2:
            method_filter = st.multiselect(
                "Detection Method",
                ['baseline', 'ml'],
                default=['baseline', 'ml']
            )
        
        # Display anomalies
        st.subheader(f"📊 {len(anomalies_df)} Anomalies Found")
        
        # Create visualization
        fig = px.scatter(
            anomalies_df,
            x='year_month',
            y='value',
            color='severity',
            size='value',
            hover_data=['vendor_name', 'method'],
            title='Spending Anomalies Over Time',
            labels={'value': 'Spending Amount ($)', 'year_month': 'Month'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(
            anomalies_df.style.format({'value': '${:,.2f}'}),
            use_container_width=True
        )

# TAB 2: Vendor Analysis
with tab2:
    st.header("📈 Vendor Spending Analysis")
    
    # Get vendor list
    vendors = conn.execute("""
        SELECT DISTINCT ve.vendor_id, ve.canonical_name
        FROM vendor_entities ve
        JOIN monthly_vendor_spend mvs ON ve.vendor_id = mvs.vendor_id
        WHERE mvs.run_id = ?
        ORDER BY ve.canonical_name
    """, [run_id]).fetchall()
    
    vendor_options = {v[1]: v[0] for v in vendors}
    selected_vendor_name = st.selectbox("Select Vendor", list(vendor_options.keys()))
    selected_vendor_id = vendor_options[selected_vendor_name]
    
    # Get vendor timeline
    timeline_df = pd.read_sql_query("""
        SELECT 
            year_month,
            obligation_sum,
            award_count,
            rolling_3m_mean
        FROM monthly_vendor_spend
        WHERE run_id = ? AND vendor_id = ?
        ORDER BY year_month
    """, conn, params=[run_id, selected_vendor_id])
    
    if not timeline_df.empty:
        # Timeline chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_df['year_month'],
            y=timeline_df['obligation_sum'],
            mode='lines+markers',
            name='Monthly Spending',
            line=dict(color='#1f77b4', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=timeline_df['year_month'],
            y=timeline_df['rolling_3m_mean'],
            mode='lines',
            name='3-Month Average',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        fig.update_layout(
            title=f'{selected_vendor_name} - Spending Timeline',
            xaxis_title='Month',
            yaxis_title='Spending ($)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Monthly", f"${timeline_df['obligation_sum'].mean():,.0f}")
        with col2:
            st.metric("Max Month", f"${timeline_df['obligation_sum'].max():,.0f}")
        with col3:
            st.metric("Total Awards", f"{timeline_df['award_count'].sum():,}")
        with col4:
            st.metric("Months Active", len(timeline_df))

# TAB 3: Evidence Explorer
with tab3:
    st.header("📋 Evidence & Award Details")
    
    # Get top spending months
    top_months = pd.read_sql_query("""
        SELECT 
            ve.canonical_name as vendor_name,
            ve.vendor_id,
            mvs.year_month,
            mvs.obligation_sum,
            mvs.award_count
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.run_id = ?
        ORDER BY mvs.obligation_sum DESC
        LIMIT 10
    """, conn, params=[run_id])
    
    st.subheader("🔝 Top 10 Spending Months")
    
    for idx, row in top_months.iterrows():
        with st.expander(f"{row['vendor_name']} - {row['year_month']}: ${row['obligation_sum']:,.2f}"):
            # Get evidence
            evidence = evidence_builder.build_evidence(
                run_id, row['vendor_id'], row['year_month']
            )
            context = evidence_builder.get_vendor_context(run_id, row['vendor_id'])
            
            if evidence:
                st.markdown("**Contributing Awards:**")
                for e in evidence:
                    st.markdown(f"""
                    - **${e['amount']:,.2f}** ({e['pct_of_month']:.1f}% of month)
                      - Agency: {e['agency']}
                      - Date: {e['date']}
                      - Award ID: `{e['award_id']}`
                    """)
            
            if context:
                st.markdown("**Vendor Context:**")
                st.markdown(f"- Average monthly: ${context['avg_monthly']:,.2f}")
                st.markdown(f"- Historical range: ${context['min_monthly']:,.2f} - ${context['max_monthly']:,.2f}")
                st.markdown(f"- Months active: {context['months_active']}")

# Footer
st.markdown("---")
st.markdown("""
**About CivicSpend**: This tool detects meaningful changes in public spending using robust statistics 
and machine learning. Every finding is traceable to specific source awards. 

⚠️ **Important**: This is NOT fraud detection. We identify changes and outliers - not intent or wrongdoing.
All findings require human review and domain context.
""")
