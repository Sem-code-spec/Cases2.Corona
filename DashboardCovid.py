import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
#os.chdir('/home/thijssnel/programeren/jupiter python/minor/week 4/code streamlit')


# RapidAPI key en endpoint setup
api_key = "2d6c64b21emsh6aafbd143bd1297p101fc0jsn3d714e718ef9"  # Vervang met je eigen API-sleutel
api_url = "https://covid-193.p.rapidapi.com/"
headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "covid-193.p.rapidapi.com"
}

gdp_health = pd.read_excel('health_country.xlsx')

# Functie om API-gegevens op te halen
def get_data(endpoint, params=None):
    try:
        response = requests.get(f"{api_url}{endpoint}", headers=headers, params=params)
        response.raise_for_status()  # Controleer of het verzoek succesvol was
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Fout bij het ophalen van gegevens: {e}")
        return None

def api_to_dataframe(url,key,part,param):
	#maakt url om request mee uit te voren
	web = 'https://'+url+'/'+part
	#vult de header en key in
	headers = {"x-rapidapi-key": key,"x-rapidapi-host": url}
	#maakt de reuest met parameters
	response = requests.get(web, headers=headers, params=param).json()
	#zet de respons om tot een dataframe
	df = pd.DataFrame(response['response'])
	return df

def corona_df_unpacker(df,unpack):
	#loopt langs alle kollomen die gegeven zijn in unpack
	for collom in unpack:
		#slaat de key values op van de dicts
		keys = df[collom][1].keys()
		#verwijderd en pakt de dict kollomen uit
		df = pd.concat([df.drop([collom], axis=1), df[collom].apply(pd.Series)], axis=1)
		#benoemt elk kollom door de kollom naam en key naam samen te voegen
		for key in keys:
			df = df.rename(columns={key : key+'_'+collom})
	return df

# Pagina setup met Streamlit
st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")  # Full-screen breedte
st.title("COVID-19 Dashboard")

# Sidebar navigatie voor meerdere pagina's
pagina = st.sidebar.selectbox("Selecteer een pagina", ["Home","Dagelijkse Nieuwe Gevallen", "Statistieken", "Kaartweergave"])

#if pagina == "Home":

    #Display local image
    #local_image_path = r'C:\Users\semvr\OneDrive - HvA\Werktuigbouwkunde\leerjaar 3\Minor Data Science\Periode 1\code streamlit\Corona.afbeelding.png'  # Replace with your local image path
    #st.image(local_image_path, caption="Don't die, get vaccinated!", use_column_width=True,)

    #st.write("De uiteenlopende sterftecijfers tussen landen tijdens de COVID-19-pandemie benadrukken de complexe wisselwerking tussen gezondheidszorgsystemen, overheidsacties, demografische factoren en sociaal gedrag. Daarom zal er gekeken worden naar wat voor invloed deze factoren hebben op het aantal mensen dat stierf")

### Pagina 1: Trendlijn Dagelijkse Nieuwe Gevallen (Nu Pagina 1)
if pagina == "Dagelijkse Nieuwe Gevallen":
    st.header("COVID-19 Trendlijn: Dagelijkse Nieuwe Gevallen per Land")

    # Haal beschikbare landen op
    landen_data = get_data("countries")
    if landen_data and 'response' in landen_data:
        landen = landen_data['response']
        gekozen_land = st.selectbox("Kies een Land", landen)
        
        if gekozen_land:
            # Haal historische gegevens op
            history_data = get_data("history", {"country": gekozen_land})
            
            if history_data and 'response' in history_data:
                history_df = pd.DataFrame(history_data['response'])
                history_df['day'] = pd.to_datetime(history_df['day'])  # Zet de dag om naar datetime object
                
                # Filter en visualiseer nieuwe gevallen
                if 'cases' in history_df.columns:
                    history_df['new_cases'] = history_df['cases'].apply(lambda x: x['new'] if 'new' in x and x['new'] is not None else 0)
                    
                    # Maak een eenvoudige trendlijn met Plotly Express
                    fig = px.line(history_df, x='day', y='new_cases', title=f"Dagelijkse Nieuwe Gevallen in {gekozen_land} door de Tijd")
                    fig.update_layout(xaxis_title='Datum', yaxis_title='Aantal Nieuwe Gevallen')

                    # Toon de grafiek
                    st.plotly_chart(fig)
                else:
                    st.warning(f"Geen gegevens over nieuwe gevallen beschikbaar voor {gekozen_land}")
            else:
                st.error(f"Kon de historische data niet ophalen voor {gekozen_land}")
    else:
        st.error("Kon de lijst met landen niet ophalen.")



