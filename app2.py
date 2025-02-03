import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('trends.csv')
df2 = pd.read_csv('countries.csv')

# Merge the data
df = pd.merge(df, df2, left_on='Geo Location', right_on='country', how='left')
df['Traffic volume'] = df['Traffic volume'].str.replace('K', '000').str.replace('+', '')
df['Traffic volume'] = pd.to_numeric(df['Traffic volume'], errors='coerce')

# Drop rows with NaN values in "Traffic volume"
df = df.dropna(subset=['Traffic volume'])

# Check if mapping was successful
if df['name'].isnull().any():
    st.warning("Some Geo Locations could not be mapped to country names.")

# Create HTML info strings
df['Info'] = df.apply(lambda row: f"<a href='{row['Link']}'>{row['Title']}</a><br>Traffic volume: {row['Traffic volume']}", axis=1)
df_info = df.groupby('name')['Info'].apply('<br>'.join).reset_index()

# Streamlit app
st.title('Google Trends News Visualization')

# Create optimized choropleth map
fig = px.choropleth(
    df_info,
    locations="name",
    locationmode="country names",
    hover_name="name",
    hover_data={"Info": True},
    projection="equirectangular",
    title="Trending News Topics by Country",
    color_continuous_scale=px.colors.sequential.Viridis
)

# Mobile-optimized geosettings
fig.update_geos(
    showcoastlines=True,
    coastlinecolor="SlateGray",
    showland=True,
    landcolor="MintCream",
    showocean=True,
    oceancolor="LightSkyBlue",
    fitbounds="locations",
    visible=False
)

# Responsive layout configuration
fig.update_layout(
    dragmode=False,
    autosize=True,
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
        showframe=False,
        showcoastlines=True,
        coastlinecolor="Gray"
    ),
    title=dict(
        text="Trending News Topics by Country",
        font=dict(size=24)
    ),
    config={
        'scrollZoom': False,
        'displayModeBar': False
    }
)

# Display the map with responsive container
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Top trending topics visualization
df_trending = df.groupby('Title')['Traffic volume'].sum().reset_index()
df_trending = df_trending.sort_values(by='Traffic volume', ascending=False)
top_trending = df_trending.head(10)

# Mobile-friendly bar chart
fig_trending = px.bar(
    top_trending,
    x='Traffic volume',
    y='Title',
    orientation='h',
    title='Top 10 Trending News Topics by Traffic Volume',
    labels={'Traffic volume': 'Traffic Volume', 'Title': 'News Title'},
    color='Traffic volume',
    color_continuous_scale=px.colors.sequential.Plasma
)

# Responsive bar chart layout
fig_trending.update_layout(
    autosize=True,
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    yaxis=dict(categoryorder='total ascending'),
    xaxis=dict(tickformat=",d")
)

# Display the bar chart
st.plotly_chart(fig_trending, use_container_width=True)

# Optional: Add mobile-friendly expanders for additional info
with st.expander("ℹ️ Mobile Usage Tips"):
    st.markdown("""
    - **Tap** country names to see details
    - **Scroll vertically** to see both visualizations
    - **Rotate screen** for better landscape viewing
    - **Click links** in popups to visit news sources
    """)

# Add a loading spinner for initial data load
with st.spinner('Loading complete!'):
    pass
