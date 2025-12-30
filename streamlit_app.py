import streamlit as st
import pandas as pd
from PIL import Image
import google.generativeai as genai
import os

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
if GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_API_KEY_HERE':
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

st.set_page_config(page_title="AI Waste Management System", page_icon="♻️", layout="wide")

st.title("♻️ AI-Powered Waste Management System - v2")
st.markdown("---")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Page", ["Dashboard", "AI Image Recognition", "Add Waste", "Statistics", "Guides"])

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

def classify_waste_from_image(image):
    """Use Gemini AI to classify waste from image"""
    if model is None:
        return None, "AI model not configured. Add GEMINI_API_KEY environment variable."
    
    try:
        # Send image to Gemini
        response = model.generate_content([
            "You are a waste classification expert. Analyze this image and identify:",
            "1. What type of waste is this? (Choose from: plastic, organic, reusable, hazardous, electronic, or mixed)",
            "2. Confidence level (0-100%)",
            "3. Items visible in the image",
            "\nRespond in this exact format:",
            "WASTE_TYPE: [type]",
            "CONFIDENCE: [percentage]",
            "ITEMS: [list of items]",
            image
        ])
        
        # Parse response
        response_text = response.text
        lines = response_text.strip().split('\n')
        
        result = {
            'waste_type': 'mixed',
            'confidence': 0,
            'items': []
        }
        
        for line in lines:
            if 'WASTE_TYPE:' in line:
                waste_type = line.split(':')[1].strip().lower()
                if waste_type in waste_types:
                    result['waste_type'] = waste_type
            elif 'CONFIDENCE:' in line:
                try:
                    conf = int(line.split(':')[1].strip().rstrip('%'))
                    result['confidence'] = conf
                except:
                    result['confidence'] = 50
            elif 'ITEMS:' in line:
                items_str = line.split(':')[1].strip()
                result['items'] = [item.strip() for item in items_str.split(',')]
        
        return result, None
    except Exception as e:
        return None, f"Error analyzing image: {str(e)}"

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
        st.info("No waste entries yet. Use AI Image Recognition or Add Waste!")

elif page == "AI Image Recognition":
    st.header("🧐 AI-Powered Waste Classification")
    
    if model is None:
        st.error("퉵7 AI model not configured. Please set GEMINI_API_KEY environment variable to enable image recognition.")
        st.info("퉵7 Get your free API key from: https://aistudio.google.com/apikey")
    else:
        st.success("✅ AI model ready for waste classification!")
    
    uploaded_file = st.file_uploader("Upload waste image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            with st.spinner("🤖 Analyzing waste image..."):
                result, error = classify_waste_from_image(image)
            
            if error:
                st.error(f"Error: {error}")
            else:
                st.subheader("📋 Analysis Results")
                
                waste_type = result['waste_type']
                confidence = result['confidence']
                items = result['items']
                
                # Display waste type
                st.markdown(f"### {waste_types[waste_type]['icon']} Detected: **{waste_type.title()}**")
                st.metric("Confidence Level", f"{confidence}%")
                
                # Items detected
                st.write("**Items Detected:**")
                for item in items:
                    st.write(f"  📄 {item}")
                
                # Add to log button
                if st.button("✅ Add to Log", key="ai_add"):
                    entry = {
                        'category': waste_type,
                        'quantity': 1.0,
                        'description': f"{', '.join(items)} (AI detected, {confidence}% confidence)",
                        'location': 'AI Recognized'
                    }
                    st.session_state.waste_log.append(entry)
                    st.session_state.stats[waste_type] += 1.0
                    st.success(f"✅ Added {waste_type} waste to log!")

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
st.markdown("<div style='text-align: center;'><p>♻️ AI Waste Management System | Help keep the environment clean!</p></div>", unsafe_allow_html=True)
