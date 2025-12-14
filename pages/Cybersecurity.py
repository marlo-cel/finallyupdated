import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Add app directory to path
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

from data import incidents

st.set_page_config(page_title="Cybersecurity Dashboard", page_icon="🛡️", layout="wide")

# Check authentication
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login first to access this dashboard")
    st.info("Redirecting to login page...")
    st.switch_page("app.py")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"**Role:** {st.session_state.role}")
    st.markdown("---")
    st.markdown("### Navigation")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.role = None
        st.switch_page("app.py")

    st.markdown("---")
    st.markdown("### Filters")
    severity_filter = st.multiselect(
        "Filter by Severity",
        ["Low", "Medium", "High", "Critical"],
        default=["Low", "Medium", "High", "Critical"]
    )

# Header
st.title("🛡️ Cybersecurity Dashboard")
st.markdown(f"**Incident Management & Analytics** | Logged in as: {st.session_state.username}")
st.markdown("---")

# View selector
view_mode = st.radio(
    "Select View:",
    ["📈 Analytics & Visualizations", "📝 Manage Incidents", "➕ Create New Incident"],
    horizontal=True
)


# Load data
@st.cache_data(ttl=60)
def load_incidents_data():
    rows = incidents.get_all_incidents()
    if not rows:
        return pd.DataFrame(columns=["id", "title", "description", "severity", "date_reported", "reported_by"])
    data = [dict(row) for row in rows]
    df = pd.DataFrame(data)
    if len(df) > 0:
        df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
    return df


df = load_incidents_data()

# Apply filters
if not df.empty:
    df_filtered = df[df['severity'].isin(severity_filter)]
else:
    df_filtered = df

