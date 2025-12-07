import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add app directory to path
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

from data import datasets
from services.ai_helper import get_data_insights, chat_with_ai

st.set_page_config(page_title="Data Science Dashboard", page_icon="📊", layout="wide")

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
    st.error("🔒 Please login first to access this dashboard")
    st.info("Redirecting to login page...")
    st.switch_page("app.py")
    st.stop()

# Initialize chat history
if "ds_chat_history" not in st.session_state:
    st.session_state.ds_chat_history = []

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
st.title("📊 Data Science Dashboard")
st.markdown(f"**Dataset Management & Analytics** | User: {st.session_state.username}")
st.markdown("---")

# View selector with AI
view_mode = st.radio(
    "Select View:",
    ["📈 Dataset Analytics", "📝 Manage Datasets", "➕ Add New Dataset", "🤖 AI Data Assistant"],
    horizontal=True
)


# Load datasets
@st.cache_data(ttl=60)
def load_datasets():
    rows = datasets.list_datasets()
    if not rows:
        return pd.DataFrame(columns=["id", "name", "description", "rows", "owner"])
    return pd.DataFrame([dict(row) for row in rows])


df = load_datasets()

# ===============================
# AI DATA ASSISTANT VIEW
# ===============================
if view_mode == "🤖 AI Data Assistant":

    st.subheader("🤖 AI-Powered Data Science Assistant")
    st.info("💡 Ask about data analysis, visualizations, statistical concepts, or get dataset insights!")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Chat with Data Science AI")

        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.ds_chat_history:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}")
                else:
                    st.markdown(f"**🤖 AI Assistant:** {msg['content']}")
                st.markdown("---")

        # Chat input
        with st.form("ds_chat_form", clear_on_submit=True):
            user_message = st.text_area("Your Question:",
                                        placeholder="E.g., What's the best visualization for time series data?",
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
                        domain="data_science",
                        conversation_history=st.session_state.ds_chat_history[-4:] if len(
                            st.session_state.ds_chat_history) > 0 else None
                    )

                    if success:
                        st.session_state.ds_chat_history.append({"role": "user", "content": user_message})
                        st.session_state.ds_chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    else:
                        st.error(f"❌ {response}")

            if clear_button:
                st.session_state.ds_chat_history = []
                st.rerun()

    with col2:
        st.markdown("### Quick Actions")

        # Analyze dataset
        st.markdown("**📊 Get Dataset Insights**")
        if not df.empty:
            dataset_options = {f"{row['name']} ({row['rows']} rows)": row for _, row in df.iterrows()}
            selected_dataset = st.selectbox("Select Dataset:", options=list(dataset_options.keys()))

            if st.button("🔍 Get AI Insights", use_container_width=True):
                dataset = dataset_options[selected_dataset]
                dataset_info = f"Dataset: {dataset['name']}\nRows: {dataset['rows']}\nDescription: {dataset['description']}"

                with st.spinner("Analyzing dataset..."):
                    success, insights = get_data_insights(dataset_info)

                    if success:
                        st.session_state.ds_chat_history.append(
                            {"role": "user", "content": f"Analyze dataset: {dataset['name']}"})
                        st.session_state.ds_chat_history.append({"role": "assistant", "content": insights})
                        st.rerun()
                    else:
                        st.error(f"❌ {insights}")
        else:
            st.info("No datasets available for analysis")

        st.markdown("---")

        # Quick prompts
        st.markdown("**💡 Quick Prompts**")
        quick_prompts = [
            "Explain linear regression simply",
            "Best practices for data cleaning",
            "How to handle missing data?",
            "Difference between mean and median",
            "What is feature engineering?"
        ]

        for prompt in quick_prompts:
            if st.button(prompt, use_container_width=True, key=f"ds_quick_{prompt}"):
                with st.spinner("Getting answer..."):
                    success, response = chat_with_ai(prompt, domain="data_science")
                    if success:
                        st.session_state.ds_chat_history.append({"role": "user", "content": prompt})
                        st.session_state.ds_chat_history.append({"role": "assistant", "content": response})
                        st.rerun()

