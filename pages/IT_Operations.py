import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px

# Add app directory to path
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

from data import tickets

st.set_page_config(page_title="IT Operations Dashboard", page_icon="🎫", layout="wide")

# Check authentication
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login first")
    st.switch_page("app.py")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"**Role:** {st.session_state.role}")
    st.markdown("---")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.session_state.logged_in = False
        st.switch_page("app.py")

# Header
st.title("🎫 IT Operations Dashboard")
st.markdown(f"**Ticket Management System** | User: {st.session_state.username}")
st.markdown("---")

# View selector
view_mode = st.radio(
    "Select View:",
    ["📈 Ticket Analytics", "📝 Manage Tickets", "➕ Create New Ticket"],
    horizontal=True
)


# Load tickets
@st.cache_data(ttl=60)
def load_tickets():
    rows = tickets.list_tickets()
    if not rows:
        return pd.DataFrame(columns=["id", "issue", "status", "priority", "opened_by"])
    return pd.DataFrame([dict(row) for row in rows])


df = load_tickets()

if view_mode == "📈 Ticket Analytics":
    if df.empty:
        st.warning("No tickets available. Create tickets to see analytics!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", len(df))
        with col2:
            open_count = len(df[df['status'] == 'Open'])
            st.metric("🔴 Open", open_count)
        with col3:
            in_progress = len(df[df['status'] == 'In Progress'])
            st.metric("🟡 In Progress", in_progress)
        with col4:
            resolved = len(df[df['status'] == 'Resolved'])
            st.metric("🟢 Resolved", resolved)

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            # Status distribution
            status_counts = df['status'].value_counts()
            fig_status = px.pie(values=status_counts.values, names=status_counts.index,
                                title='Tickets by Status')
            st.plotly_chart(fig_status, use_container_width=True)

        with col2:
            # Priority distribution
            priority_counts = df['priority'].value_counts()
            fig_priority = px.bar(x=priority_counts.index, y=priority_counts.values,
                                  title='Tickets by Priority',
                                  labels={'x': 'Priority', 'y': 'Count'})
            st.plotly_chart(fig_priority, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

elif view_mode == "📝 Manage Tickets":
    if df.empty:
        st.info("No tickets to manage. Create your first ticket!")
    else:
        search = st.text_input("🔍 Search tickets", placeholder="Search by issue...")

        if search:
            df_display = df[df['issue'].str.contains(search, case=False, na=False)]
        else:
            df_display = df

        st.markdown(f"**Showing {len(df_display)} tickets**")

        for idx, row in df_display.iterrows():
            status_emoji = {"Open": "🔴", "In Progress": "🟡", "Resolved": "🟢", "Closed": "⚪"}

            with st.expander(f"{status_emoji.get(row['status'], '⚪')} {row['issue']} - {row['priority']} Priority"):
                st.write(f"**Status:** {row['status']}")
                st.write(f"**Priority:** {row['priority']}")
                st.write(f"**Ticket ID:** {row['id']}")
                if row['opened_by']:
                    st.write(f"**Opened By:** User ID {row['opened_by']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Delete", key=f"del_tkt_{row['id']}"):
                        tickets.delete_ticket(row['id'])
                        st.success("Ticket deleted!")
                        st.cache_data.clear()
                        st.rerun()
                with col2:
                    if st.button("✏️ Edit", key=f"edit_tkt_{row['id']}"):
                        st.session_state[f"editing_tkt_{row['id']}"] = True

                # Edit form
                if st.session_state.get(f"editing_tkt_{row['id']}", False):
                    with st.form(f"edit_tkt_form_{row['id']}"):
                        new_issue = st.text_input("Issue", value=row['issue'])
                        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"],
                                                  index=["Open", "In Progress", "Resolved", "Closed"].index(
                                                      row['status']))
                        new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"],
                                                    index=["Low", "Medium", "High", "Critical"].index(row['priority']))

                        col_s, col_c = st.columns(2)
                        with col_s:
                            if st.form_submit_button("💾 Save"):
                                tickets.update_ticket(row['id'], issue=new_issue,
                                                      status=new_status, priority=new_priority)
                                st.session_state[f"editing_tkt_{row['id']}"] = False
                                st.success("Ticket updated!")
                                st.cache_data.clear()
                                st.rerun()
                        with col_c:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"editing_tkt_{row['id']}"] = False
                                st.rerun()

elif view_mode == "➕ Create New Ticket":
    with st.form("create_ticket_form", clear_on_submit=True):
        issue = st.text_input("Issue Description*")
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])

        link_user = st.checkbox("Link to my account")

        if st.form_submit_button("Create Ticket", type="primary"):
            if not issue:
                st.error("Please enter an issue description")
            else:
                opened_by = st.session_state.user_id if link_user else None
                ticket_id = tickets.create_ticket(issue, status, priority, opened_by)
                st.success(f"Ticket created! ID: {ticket_id}")
                st.cache_data.clear()
                st.balloons()

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'><small>🎫 IT Operations Dashboard</small></div>",
            unsafe_allow_html=True)