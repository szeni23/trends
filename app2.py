import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('trends.csv')
df2 = pd.read_csv('countries.csv')

df = pd.merge(df, df2, left_on='Geo Location', right_on='country', how='left')
df['Traffic volume'] = df['Traffic volume'].str.replace('K', '000').str.replace('+', '')
df['Traffic volume'] = pd.to_numeric(df['Traffic volume'], errors='coerce')
df = df.dropna(subset=['Traffic volume'])

if df['name'].isnull().any():
    st.warning("Some Geo Locations could not be mapped to country names.")

df['Info'] = df.apply(lambda row: f"<a href='{row['Link']}'>{row['Title']}</a><br>Traffic volume: {row['Traffic volume']}", axis=1)
df_info = df.groupby('name')['Info'].apply('<br>'.join).reset_index()

st.title('Google Trends News Visualization')

fig = px.choropleth(
    df_info,
    locations="name",
    locationmode="country names",
    hover_name="name",
    hover_data={"Info": True},
    projection="orthographic",
    title="Trending News Topics by Country",
    color_continuous_scale=px.colors.sequential.Viridis
)

fig.update_geos(
    showcoastlines=True,
    coastlinecolor="SlateGray",
    showland=True,
    landcolor="MintCream",
    showocean=True,
    oceancolor="LightSkyBlue",
    showlakes=True,
    lakecolor="LightBlue",
    showrivers=True,
    rivercolor="Aqua"
)

fig.update_layout(
    autosize=True,
    margin={"r": 10, "t": 50, "l": 10, "b": 10},
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
        showframe=False,
        showcoastlines=True,
        coastlinecolor="Gray"
    ),
    title=dict(
        text="Trending News Topics by Country",
        font=dict(size=20)
    )
)

fig.update_traces(hovertemplate='%{customdata[0]}')

st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

df_trending = df.groupby('Title')['Traffic volume'].sum().reset_index()
df_trending = df_trending.sort_values(by='Traffic volume', ascending=False)
top_trending = df_trending.head(10)

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

fig_trending.update_layout(
    autosize=True,
    margin={"r": 10, "t": 50, "l": 10, "b": 10},
    yaxis=dict(categoryorder='total ascending')
)

st.plotly_chart(fig_trending, use_container_width=True, config={'responsive': True})
