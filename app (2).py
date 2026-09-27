import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="Nassau Candy Shipping Dashboard",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Factory-to-Customer Shipping Route Efficiency Dashboard")
st.caption("Nassau Candy Distributor Logistics & Route Optimization Platform")

# Data Loader
@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    
    factory_map = {
        "Wonka Bar - Nutty Crunch Surprise": ("Lot's O' Nuts", 32.881893, -111.768036),
        "Wonka Bar - Fudge Mallows": ("Lot's O' Nuts", 32.881893, -111.768036),
        "Wonka Bar -Scrumdiddlyumptious": ("Lot's O' Nuts", 32.881893, -111.768036),
        "Wonka Bar - Milk Chocolate": ("Wicked Choccy's", 32.076176, -81.088371),
        "Wonka Bar - Triple Dazzle Caramel": ("Wicked Choccy's", 32.076176, -81.088371),
        "Laffy Taffy": ("Sugar Shack", 48.119140, -96.181150),
        "SweeTARTS": ("Sugar Shack", 48.119140, -96.181150),
        "Nerds": ("Sugar Shack", 48.119140, -96.181150),
        "Fun Dip": ("Sugar Shack", 48.119140, -96.181150),
        "Fizzy Lifting Drinks": ("Sugar Shack", 48.119140, -96.181150),
        "Everlasting Gobstopper": ("Secret Factory", 41.446333, -90.565487),
        "Lickable Wallpaper": ("Secret Factory", 41.446333, -90.565487),
        "Wonka Gum": ("Secret Factory", 41.446333, -90.565487),
        "Hair Toffee": ("The Other Factory", 35.117500, -89.971107),
        "Kazookles": ("The Other Factory", 35.117500, -89.971107)
    }
    
    df['Factory'] = df['Product Name'].map(lambda x: factory_map.get(str(x).strip(), ("Unknown", 0.0, 0.0))[0])
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y', errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d-%m-%Y', errors='coerce')
    df['Shipping Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    df['Route'] = df['Factory'] + " ➔ " + df['State/Province']
    return df

try:
    df = load_data()

    # Sidebar Filters (Badha 4 Requirements Mujab)
    st.sidebar.header("⚙️ User Capabilities & Filters")
    
    # 1. Date Range Filter
    min_date, max_date = df['Order Date'].min().date(), df['Order Date'].max().date()
    selected_dates = st.sidebar.date_input("1. Date Range Filter", [min_date, max_date])
    
    # 2. Region & State Selector
    all_regions = df['Region'].dropna().unique().tolist()
    selected_regions = st.sidebar.multiselect("2. Region Selector", options=all_regions, default=all_regions)
    
    all_states = df[df['Region'].isin(selected_regions)]['State/Province'].dropna().unique().tolist()
    selected_states = st.sidebar.multiselect("   State Selector", options=all_states, default=all_states)
    
    # 3. Ship Mode Filter
    all_modes = df['Ship Mode'].dropna().unique().tolist()
    selected_modes = st.sidebar.multiselect("3. Ship Mode Filter", options=all_modes, default=all_modes)
    
    # 4. Lead-Time Threshold Slider
    min_lt, max_lt = int(df['Shipping Lead Time'].min()), int(df['Shipping Lead Time'].max())
    lt_threshold = st.sidebar.slider("4. Lead-Time Threshold (Days)", min_value=min_lt, max_value=max_lt, value=1300)

    # Filter Applications
    filtered = df[
        (df['Order Date'].dt.date >= selected_dates[0]) &
        (df['Order Date'].dt.date <= selected_dates[1]) &
        (df['Region'].isin(selected_regions)) &
        (df['State/Province'].isin(selected_states)) &
        (df['Ship Mode'].isin(selected_modes))
    ]

    # Metrics Display
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Orders", f"{len(filtered):,}")
    c2.metric("⏱️ Avg Lead Time", f"{filtered['Shipping Lead Time'].mean():.1f} Days")
    delay_rate = (filtered['Shipping Lead Time'] > lt_threshold).mean() * 100
    c3.metric("⚠️ Exceeding Threshold", f"{delay_rate:.1f}%")
    c4.metric("💰 Total Sales", f"${filtered['Sales'].sum():,.2f}")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Route Leaderboard", 
        "🗺️ US State Map", 
        "🚚 Ship Mode Analysis", 
        "🔍 Data Inspector"
    ])

    with tab1:
        st.subheader("Route Efficiency Breakdown")
        route_agg = filtered.groupby('Route')['Shipping Lead Time'].mean().reset_index()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Top 10 Fastest Routes**")
            fast_fig = px.bar(
                route_agg.sort_values('Shipping Lead Time', ascending=True).head(10),
                x='Shipping Lead Time', y='Route', orientation='h', color='Shipping Lead Time',
                color_continuous_scale='Greens_r'
            )
            st.plotly_chart(fast_fig, use_container_width=True)
            
        with col_b:
            st.write("**Top 10 Bottleneck Routes**")
            slow_fig = px.bar(
                route_agg.sort_values('Shipping Lead Time', ascending=False).head(10),
                x='Shipping Lead Time', y='Route', orientation='h', color='Shipping Lead Time',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(slow_fig, use_container_width=True)

    with tab2:
        st.subheader("Average Lead Time Across States")
        state_agg = filtered.groupby('State/Province')['Shipping Lead Time'].mean().reset_index()
        fig_map = px.choropleth(
            state_agg, locations='State/Province', locationmode="USA-states",
            color='Shipping Lead Time', scope="usa", color_continuous_scale="YlOrRd"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with tab3:
        st.subheader("Ship Mode Performance Comparison")
        fig_box = px.box(filtered, x='Ship Mode', y='Shipping Lead Time', color='Ship Mode')
        st.plotly_chart(fig_box, use_container_width=True)

    with tab4:
        st.subheader("Order Level Inspector")
        st.dataframe(filtered[['Order ID', 'Order Date', 'Ship Date', 'Factory', 'State/Province', 'Ship Mode', 'Shipping Lead Time', 'Sales']])

except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.info("Ensure 'Nassau Candy Distributor.csv' is uploaded in Colab files section.")
