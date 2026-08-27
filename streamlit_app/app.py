import sklearn  # Pre-initialize scikit-learn & scipy early to save RAM
import os
import joblib
import pandas as pd
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="C&W Infrastructure Cost Predictor",
    page_icon="cw logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MODEL & ENCODER LOADING
# ==========================================
@st.cache_resource
def load_ml_assets():
    # Get the directory where app.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    model_path = os.path.join(base_dir, 'Model', 'C&W_model.pkl')
    encoder_path = os.path.join(base_dir, 'Model', 'C&W_encoder.pkl')
    
    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    
    return model, encoder
    
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        st.error(f"⚠️ Missing Model files! Ensure `C&W_model.pkl` and `C&W_encoder.pkl` exist in the `./Model/` folder.")
        st.stop()
        
    # Using read-only memory mapping to prevent MemoryError
    model = joblib.load(model_path, mmap_mode='r')
    encoder = joblib.load(encoder_path)
    return model, encoder

# Explicitly load assets into memory
model, encoder = load_ml_assets()

# Extract categorical dropdowns directly from the fitted encoder
cat_cols = ["District", "Tehsil/Town", "Building_Type", "Structure_Type", "Foundation_Type"]
categories_dict = {
    col: list(categories) for col, categories in zip(cat_cols, encoder.categories_)
}

# ==========================================
# HEADER SECTION
# ==========================================
# Create 3 columns with a 1:2:1 width ratio
left_col, center_col, right_col = st.columns([7,3,6])

with center_col:
    # Set width (e.g., 100 or 120) to shrink the image size
    st.image("cw logo.jpg", width=110)
st.title("C&W Cost Estimation Engine",text_alignment="center")
st.caption("Predictive Infrastructure Budgeting Powered by Machine Learning (R² = 0.62)")
st.divider()

# ==========================================
# INPUT FORM LAYOUT
# ==========================================
col_left, col_right = st.columns([7, 5], gap="large")

with col_left:
    st.subheader("📋 Project Specifications")
    
    st.markdown("##### 📍 Location & Classification")
    c1, c2 = st.columns(2)
    with c1:
        district = st.selectbox("District", options=categories_dict["District"])
        building_type = st.selectbox("Building Type", options=categories_dict["Building_Type"])
    with c2:
        tehsil = st.selectbox("Tehsil / Town", options=categories_dict["Tehsil/Town"])
        cleaned_year = st.number_input("Sanction Year", min_value=2010, max_value=2030, value=2024, step=1)

    st.markdown("---")
    st.markdown("##### 🧱 Structural Engineering Parameters")
    c3, c4 = st.columns(2)
    with c3:
        structure_type = st.selectbox("Structure Type", options=categories_dict["Structure_Type"])
        floors = st.number_input("Number of Floors", min_value=1, max_value=20, value=4, step=1)
    with c4:
        foundation_type = st.selectbox("Foundation Type", options=categories_dict["Foundation_Type"])
        cost_sqft = st.number_input("Cost-per-Sqft (PKR)", min_value=500, max_value=15000, value=3500, step=250)

# ==========================================
# PREDICTION & RESULTS PANEL
# ==========================================
with col_right:
    st.subheader("📊 Expenditure Forecast")
    
    # 1. Assemble Input Data
    input_data = pd.DataFrame({
        'District': [district],
        'Tehsil/Town': [tehsil],
        'Building_Type': [building_type],
        'Structure_Type': [structure_type],
        'Foundation_Type': [foundation_type],
        'No._of_Floors': [floors],
        'Cost-per-Sqft': [cost_sqft],
        'Cleaned_Year': [cleaned_year]
    })
    
    # Predict button
    if st.button("🚀 Calculate Estimated Cost", type="primary", use_container_width=True):
        try:
            # 2. Transform categorical features
            encoded_cats = encoder.transform(input_data[cat_cols])
            encoded_cat_df = pd.DataFrame(
                encoded_cats,
                columns=encoder.get_feature_names_out(cat_cols)
            )
            
            # 3. Assemble full 23-feature matrix X_new
            num_cols = ["No._of_Floors", "Cost-per-Sqft", "Cleaned_Year"]
            X_new = pd.concat([input_data[num_cols], encoded_cat_df], axis=1)
            
            # 4. Generate prediction
            predicted_cost = model.predict(X_new)[0]
            
            # 5. Display Metric Box
            st.success("Cost Calculated Successfully!")
            st.metric(
                label="Predicted Total Infrastructure Cost",
                value=f"Rs. {predicted_cost:.2f} Million",
                delta="± Rs. 15.28M (MAE)"
            )
            
            # Matrix Breakdown
            with st.expander("🔍 View Feature Matrix Details", expanded=True):
                st.write("**Inputs Processed:**")
                st.json({
                    "Location": f"{tehsil}, {district}",
                    "Scope": f"{building_type} ({floors} Floors)",
                    "Engineering": f"{structure_type} | {foundation_type}",
                    "Unit Rate": f"Rs. {cost_sqft:,} / sqft",
                    "Sanction Year": cleaned_year,
                    "Total Features (X)": X_new.shape[1]
                })

        except Exception as e:
            st.error(f"Prediction Error: {e}")

    else:
        st.info("💡 Adjust parameters on the left and click **'Calculate Estimated Cost'** to run the prediction.")

# Footer
st.divider()
st.caption("C&W Infrastructure Cost Intelligence • Powered by Scikit-Learn Random Forest Architecture")