### Pagina 2: Geschiedenis (voorheen Huidige Statistieken)
elif pagina == "Statistieken":
    st.header("COVID-19 Statistieken per Land")

    # Haal beschikbare landen op
    landen_data = get_data("countries")
    if landen_data and 'response' in landen_data:
        landen = landen_data['response']
        gekozen_land = st.selectbox("Kies een Land", landen)

        if gekozen_land:
            # Haal huidige statistieken op
            data = get_data("history", {"country": gekozen_land})

            if data and 'response' in data:
                df = pd.DataFrame(data['response'])

                # Visuele presentatie: gebruik kolommen voor overzichtelijkheid
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("Totale Gevallen", df.iloc[0]['cases']['total'])
                with col2:
                    st.metric("Totale Sterfgevallen", df.iloc[0]['deaths']['total'])
                with col3:
                    st.metric("Actieve Gevallen", df.iloc[0]['cases']['active'])
                with col4:
                    st.metric("Totale Tests", df.iloc[0]['tests']['total'])
                with col5:
                    if gdp_health["Country Name"].isin([gekozen_land]).any():
                        gdp_health_country = gdp_health[gdp_health['Country Name'] == gekozen_land]
                        st.metric("Procentuele Zorguitgaven", round(gdp_health_country.iloc[0][2021], 2) if not pd.isna(gdp_health_country.iloc[0][2021]) else 'Geen info')
                    else:
                        st.metric("Procentuele Zorguitgaven", 'Geen info')

                # Grafische weergave met duidelijke visualisaties
                st.subheader(f"Visualisatie van Statistieken voor {gekozen_land}")
                data_for_chart = pd.DataFrame({
                    'Categorie': ['Totale Gevallen', 'Totale Sterfgevallen', 'Actieve Gevallen', 'Totale Tests'],
                    'Aantal': [df.iloc[0]['cases']['total'], df.iloc[0]['deaths']['total'], df.iloc[0]['cases']['active'], df.iloc[0]['tests']['total']]
                })

                fig = px.bar(data_for_chart, x="Categorie", y="Aantal", color="Categorie", title=f"COVID-19 Statistieken voor {gekozen_land}")
                fig.update_layout(yaxis_type='log')
                st.plotly_chart(fig)

                # Toevoegen van een duidelijke scheiding en algemene titel voor de onderste sectie
                st.subheader("Procentuele Zorguitgaven Over de Wereld")

                #weergaven groei gdp uitgaven naar zorg
                st.subheader("Selecteer een Bereik van Jaartallen")
                van, tot = st.slider(
                'Selecteer een Bereik van Jaartallen:',
                min_value=int(2000),
                max_value=int(2023),
                value=(int(2000), int(2023))
                )
                st.subheader(f'Procentuele Zorguitgaven van {van} Tot {tot} Over de Wereld')
                gdp_max = gdp_health[range(van, tot + 1)].quantile(0.75)
                gdp_min = gdp_health[range(van, tot + 1)].quantile(0.25)
                gdp_mean = gdp_health[range(van, tot + 1)].mean()
                fig = go.Figure()
                # Voeg de max-waarden toe als een lijn
                fig.add_trace(go.Scatter(x=gdp_max.index, y=gdp_max, mode='lines', name='75% Waarden', line=dict(color='red')))

                # Voeg de min-waarden toe als een lijn
                fig.add_trace(go.Scatter(x=gdp_max.index, y=gdp_min, mode='lines', name='25% Waarden', line=dict(color='blue')))

                # Voeg de gemiddelde waarden toe als een lijn
                fig.add_trace(go.Scatter(x=gdp_max.index, y=gdp_mean, mode='lines', name='Gemiddelde Waarden', line=dict(color='green')))

                fig.update_layout(
                    xaxis={'title': 'Jaartal'},
                    yaxis={'title': 'Uitgaven Percentage voor Zorg'},
                    legend=dict(
                        x=0,
                        y=1,
                        bgcolor='rgba(255, 255, 255, 0.5)',
                        bordercolor='Black',
                        borderwidth=2
                    ))
                st.plotly_chart(fig)
                
                # Correlatie heatmap
                part = 'statistics'
                corona = api_to_dataframe(url = api_url,key = api_key, part='statistics', param=None)
                corona = corona_df_unpacker(corona, ['cases', 'deaths', 'tests'])
                corona = corona[corona['country'].isin(gdp_health['Country Name'])]
                gdp_health = gdp_health[gdp_health['Country Name'].isin(corona['country'])].rename(columns={'Country Name':'country'})
                jaartal = 2021
                corona = corona.merge(gdp_health[['country', 2021]])
                delen = [corona[jaartal].quantile(i*0.25) for i in range(5)]
                corona['kwart'] = np.where((corona[jaartal] >= delen[0]) & (corona[jaartal] < delen[1]), 1,
                                            np.where((corona[jaartal] >= delen[1]) & (corona[jaartal] < delen[2]), 2, 
                                                    np.where((corona[jaartal] >= delen[2]) & (corona[jaartal] < delen[3]), 3,  
                                                                np.where((corona[jaartal] >= delen[3]) & (corona[jaartal] <= delen[4]), 4, 0))))
                map = corona[['population','1M_pop_tests','1M_pop_cases','1M_pop_deaths',2021]].corr().round(2).rename(columns = {2021:'gdp%'}, index={2021:'gdp%'})
                fig = px.imshow(map, text_auto=True)
                fig.update_layout({'title': 'correlatie heatmap'})
                st.plotly_chart(fig)
                
            else:
                st.error(f"Geen gegevens beschikbaar voor {gekozen_land}.")
    else:
        st.error("Kon de lijst met landen niet ophalen.")


