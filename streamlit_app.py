import streamlit as st
import pandas as pd

st.set_page_config(page_title="Waste Management System", page_icon="♻️", layout="wide")

st.title("♻️ Waste Management System")
st.markdown("---")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Page", ["Dashboard", "Add Waste", "Statistics", "Guides"])

# Waste categories
waste_types = {
    'plastic': {'icon': '🥤', 'color': '#FF6B6B'},
    'organic': {'icon': '🍎', 'color': '#51CF66'},
    'reusable': {'icon': '♻️', 'color': '#4ECDC4'},
    'hazardous': {'icon': '⚠️', 'color': '#FFD93D'},
    'electronic': {'icon': '📱', 'color': '#6C5CE7'},
    'mixed': {'icon': '🗑️', 'color': '#A29BFE'}
}

# Initialize session state
if 'waste_log' not in st.session_state:
    st.session_state.waste_log = []
if 'stats' not in st.session_state:
    st.session_state.stats = {k: 0 for k in waste_types.keys()}

# Pages
if page == "Dashboard":
    st.header("Waste Management Dashboard")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    metrics = [
        (col1, "🥤 Plastic", st.session_state.stats['plastic']),
        (col2, "🍎 Organic", st.session_state.stats['organic']),
        (col3, "♻️ Reusable", st.session_state.stats['reusable']),
        (col4, "⚠️ Hazardous", st.session_state.stats['hazardous']),
        (col5, "📱 Electronic", st.session_state.stats['electronic']),
        (col6, "🗑️ Mixed", st.session_state.stats['mixed'])
    ]
    
    for col, label, value in metrics:
        with col:
            st.metric(label, f"{value:.1f} kg")
    
    st.markdown("---")
    
    if len(st.session_state.waste_log) > 0:
        st.subheader("Recent Waste Entries")
        df = pd.DataFrame(st.session_state.waste_log)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No waste entries yet. Add waste from the 'Add Waste' page!")

elif page == "Add Waste":
    st.header("Add Waste Item")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        waste_type = st.selectbox("Select Waste Category", list(waste_types.keys()))
    
    with col2:
        quantity = st.number_input("Quantity (kg)", min_value=0.1, value=1.0)
    
    description = st.text_area("Description")
    location = st.text_input("Location/Area")
    
    if st.button("➕ Add to Log"):
        entry = {
            'category': waste_type,
            'quantity': quantity,
            'description': description,
            'location': location
        }
        st.session_state.waste_log.append(entry)
        st.session_state.stats[waste_type] += quantity
        st.success(f"✅ Added {quantity}kg of {waste_type}!")

elif page == "Statistics":
    st.header("Waste Statistics")
    
    if len(st.session_state.waste_log) == 0:
        st.warning("No data available yet.")
    else:
        total = sum(st.session_state.stats.values())
        st.metric("Total Waste Managed", f"{total:.1f} kg")
        
        # Chart
        chart_data = pd.DataFrame({
            'Type': list(st.session_state.stats.keys()),
            'Amount': list(st.session_state.stats.values())
        })
        chart_data = chart_data[chart_data['Amount'] > 0]
        
        if len(chart_data) > 0:
            st.bar_chart(chart_data.set_index('Type'))

elif page == "Guides":
    st.header("Waste Classification Guide")
    
    for waste_type, info in waste_types.items():
        with st.expander(f"{info['icon']} {waste_type.title()}"):
            st.write(f"**Icon**: {info['icon']}")
            st.write(f"**Color**: {info['color']}")
            if waste_type == 'plastic':
                st.info("Plastic items should be recycled in designated bins.")
            elif waste_type == 'organic':
                st.info("Organic waste can be composted.")
            elif waste_type == 'reusable':
                st.info("These items can be donated or reused.")
            elif waste_type == 'hazardous':
                st.warning("Handle with care. Requires special disposal.")
            elif waste_type == 'electronic':
                st.info("E-waste contains valuable materials and should be recycled.")
            else:
                st.info("Mixed waste should be sent to landfill.")

st.markdown("---")
st.markdown("<div style='text-align: center;'><p>♻️ Waste Management System | Help keep the environment clean!</p></div>", unsafe_allow_html=True)