# ===============================
# ANALYTICS VIEW
# ===============================
if view_mode == "📈 Analytics & Visualizations":

    if df_filtered.empty:
        st.warning("⚠️ No incidents found. Create some incidents to see analytics!")
        st.stop()

    # Key Metrics
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Incidents", len(df_filtered))
    with col2:
        critical_count = len(df_filtered[df_filtered['severity'] == 'Critical'])
        st.metric("🔴 Critical", critical_count)
    with col3:
        high_count = len(df_filtered[df_filtered['severity'] == 'High'])
        st.metric("🟠 High", high_count)
    with col4:
        medium_count = len(df_filtered[df_filtered['severity'] == 'Medium'])
        st.metric("🟡 Medium", medium_count)
    with col5:
        low_count = len(df_filtered[df_filtered['severity'] == 'Low'])
        st.metric("🟢 Low", low_count)

    st.markdown("---")

    # Visualizations in tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📅 Time Series Analysis", "📊 Severity Distribution", "📈 Monthly Trends", "🔍 Detailed Breakdown"])

    with tab1:
        st.subheader("Incidents Over Time")

        # Time series chart
        df_time = df_filtered.copy()
        df_time['date'] = df_time['date_reported'].dt.date
        time_series = df_time.groupby(['date', 'severity']).size().reset_index(name='count')

        fig_time = px.line(
            time_series,
            x='date',
            y='count',
            color='severity',
            title='Daily Incident Frequency by Severity',
            labels={'date': 'Date', 'count': 'Number of Incidents', 'severity': 'Severity Level'},
            color_discrete_map={
                'Low': '#90EE90',
                'Medium': '#FFD700',
                'High': '#FFA500',
                'Critical': '#FF4500'
            }
        )
        fig_time.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig_time, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(
                f"📅 **Date Range:** {df_filtered['date_reported'].min().date()} to {df_filtered['date_reported'].max().date()}")
        with col2:
            days_span = max((df_filtered['date_reported'].max() - df_filtered['date_reported'].min()).days, 1)
            avg_per_day = len(df_filtered) / days_span
            st.info(f"📊 **Avg Incidents/Day:** {avg_per_day:.2f}")
        with col3:
            recent_7days = len(df_filtered[df_filtered['date_reported'] >= (datetime.now() - timedelta(days=7))])
            st.info(f"🕐 **Last 7 Days:** {recent_7days} incidents")

    with tab2:
        st.subheader("Severity Distribution Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            severity_counts = df_filtered['severity'].value_counts()
            fig_pie = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                title='Distribution by Severity Level',
                color=severity_counts.index,
                color_discrete_map={
                    'Low': '#90EE90',
                    'Medium': '#FFD700',
                    'High': '#FFA500',
                    'Critical': '#FF4500'
                },
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                title='Incident Count by Severity',
                labels={'x': 'Severity Level', 'y': 'Number of Incidents'},
                color=severity_counts.index,
                color_discrete_map={
                    'Low': '#90EE90',
                    'Medium': '#FFD700',
                    'High': '#FFA500',
                    'Critical': '#FF4500'
                }
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        # Severity table
        st.markdown("### Severity Breakdown Table")
        severity_df = pd.DataFrame({
            'Severity': severity_counts.index,
            'Count': severity_counts.values,
            'Percentage': [f"{(v / severity_counts.sum() * 100):.1f}%" for v in severity_counts.values]
        })
        st.dataframe(severity_df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Monthly Trend Analysis")

        # Monthly trend
        df_monthly = df_filtered.copy()
        df_monthly['month'] = df_monthly['date_reported'].dt.to_period('M').astype(str)
        monthly_counts = df_monthly.groupby('month').size().reset_index(name='count')

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly_counts['month'],
            y=monthly_counts['count'],
            mode='lines+markers',
            name='Incidents',
            line=dict(color='#4169E1', width=3),
            marker=dict(size=12),
            fill='tozeroy',
            fillcolor='rgba(65, 105, 225, 0.2)'
        ))
        fig_trend.update_layout(
            title='Monthly Incident Volume',
            xaxis_title='Month',
            yaxis_title='Number of Incidents',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Monthly breakdown by severity
        monthly_severity = df_monthly.groupby(['month', 'severity']).size().reset_index(name='count')
        fig_monthly_sev = px.bar(
            monthly_severity,
            x='month',
            y='count',
            color='severity',
            title='Monthly Incidents by Severity',
            labels={'month': 'Month', 'count': 'Count'},
            color_discrete_map={
                'Low': '#90EE90',
                'Medium': '#FFD700',
                'High': '#FFA500',
                'Critical': '#FF4500'
            }
        )
        st.plotly_chart(fig_monthly_sev, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if len(monthly_counts) > 0:
                peak_month = monthly_counts.loc[monthly_counts['count'].idxmax(), 'month']
                st.metric("📈 Peak Month", peak_month)
            else:
                st.metric("📈 Peak Month", "N/A")
        with col2:
            if len(monthly_counts) > 0:
                st.metric("🔝 Peak Count", monthly_counts['count'].max())
            else:
                st.metric("🔝 Peak Count", 0)
        with col3:
            if len(monthly_counts) > 1:
                trend = "📈 Increasing" if monthly_counts['count'].iloc[-1] > monthly_counts['count'].iloc[0] else "📉 Decreasing"
            else:
                trend = "➡️ Stable"
            st.metric("Trend Direction", trend)

    with tab4:
        st.subheader("Detailed Incident Breakdown")

        # Show recent incidents
        st.markdown("### Recent Incidents (Last 10)")
        recent_df = df_filtered.sort_values('date_reported', ascending=False).head(10)

        display_df = recent_df[['id', 'title', 'severity', 'date_reported']].copy()
        display_df['date_reported'] = display_df['date_reported'].dt.strftime('%Y-%m-%d %H:%M')

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "title": st.column_config.TextColumn("Title", width="large"),
                "severity": st.column_config.TextColumn("Severity", width="small"),
                "date_reported": st.column_config.TextColumn("Date", width="medium")
            }
        )