### Pagina 3: Kaartweergave (Ongewijzigd)
elif pagina == "Kaartweergave":
    st.header("Kaartweergave: Doden per inwoners")
    
    # Haal de statistieken per land op
    data = get_data("statistics")
    
    if data and 'response' in data:
        df = pd.DataFrame(data['response'])
        df['deaths_per_million'] = df['deaths'].apply(lambda x: x['total']) / df['population'] * 1_000_000
        fig_doden = px.choropleth(df, locations="country", locationmode="country names",
                            color="deaths_per_million", hover_name="country",
                            title="Doden per miljoen inwoners",
                            color_continuous_scale="Reds")
        
        df['cases_per_million'] = df['cases'].apply(lambda x: x['total']) / df['population'] * 1_000_000
        fig_gevallen = px.choropleth(df, locations="country", locationmode="country names",
                            color="cases_per_million", hover_name="country",
                            title="gevallen per miljoen inwoners",
                            color_continuous_scale="greens")
        
        df['tests_per_million'] = df['tests'].apply(lambda x: x['total']) / df['population'] * 1_000_000
        fig_testen = px.choropleth(df, locations="country", locationmode="country names",
                            color="tests_per_million", hover_name="country",
                            title="testen per miljoen inwoners",
                            color_continuous_scale="blues")
        gekozen_land = st.selectbox("testen / gevallen / doden", ['testen','gevallen','doden'])
        if gekozen_land == 'testen':
            st.plotly_chart(fig_testen)
        elif gekozen_land == 'gevallen':
            st.plotly_chart(fig_gevallen)
        else:
            st.plotly_chart(fig_doden)
        
    else:
        st.error("Kon de gegevens niet ophalen.")
