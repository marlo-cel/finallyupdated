import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add app directory to path
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

from data import tickets
from services.ai_helper import get_it_solution, chat_with_ai

st.set_page_config(page_title="IT Operations Dashboard", page_icon="🎫", layout="wide")

# Hide default menu
hide_streamlit_style = """
<style>
    [data-testid="stSidebarNav"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Check authentication
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please login first")
    st.switch_page("app.py")
    st.stop()

# Initialize chat history
if "it_chat_history" not in st.session_state:
    st.session_state.it_chat_history = []

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"**Role:** {st.session_state.role}")
    st.markdown("---")
    st.markdown("### Navigation")

    if st.button("⬅️ Return to Home", use_container_width=True, type="secondary"):
        st.session_state.current_page = "home"
        st.switch_page("app.py")

    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.role = None
        st.switch_page("app.py")

# Header
st.title("🎫 IT Operations Dashboard")
st.markdown(f"**Ticket Management System** | User: {st.session_state.username}")
st.markdown("---")

# View selector with AI
view_mode = st.radio(
    "Select View:",
    ["📈 Ticket Analytics", "📝 Manage Tickets", "➕ Create New Ticket", "🤖 AI IT Assistant"],
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

# ===============================
# AI IT ASSISTANT VIEW
# ===============================
if view_mode == "🤖 AI IT Assistant":

    st.subheader("🤖 AI-Powered IT Operations Assistant")
    st.info("💡 Get troubleshooting help, IT solutions, and operational guidance!")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Chat with IT AI")

        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.it_chat_history:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}")
                else:
                    st.markdown(f"**🤖 AI Assistant:** {msg['content']}")
                st.markdown("---")

        # Chat input
        with st.form("it_chat_form", clear_on_submit=True):
            user_message = st.text_area("Your Question:",
                                        placeholder="E.g., How do I troubleshoot network connectivity issues?",
                                        height=100)
            col_send, col_clear = st.columns([1, 1])

            with col_send:
                send_button = st.form_submit_button("💬 Send Message", use_container_width=True, type="primary")
            with col_clear:
                clear_button = st.form_submit_button("🗑️ Clear Chat", use_container_width=True)

            if send_button and user_message:
                with st.spinner("🤔 AI is thinking..."):
                    success, response = chat_with_ai(
                        user_message,
                        domain="it_operations",
                        conversation_history=st.session_state.it_chat_history[-4:] if len(
                            st.session_state.it_chat_history) > 0 else None
                    )

                    if success:
                        st.session_state.it_chat_history.append({"role": "user", "content": user_message})
                        st.session_state.it_chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    else:
                        st.error(f"❌ {response}")

            if clear_button:
                st.session_state.it_chat_history = []
                st.rerun()

    with col2:
        st.markdown("### Quick Actions")

        # Analyze ticket
        st.markdown("**🎫 Get Ticket Solution**")
        if not df.empty:
            open_tickets = df[df['status'] == 'Open']
            if not open_tickets.empty:
                ticket_options = {f"{row['issue']} ({row['priority']})": row for _, row in open_tickets.iterrows()}
                selected_ticket = st.selectbox("Select Open Ticket:", options=list(ticket_options.keys()))

                if st.button("🔍 Get AI Solution", use_container_width=True):
                    ticket = ticket_options[selected_ticket]

                    with st.spinner("Analyzing ticket..."):
                        success, solution = get_it_solution(ticket['issue'])

                        if success:
                            st.session_state.it_chat_history.append(
                                {"role": "user", "content": f"Help with ticket: {ticket['issue']}"})
                            st.session_state.it_chat_history.append({"role": "assistant", "content": solution})
                            st.rerun()
                        else:
                            st.error(f"❌ {solution}")
            else:
                st.info("No open tickets available")
        else:
            st.info("No tickets available")

        st.markdown("---")

        # Quick prompts
        st.markdown("**💡 Quick Prompts**")
        quick_prompts = [
            "How to reset a user password?",
            "Troubleshoot printer issues",
            "Network connectivity problems",
            "Software installation guide",
            "Email configuration help"
        ]

        for prompt in quick_prompts:
            if st.button(prompt, use_container_width=True, key=f"it_quick_{prompt}"):
                with st.spinner("Getting answer..."):
                    success, response = chat_with_ai(prompt, domain="it_operations")
                    if success:
                        st.session_state.it_chat_history.append({"role": "user", "content": prompt})
                        st.session_state.it_chat_history.append({"role": "assistant", "content": response})
                        st.rerun()

# ===============================
# ANALYTICS VIEW
# ===============================
elif view_mode == "📈 Ticket Analytics":

    if df.empty:
        st.warning("⚠️ No tickets available. Create tickets to see analytics!")
        st.stop()

    # Key Metrics
    st.subheader("📊 Key Performance Indicators")
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

    # Visualizations
    tab1, tab2, tab3 = st.tabs(["📊 Status Distribution", "🎯 Priority Analysis", "📋 Detailed View"])

    with tab1:
        st.subheader("Ticket Status Distribution")

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            status_counts = df['status'].value_counts()
            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='Tickets by Status',
                color=status_counts.index,
                color_discrete_map={
                    'Open': '#FF4444',
                    'In Progress': '#FFD700',
                    'Resolved': '#90EE90',
                    'Closed': '#CCCCCC'
                },
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title='Ticket Count by Status',
                labels={'x': 'Status', 'y': 'Count'},
                color=status_counts.index,
                color_discrete_map={
                    'Open': '#FF4444',
                    'In Progress': '#FFD700',
                    'Resolved': '#90EE90',
                    'Closed': '#CCCCCC'
                }
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("Priority Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Priority distribution
            priority_counts = df['priority'].value_counts()
            fig_priority = px.bar(
                x=priority_counts.index,
                y=priority_counts.values,
                title='Tickets by Priority Level',
                labels={'x': 'Priority', 'y': 'Count'},
                color=priority_counts.index,
                color_discrete_map={
                    'Low': '#90EE90',
                    'Medium': '#FFD700',
                    'High': '#FFA500',
                    'Critical': '#FF4500'
                }
            )
            st.plotly_chart(fig_priority, use_container_width=True)

        with col2:
            # Priority by status heatmap-style
            priority_status = df.groupby(['priority', 'status']).size().reset_index(name='count')
            fig_grouped = px.bar(
                priority_status,
                x='priority',
                y='count',
                color='status',
                title='Priority vs Status Breakdown',
                labels={'priority': 'Priority', 'count': 'Count'},
                color_discrete_map={
                    'Open': '#FF4444',
                    'In Progress': '#FFD700',
                    'Resolved': '#90EE90',
                    'Closed': '#CCCCCC'
                }
            )
            st.plotly_chart(fig_grouped, use_container_width=True)

    with tab3:
        st.subheader("Detailed Ticket Information")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "issue": st.column_config.TextColumn("Issue", width="large"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "priority": st.column_config.TextColumn("Priority", width="small"),
                "opened_by": st.column_config.NumberColumn("Opened By", width="small")
            }
        )

# ===============================
# MANAGE TICKETS VIEW
# ===============================
elif view_mode == "📝 Manage Tickets":

    st.subheader("Ticket Management")

    if df.empty:
        st.info("📋 No tickets to manage. Create your first ticket!")
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
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Priority:** {row['priority']}")
                    st.write(f"**Ticket ID:** {row['id']}")
                    if row['opened_by']:
                        st.write(f"**Opened By:** User ID {row['opened_by']}")

                with col2:
                    if st.button("🗑️ Delete", key=f"del_tkt_{row['id']}", use_container_width=True):
                        tickets.delete_ticket(row['id'])
                        st.success("Ticket deleted!")
                        st.cache_data.clear()
                        st.rerun()

                    if st.button("✏️ Edit", key=f"edit_tkt_{row['id']}", use_container_width=True):
                        st.session_state[f"editing_tkt_{row['id']}"] = True

                # Edit form
                if st.session_state.get(f"editing_tkt_{row['id']}", False):
                    st.markdown("---")
                    st.markdown("**✏️ Edit Ticket**")
                    with st.form(f"edit_tkt_form_{row['id']}"):
                        new_issue = st.text_input("Issue", value=row['issue'])
                        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"],
                                                  index=["Open", "In Progress", "Resolved", "Closed"].index(
                                                      row['status']))
                        new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"],
                                                    index=["Low", "Medium", "High", "Critical"].index(row['priority']))

                        col_s, col_c = st.columns(2)
                        with col_s:
                            if st.form_submit_button("💾 Save", use_container_width=True):
                                tickets.update_ticket(row['id'], issue=new_issue, status=new_status,
                                                      priority=new_priority)
                                st.session_state[f"editing_tkt_{row['id']}"] = False
                                st.success("Ticket updated!")
                                st.cache_data.clear()
                                st.rerun()
                        with col_c:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"editing_tkt_{row['id']}"] = False
                                st.rerun()

# ===============================
# CREATE TICKET VIEW
# ===============================
elif view_mode == "➕ Create New Ticket":

    st.subheader("Create New IT Ticket")

    with st.form("create_ticket_form", clear_on_submit=True):
        issue = st.text_input("Issue Description*", placeholder="Describe the IT issue")

        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])

        link_user = st.checkbox("Link to my account", value=True)

        submitted = st.form_submit_button("🚀 Create Ticket", use_container_width=True, type="primary")

        if submitted:
            if not issue:
                st.error("⚠️ Please enter an issue description")
            else:
                opened_by = st.session_state.user_id if link_user else None
                ticket_id = tickets.create_ticket(issue, status, priority, opened_by)
                st.success(f"✅ Ticket created! ID: {ticket_id}")
                st.balloons()
                st.cache_data.clear()
                st.info("💡 Switch to 'Manage Tickets' to view your new ticket")

st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'><small>🎫 IT Operations Dashboard | User: {st.session_state.username} | Session Active 🟢</small></div>",
    unsafe_allow_html=True)