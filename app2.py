import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('trends.csv')
    df2 = pd.read_csv('countries.csv')
    return df, df2

df, df2 = load_data()

# Merge and clean data
df = pd.merge(df, df2, left_on='Geo Location', right_on='country', how='left')
df['Traffic volume'] = df['Traffic volume'].str.replace('K', '000').str.replace('+', '')
df['Traffic volume'] = pd.to_numeric(df['Traffic volume'], errors='coerce')
df = df.dropna(subset=['Traffic volume', 'name'])

# Create HTML info strings
df['Info'] = df.apply(lambda row: 
    f"<a href='{row['Link']}' target='_blank'>{row['Title']}</a><br>"
    f"Traffic volume: {row['Traffic volume']:,}", 
    axis=1
)
df_info = df.groupby('name')['Info'].apply('<br><br>'.join).reset_index()

# Streamlit app layout
st.title('Google Trends News Visualization')
st.markdown("### Interactive Global News Trends Map")

# Create optimized choropleth map
with st.spinner('Loading world map...'):
    fig = px.choropleth(
        df_info,
        locations="name",
        locationmode="country names",
        hover_name="name",
        hover_data={"Info": True},
        projection="equirectangular",
        color_continuous_scale=px.colors.sequential.Viridis
    )

    # Mobile-optimized geosettings
    fig.update_geos(
        visible=False,
        showcountries=True,
        fitbounds="locations",
        resolution=50
    )

    # Responsive layout configuration
    fig.update_layout(
        dragmode=False,
        autosize=True,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        geo=dict(
            bgcolor='rgba(255,255,255,0.1)',
            showframe=False,
            landcolor='MintCream',
            subunitcolor='Gray'
        ),
        title=None
    )

    # Disable plotly controls
    fig.update_layout(
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False)
    )
    
    # Set config separately
    fig.config.update({
        'scrollZoom': False,
        'displayModeBar': False,
        'responsive': True
    })

    # Display the map
    st.plotly_chart(fig, use_container_width=True)

# Top trending section
st.markdown("---")
st.markdown("### Top Trending News Topics")

# Process trending data
@st.cache_data
def get_trending_data():
    df_trending = df.groupby('Title')['Traffic volume'].sum().reset_index()
    return df_trending.sort_values(by='Traffic volume', ascending=False).head(10)

top_trending = get_trending_data()

# Create mobile-friendly bar chart
with st.spinner('Loading trends...'):
    fig_trending = px.bar(
        top_trending,
        x='Traffic volume',
        y='Title',
        orientation='h',
        labels={'Traffic volume': 'Traffic Volume', 'Title': ''},
        color='Traffic volume',
        color_continuous_scale=px.colors.sequential.Plasma
    )

    # Responsive bar chart layout
    fig_trending.update_layout(
        autosize=True,
        margin={"r": 10, "t": 0, "l": 0, "b": 0},
        yaxis=dict(categoryorder='total ascending'),
        xaxis=dict(tickformat=",d"),
        showlegend=False,
        height=max(400, 50 * len(top_trending))
    )
    
    st.plotly_chart(fig_trending, use_container_width=True)

# Mobile help section
with st.expander("📱 Mobile Usage Guide"):
    st.markdown("""
    **Optimized for mobile devices:**
    - Tap country names to see news details
    - Vertical scroll for navigation
    - Landscape mode recommended for maps
    - Links open in new tabs
    - Pull-to-refresh for updates
    """)

# Data disclaimer
st.caption("Note: Data aggregated from Google Trends. Updated hourly.")