# ===============================
# ANALYTICS VIEW
# ===============================
elif view_mode == "📈 Dataset Analytics":

    if df.empty:
        st.warning("⚠️ No datasets available. Add datasets to see analytics!")
        st.stop()

    # Key Metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Datasets", len(df))
    with col2:
        st.metric("Total Rows", f"{df['rows'].sum():,}")
    with col3:
        st.metric("Avg Rows/Dataset", f"{df['rows'].mean():.0f}")
    with col4:
        st.metric("Largest Dataset", f"{df['rows'].max():,}")

    st.markdown("---")

    # Visualizations in tabs
    tab1, tab2, tab3 = st.tabs(["📊 Size Comparison", "📈 Distribution Analysis", "📋 Detailed View"])

    with tab1:
        st.subheader("Dataset Size Comparison")

        # Bar chart
        fig_bar = px.bar(
            df,
            x='name',
            y='rows',
            title='Number of Rows per Dataset',
            labels={'name': 'Dataset Name', 'rows': 'Number of Rows'},
            color='rows',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Horizontal bar for better readability
        fig_h_bar = px.bar(
            df.sort_values('rows', ascending=True),
            y='name',
            x='rows',
            orientation='h',
            title='Dataset Size Ranking (Horizontal)',
            labels={'name': 'Dataset Name', 'rows': 'Number of Rows'},
            color='rows',
            color_continuous_scale='Viridis'
        )
        fig_h_bar.update_layout(height=400)
        st.plotly_chart(fig_h_bar, use_container_width=True)

    with tab2:
        st.subheader("Distribution Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            fig_pie = px.pie(
                df,
                values='rows',
                names='name',
                title='Dataset Size Distribution',
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Treemap
            fig_tree = px.treemap(
                df,
                path=['name'],
                values='rows',
                title='Dataset Size Treemap',
                color='rows',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_tree, use_container_width=True)

        # Statistics
        st.markdown("### Statistical Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Min Rows", f"{df['rows'].min():,}")
        with col2:
            st.metric("Max Rows", f"{df['rows'].max():,}")
        with col3:
            st.metric("Median Rows", f"{df['rows'].median():.0f}")
        with col4:
            st.metric("Std Dev", f"{df['rows'].std():.0f}")

    with tab3:
        st.subheader("Detailed Dataset Information")

        display_df = df.copy()
        display_df['rows'] = display_df['rows'].apply(lambda x: f"{x:,}")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Dataset Name", width="medium"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "rows": st.column_config.TextColumn("Rows", width="small"),
                "owner": st.column_config.NumberColumn("Owner ID", width="small")
            }
        )

# ===============================
# MANAGE DATASETS VIEW
# ===============================
elif view_mode == "📝 Manage Datasets":

    st.subheader("Dataset Management")

    if df.empty:
        st.info("📋 No datasets to manage. Add your first dataset using the 'Add New Dataset' view.")
    else:
        search_term = st.text_input("🔍 Search datasets", placeholder="Search by name or description...")

        if search_term:
            df_display = df[
                df['name'].str.contains(search_term, case=False, na=False) |
                df['description'].fillna('').str.contains(search_term, case=False, na=False)
                ]
        else:
            df_display = df

        st.markdown(f"**Showing {len(df_display)} datasets**")

        for idx, row in df_display.iterrows():
            with st.expander(f"📁 **{row['name']}** ({row['rows']:,} rows)"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Description:** {row['description'] if row['description'] else 'No description'}")
                    st.write(f"**Number of Rows:** {row['rows']:,}")
                    st.write(f"**Dataset ID:** {row['id']}")
                    st.write(f"**Owner:** User ID {row['owner']}" if row['owner'] else "**Owner:** Not assigned")

                with col2:
                    if st.button("🗑️ Delete", key=f"del_ds_{row['id']}", use_container_width=True):
                        datasets.delete_dataset(row['id'])
                        st.success("✅ Dataset deleted!")
                        st.cache_data.clear()
                        st.rerun()

                    if st.button("✏️ Edit", key=f"edit_ds_{row['id']}", use_container_width=True):
                        st.session_state[f"editing_ds_{row['id']}"] = True

                if st.session_state.get(f"editing_ds_{row['id']}", False):
                    st.markdown("---")
                    st.markdown("**✏️ Edit Dataset**")
                    with st.form(f"edit_ds_form_{row['id']}"):
                        new_name = st.text_input("Name", value=row['name'])
                        new_desc = st.text_area("Description", value=row['description'] if row['description'] else "")
                        new_rows = st.number_input("Number of Rows", min_value=0, value=int(row['rows']))

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Save", use_container_width=True):
                                datasets.update_dataset(row['id'], name=new_name, description=new_desc, rows=new_rows)
                                st.session_state[f"editing_ds_{row['id']}"] = False
                                st.success("✅ Dataset updated!")
                                st.cache_data.clear()
                                st.rerun()
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"editing_ds_{row['id']}"] = False
                                st.rerun()

# ===============================
# ADD DATASET VIEW
# ===============================
elif view_mode == "➕ Add New Dataset":

    st.subheader("Add New Dataset")

    with st.form("add_dataset_form", clear_on_submit=True):
        name = st.text_input("Dataset Name*", placeholder="Enter dataset name")
        description = st.text_area("Description", placeholder="Brief description of the dataset", height=100)

        col1, col2 = st.columns(2)
        with col1:
            rows = st.number_input("Number of Rows*", min_value=0, value=0, step=1)
        with col2:
            link_owner = st.checkbox("Link to my user account", value=True)

        st.info("💡 **Tip:** Add accurate row counts to help with dataset size analytics")

        submitted = st.form_submit_button("🚀 Add Dataset", use_container_width=True, type="primary")

        if submitted:
            if not name:
                st.error("⚠️ Please enter a dataset name")
            else:
                owner_id = st.session_state.user_id if link_owner else None
                dataset_id = datasets.add_dataset(name, description, rows, owner_id)

                st.success(f"✅ Dataset '{name}' added successfully!")
                st.success(f"🆔 Dataset ID: {dataset_id}")
                st.balloons()
                st.cache_data.clear()
                st.info("💡 Switch to 'Dataset Analytics' to see visualizations")

st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'><small>📊 Data Science Dashboard | User: {st.session_state.username} | Session Active 🟢</small></div>",
    unsafe_allow_html=True)