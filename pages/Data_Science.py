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

st.set_page_config(page_title="Data Science Dashboard", page_icon="📊", layout="wide")

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

# Header
st.title("📊 Data Science Dashboard")
st.markdown(f"**Dataset Management & Analytics** | User: {st.session_state.username}")
st.markdown("---")

# View selector
view_mode = st.radio(
    "Select View:",
    ["📈 Dataset Analytics", "📝 Manage Datasets", "➕ Add New Dataset"],
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
# ANALYTICS VIEW
# ===============================
if view_mode == "📈 Dataset Analytics":

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

        # Horizontal bar for better readability with many datasets
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
            # Pie chart showing proportion of total rows
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
            # Treemap visualization
            fig_tree = px.treemap(
                df,
                path=['name'],
                values='rows',
                title='Dataset Size Treemap',
                color='rows',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_tree, use_container_width=True)

        # Statistics summary
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

        # Enhanced dataframe with formatting
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

        # Summary table
        st.markdown("### Quick Summary")
        summary_data = {
            'Metric': ['Total Datasets', 'Total Rows', 'Average Size', 'Largest Dataset', 'Smallest Dataset'],
            'Value': [
                len(df),
                f"{df['rows'].sum():,}",
                f"{df['rows'].mean():.0f}",
                f"{df['rows'].max():,} ({df.loc[df['rows'].idxmax(), 'name']})",
                f"{df['rows'].min():,} ({df.loc[df['rows'].idxmin(), 'name']})"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ===============================
# MANAGE DATASETS VIEW
# ===============================
elif view_mode == "📝 Manage Datasets":

    st.subheader("Dataset Management")

    if df.empty:
        st.info("📋 No datasets to manage. Add your first dataset using the 'Add New Dataset' view.")
    else:
        # Search functionality
        search_term = st.text_input("🔍 Search datasets", placeholder="Search by name or description...")

        if search_term:
            df_display = df[
                df['name'].str.contains(search_term, case=False, na=False) |
                df['description'].fillna('').str.contains(search_term, case=False, na=False)
                ]
        else:
            df_display = df

        st.markdown(f"**Showing {len(df_display)} datasets**")

        # Display datasets
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

                # Edit form
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
                                datasets.update_dataset(
                                    row['id'],
                                    name=new_name,
                                    description=new_desc,
                                    rows=new_rows
                                )
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
                st.info("💡 Switch to 'Dataset Analytics' to see visualizations or 'Manage Datasets' to view details")

st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'><small>📊 Data Science Dashboard | User: {st.session_state.username} | Session Active 🟢</small></div>",
    unsafe_allow_html=True)