import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Waste Management System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.waste-category {
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    color: white;
    font-size: 18px;
    font-weight: bold;
}
.plastic { background-color: #FF6B6B; }
.organic { background-color: #51CF66; }
.reusable { background-color: #4ECDC4; }
.hazardous { background-color: #FFD93D; color: black; }
.electronic { background-color: #6C5CE7; }
.mixed { background-color: #A29BFE; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'waste_log' not in st.session_state:
    st.session_state.waste_log = []
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'plastic': 0,
        'organic': 0,
        'reusable': 0,
        'hazardous': 0,
        'electronic': 0,
        'mixed': 0
    }

# Header
st.title("♻️ Waste Management System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Options")
    page = st.radio("Select Page", ["Add Waste", "View Statistics", "Waste Guide", "Reports"])

# Waste categories with details
WASTE_CATEGORIES = {
    'plastic': {
        'icon': '🥤',
        'color': '#FF6B6B',
        'examples': ['Bottles', 'Bags', 'Containers', 'Straws', 'Packaging'],
        'disposal': 'Recycle in plastic bins. Separate by type if possible.'
    },
    'organic': {
        'icon': '🍎',
        'color': '#51CF66',
        'examples': ['Food scraps', 'Leaves', 'Paper', 'Cardboard', 'Plant waste'],
        'disposal': 'Compost or send to organic waste facility. Can be biodegraded.'
    },
    'reusable': {
        'icon': '♻️',
        'color': '#4ECDC4',
        'examples': ['Clothes', 'Books', 'Furniture', 'Electronics (working)', 'Containers'],
        'disposal': 'Donate to charities or reuse. Reduce environmental impact.'
    },
    'hazardous': {
        'icon': '⚠️',
        'color': '#FFD93D',
        'examples': ['Batteries', 'Paint', 'Chemicals', 'Oils', 'Expired medicines'],
        'disposal': 'Send to hazardous waste facility. Handle with care!'
    },
    'electronic': {
        'icon': '📱',
        'color': '#6C5CE7',
        'examples': ['Old phones', 'Computers', 'Cables', 'Chargers', 'Broken appliances'],
        'disposal': 'E-waste recycling center. Contains valuable materials.'
    },
    'mixed': {
        'icon': '🗑️',
        'color': '#A29BFE',
        'examples': ['Mixed waste', 'Unclassified items', 'General garbage'],
        'disposal': 'Send to landfill or waste management facility.'
    }
}

# PAGE: Add Waste
if page == "Add Waste":
    st.header("Add Waste Item")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        waste_type = st.selectbox(
            "Select Waste Category",
            list(WASTE_CATEGORIES.keys()),
            format_func=lambda x: f"{WASTE_CATEGORIES[x]['icon']} {x.title()}"
        )
    
    with col2:
        quantity = st.number_input("Quantity (kg)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)
    
    description = st.text_area("Item Description")
    location = st.text_input("Location/Area")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        add_button = st.button("➕ Add to Log", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear Form", use_container_width=True)
    
    if add_button:
        waste_item = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'category': waste_type,
            'quantity': quantity,
            'description': description,
            'location': location
        }
        st.session_state.waste_log.append(waste_item)
        st.session_state.stats[waste_type] += quantity
        st.success(f"✅ Added {quantity}kg of {waste_type}!")
        st.balloons()
    
    if clear_button:
        st.rerun()
    
    # Display category info
    st.markdown("---")
    st.subheader(f"{WASTE_CATEGORIES[waste_type]['icon']} {waste_type.title()} Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Common Examples:**")
        for example in WASTE_CATEGORIES[waste_type]['examples']:
            st.write(f"• {example}")
    with col2:
        st.write("**Disposal Method:**")
        st.info(WASTE_CATEGORIES[waste_type]['disposal'])

# PAGE: View Statistics
elif page == "View Statistics":
    st.header("Waste Statistics")
    
    if len(st.session_state.waste_log) == 0:
        st.info("No waste data yet. Add some waste items to see statistics!")
    else:
        # Summary metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("🥤 Plastic", f"{st.session_state.stats['plastic']:.1f} kg")
        with col2:
            st.metric("🍎 Organic", f"{st.session_state.stats['organic']:.1f} kg")
        with col3:
            st.metric("♻️ Reusable", f"{st.session_state.stats['reusable']:.1f} kg")
        with col4:
            st.metric("⚠️ Hazardous", f"{st.session_state.stats['hazardous']:.1f} kg")
        with col5:
            st.metric("📱 Electronic", f"{st.session_state.stats['electronic']:.1f} kg")
        with col6:
            st.metric("🗑️ Mixed", f"{st.session_state.stats['mixed']:.1f} kg")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            chart_data = pd.DataFrame({
                'Category': list(st.session_state.stats.keys()),
                'Quantity': list(st.session_state.stats.values())
            })
            chart_data = chart_data[chart_data['Quantity'] > 0]
            st.subheader("Waste Distribution")
            st.bar_chart(chart_data.set_index('Category'))
        
        with col2:
            st.subheader("Waste Breakdown")
            fig_data = chart_data.copy()
            st.write(fig_data.to_string(index=False))
            total = fig_data['Quantity'].sum()
            st.metric("Total Waste", f"{total:.1f} kg")
        
        st.markdown("---")
        st.subheader("Waste Log")
        if st.session_state.waste_log:
            log_df = pd.DataFrame(st.session_state.waste_log)
            st.dataframe(log_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export as CSV"):
                    csv = log_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="waste_log.csv",
                        mime="text/csv"
                    )

# PAGE: Waste Guide
elif page == "Waste Guide":
    st.header("Waste Classification Guide")
    
    for category, info in WASTE_CATEGORIES.items():
        with st.expander(f"{info['icon']} {category.title()}", expanded=(category == 'plastic')):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Examples:**")
                for example in info['examples']:
                    st.write(f"• {example}")
            with col2:
                st.write("**Disposal Method:**")
                st.info(info['disposal'])
                
                if category == 'plastic':
                    st.warning("♻️ Plastic takes 500+ years to decompose!")
                elif category == 'hazardous':
                    st.warning("⚠️ Hazardous waste requires special handling!")
                elif category == 'electronic':
                    st.info("💰 Electronic waste contains valuable metals!")

# PAGE: Reports
elif page == "Reports":
    st.header("Waste Management Reports")
    
    if len(st.session_state.waste_log) == 0:
        st.info("No data available for reports yet.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Summary Report")
            total_waste = sum(st.session_state.stats.values())
            st.metric("Total Waste Managed", f"{total_waste:.1f} kg")
            st.metric("Number of Entries", len(st.session_state.waste_log))
            
            # Most common waste type
            if st.session_state.stats:
                most_common = max(st.session_state.stats, key=st.session_state.stats.get)
                st.metric("Most Common Type", f"{most_common.title()}")
        
        with col2:
            st.subheader("Environmental Impact")
            if st.session_state.stats['organic'] > 0:
                st.success(f"♻️ {st.session_state.stats['organic']:.1f}kg organic waste can be composted!")
            if st.session_state.stats['reusable'] > 0:
                st.success(f"♻️ {st.session_state.stats['reusable']:.1f}kg reusable items donated!")
            if st.session_state.stats['hazardous'] > 0:
                st.warning(f"⚠️ {st.session_state.stats['hazardous']:.1f}kg hazardous waste needs special care!")
        
        st.markdown("---")
        st.subheader("Category-wise Analysis")
        
        analysis_data = []
        for category, amount in st.session_state.stats.items():
            if amount > 0:
                percentage = (amount / total_waste) * 100
                analysis_data.append({
                    'Category': category.title(),
                    'Amount (kg)': f"{amount:.1f}",
                    'Percentage': f"{percentage:.1f}%"
                })
        
        if analysis_data:
            analysis_df = pd.DataFrame(analysis_data)
            st.dataframe(analysis_df, use_container_width=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
<p>♻️ Waste Management System v1.0</p>
<p>Help us keep the environment clean! Proper waste segregation saves our planet.</p>
</div>
""", unsafe_allow_html=True)
