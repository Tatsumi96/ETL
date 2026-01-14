
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

DB_PATH = "database.db"

@st.cache_data
def load_aggregated_data():
    """
    Charge les données agrégées depuis la base de données SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    encours_par_produit = pd.read_sql_query("SELECT * FROM agg_encours_par_produit", conn)
    repartition_agences = pd.read_sql_query("SELECT * FROM agg_repartition_agences", conn)
    perf_gestionnaire = pd.read_sql_query("SELECT * FROM agg_perf_gestionnaire", conn)
    top_deposants = pd.read_sql_query("SELECT * FROM agg_top_deposants", conn)
    conn.close()
    return encours_par_produit, repartition_agences, perf_gestionnaire, top_deposants

encours_par_produit, repartition_agences, perf_gestionnaire, top_deposants = load_aggregated_data()

st.set_page_config(layout="wide")

st.title("Compte client")

# --- TotalEncours (montant) par produit ---
st.header("Total Encours (montant) par produit")
fig_produit = px.pie(encours_par_produit,
                     values='AvailableBalance',
                     names='nom_produit',
                     hole=0.6,
                     title="Total Encours par Produit")
fig_produit.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_produit, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    # --- Répartition par Agences ---
    st.header("Répartition par Agences")
    fig_agences = make_subplots(specs=[[{"secondary_y": True}]])

    fig_agences.add_trace(
        go.Bar(x=repartition_agences['nom_agence'], y=repartition_agences['montant'], name='Encours (Montant)'),
        secondary_y=False,
    )

    fig_agences.add_trace(
        go.Scatter(x=repartition_agences['nom_agence'], y=repartition_agences['nombre_de_compte'], name='Nombre de compte', mode='lines'),
        secondary_y=True,
    )

    fig_agences.update_layout(
        title_text="Répartition par Agences",
        xaxis_title="Agence"
    )
    fig_agences.update_yaxes(title_text="Montant en Millions", secondary_y=False)
    fig_agences.update_yaxes(title_text="Nombre de compte", secondary_y=True)
    st.plotly_chart(fig_agences, use_container_width=True)

    # --- Top 10 Performance gestionnaire ---
    st.header("Top 10 Performance gestionnaire")
    fig_gestionnaire = make_subplots(specs=[[{"secondary_y": True}]])

    fig_gestionnaire.add_trace(
        go.Bar(x=perf_gestionnaire['gestionnaire'], y=perf_gestionnaire['montant'], name='Encours de dépôt'),
        secondary_y=False,
    )

    fig_gestionnaire.add_trace(
        go.Scatter(x=perf_gestionnaire['gestionnaire'], y=perf_gestionnaire['nombre_de_compte'], name='Nombre de compte', mode='lines'),
        secondary_y=True,
    )

    fig_gestionnaire.update_layout(
        title_text="Top 10 Performance gestionnaire",
        xaxis_title="Gestionnaire"
    )
    fig_gestionnaire.update_yaxes(title_text="Montant en millions", secondary_y=False)
    fig_gestionnaire.update_yaxes(title_text="Nombre de compte", secondary_y=True)
    st.plotly_chart(fig_gestionnaire, use_container_width=True)

with col2:
    # --- Top 10 déposants ---
    st.header("Top 10 déposants")
    st.dataframe(top_deposants.style.format({"Total Encours": "{:,.2f}"}), use_container_width=True)

    total_encours_top10 = top_deposants['Total Encours'].sum()
    total_encours_total = repartition_agences['montant'].sum()
    concentration_risk = (total_encours_top10 / total_encours_total) * 100

    st.metric(label="Total des 10 premiers déposants", value=f"{total_encours_top10:,.2f}")
    st.metric(label="Encours total", value=f"{total_encours_total:,.2f}")
    st.metric(label="% de concentration de risque", value=f"{concentration_risk:.2f}%")