# ===============================
# MANAGE INCIDENTS VIEW
# ===============================
elif view_mode == "📝 Manage Incidents":

    st.subheader("Incident Management")

    if df_filtered.empty:
        st.info("📋 No incidents to display. Create your first incident using the 'Create New Incident' view.")
    else:
        # Search functionality
        search_term = st.text_input("🔍 Search incidents", placeholder="Search by title or description...")

        if search_term:
            df_display = df_filtered[
                df_filtered['title'].str.contains(search_term, case=False, na=False) |
                df_filtered['description'].str.contains(search_term, case=False, na=False)
            ]
        else:
            df_display = df_filtered

        st.markdown(f"**Showing {len(df_display)} incidents**")

        # Display incidents
        for idx, row in df_display.iterrows():
            severity_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}

            with st.expander(
                    f"{severity_emoji.get(row['severity'], '⚪')} **{row['title']}** - {row['severity']} ({row['date_reported'].strftime('%Y-%m-%d')})"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Date Reported:** {row['date_reported'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Incident ID:** {row['id']}")
                    if row['reported_by']:
                        st.write(f"**Reported By:** User ID {row['reported_by']}")

                with col2:
                    if st.button("🗑️ Delete", key=f"del_{row['id']}", use_container_width=True):
                        incidents.delete_incident(row['id'])
                        st.success("✅ Incident deleted!")
                        st.cache_data.clear()
                        st.rerun()

                    if st.button("✏️ Edit", key=f"edit_{row['id']}", use_container_width=True):
                        st.session_state[f"editing_{row['id']}"] = True

                # Edit form
                if st.session_state.get(f"editing_{row['id']}", False):
                    st.markdown("---")
                    st.markdown("**✏️ Edit Incident**")
                    with st.form(f"edit_form_{row['id']}"):
                        new_title = st.text_input("Title", value=row['title'])
                        new_desc = st.text_area("Description", value=row['description'])
                        new_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"],
                                                    index=["Low", "Medium", "High", "Critical"].index(row['severity']))

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Save", use_container_width=True):
                                incidents.update_incident(
                                    row['id'],
                                    title=new_title,
                                    description=new_desc,
                                    severity=new_severity
                                )
                                st.session_state[f"editing_{row['id']}"] = False
                                st.success("✅ Incident updated!")
                                st.cache_data.clear()
                                st.rerun()
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"editing_{row['id']}"] = False
                                st.rerun()

# ===============================
# CREATE INCIDENT VIEW
# ===============================
elif view_mode == "➕ Create New Incident":

    st.subheader("Create New Cyber Incident")

    with st.form("create_incident_form", clear_on_submit=True):
        title = st.text_input("Incident Title*", placeholder="Brief description of the incident")
        description = st.text_area("Description*", placeholder="Detailed description of the incident", height=150)

        col1, col2 = st.columns(2)
        with col1:
            severity = st.selectbox("Severity Level*", ["Low", "Medium", "High", "Critical"])
        with col2:
            date_reported = st.date_input("Date Reported*", value=datetime.now())

        include_reporter = st.checkbox("Link this incident to my user account")

        submitted = st.form_submit_button("🚀 Create Incident", use_container_width=True, type="primary")

        if submitted:
            if not title or not description:
                st.error("⚠️ Please fill in all required fields (Title and Description)")
            else:
                reporter_id = st.session_state.user_id if include_reporter else None
                date_str = date_reported.strftime('%Y-%m-%d')

                incident_id = incidents.create_incident(
                    title=title,
                    description=description,
                    severity=severity,
                    date_reported=date_str,
                    reported_by=reporter_id
                )

                st.success(f"✅ Incident created successfully!")
                st.success(f"🆔 Incident ID: {incident_id}")
                st.balloons()
                st.cache_data.clear()
                st.info("💡 Switch to 'Manage Incidents' view to see your new incident")

st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'><small>🛡️ Cybersecurity Dashboard | User: {st.session_state.username} | Session Active 🟢</small></div>",
    unsafe_allow_html=True)