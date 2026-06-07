import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title = 'Restaurants with Vegetarian Options', layout = 'wide')

# data
SHEET_ID = "10UpuaSE9N5Zc4cOxvNaXYlwyeMULvFRIhpuaPmUXXk4"

restaurants_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1572529624"
)

malls_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=31702557"
)

mapping_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1760479065"
)

meta_url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=200004708")

restaurants_df = pd.read_csv(restaurants_url)
malls_df = pd.read_csv(malls_url)
mapping_df = pd.read_csv(mapping_url)
meta_df = pd.read_csv(meta_url)

@st.cache_data(ttl=300)
def load_data():

    restaurants_df = pd.read_csv(restaurants_url)
    malls_df = pd.read_csv(malls_url)
    mapping_df = pd.read_csv(mapping_url)
    meta_df = pd.read_csv(meta_url)

    return restaurants_df, malls_df, mapping_df, meta_df

restaurants_df, malls_df, mapping_df, meta_df = load_data()

last_updated = meta_df.loc[
    meta_df["Key"] == "last_updated", "Value"
].values[0]

st.title('Find Vegetarian Options')
st.caption('Find vegetarian-friendly dining options across malls in Singapore. \n Use filters or browse by mall to explore restaurants easily.')

# filter by area sidebar
st.sidebar.caption(
    "This list is non-exhaustive and will be updated over time. "
    "While efforts have been made to ensure accuracy, some information may not be fully up to date or complete."
)
st.sidebar.caption(f"Last updated: {last_updated}")
st.sidebar.header("Filters")

selected_area = st.sidebar.multiselect(
    "Filter by Area",
    sorted(malls_df["Area"].dropna().unique())
)

malls_filtered = malls_df.copy()
mapping_filtered = mapping_df.copy()

if selected_area:
    malls_filtered = malls_df[malls_df["Area"].isin(selected_area)]

    valid_malls = malls_filtered["Mall Name"]

    mapping_filtered = mapping_df[
        mapping_df["Mall Name"].isin(valid_malls)
    ]

restaurants_filtered = restaurants_df[
    restaurants_df["Restaurant Name"].isin(
        mapping_filtered["Restaurant Name"]
    )
]

# tabs
tab1, tab2 = st.tabs([
    "🍽 Restaurants",
    "🏬 Browse by Mall"
])

# tab 1 - masterlist
with tab1:
    st.subheader("Restaurants")
    st.info(
        "Click on row to view restaurant's available locations. Use sidebar filter to narrow results by area or mall location."
    )

    # create clickable table
    event = st.dataframe(
        restaurants_filtered,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    selected_restaurant = None

    if event.selection.rows:
        idx = event.selection.rows[0]
        selected_restaurant = restaurants_filtered.iloc[idx]["Restaurant Name"]
    
    if selected_restaurant:
        st.divider()
        st.subheader(selected_restaurant)

        # Available at (FILTERED)
        restaurant_malls = mapping_filtered[
            mapping_filtered["Restaurant Name"] == selected_restaurant
        ]["Mall Name"].tolist()

        st.write("### 📍 Available at")

        if restaurant_malls:
            for mall in restaurant_malls:
                st.write("•", mall)
        else:
            st.write("No locations available in current filter.")

# tab 2 - search by malls
with tab2:
    st.subheader("Browse by Mall")

    selected_mall = st.selectbox(
        "Select Mall",
        sorted(malls_filtered["Mall Name"].unique())
    )

    mall_area = malls_filtered[
        malls_filtered["Mall Name"] == selected_mall
    ]["Area"].values[0]

    mall_restaurants = mapping_filtered[
        mapping_filtered["Mall Name"] == selected_mall
    ]["Restaurant Name"]

    # METRICS
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Area", mall_area)

    with col2:
        st.metric("Number of Restaurants", len(mall_restaurants))

    st.divider()

    st.dataframe(
        restaurants_filtered[
            restaurants_filtered["Restaurant Name"].isin(mall_restaurants)
        ],
        use_container_width=True,
        hide_index=True
    )
