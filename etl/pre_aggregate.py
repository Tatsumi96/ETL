
import pandas as pd
import sqlite3

def pre_aggregate_data(db_path):
    """
    Charge les données, effectue les agrégations et les sauvegarde dans de nouvelles tables.
    """
    conn = sqlite3.connect(db_path)
    
    # Charger les données
    query = """
    SELECT
        fc.*,
        da.nom_agence,
        dp.nom_produit,
        dg."gestionnaire de compte" as gestionnaire
    FROM fact_comptes fc
    LEFT JOIN dim_agence da ON fc.code_agence = da.code_agence
    LEFT JOIN dim_produit dp ON fc.code_produit = dp.code_produit
    LEFT JOIN dim_gestionnaire dg ON fc.id_gestionnaire = dg.id_gestionnaire
    """
    df = pd.read_sql_query(query, conn)
    
    # 1. Encours par produit
    encours_par_produit = df.groupby('nom_produit')['AvailableBalance'].sum().reset_index()
    encours_par_produit.to_sql('agg_encours_par_produit', conn, if_exists='replace', index=False)
    
    # 2. Répartition par agences
    repartition_agences = df.groupby('nom_agence').agg(
        montant=('AvailableBalance', 'sum'),
        nombre_de_compte=('noCompte', 'nunique')
    ).reset_index()
    repartition_agences.to_sql('agg_repartition_agences', conn, if_exists='replace', index=False)
    
    # 3. Top 10 performance gestionnaire
    perf_gestionnaire = df.groupby('gestionnaire').agg(
        montant=('AvailableBalance', 'sum'),
        nombre_de_compte=('noCompte', 'nunique')
    ).reset_index().nlargest(10, 'montant')
    perf_gestionnaire.to_sql('agg_perf_gestionnaire', conn, if_exists='replace', index=False)
    
    # 4. Top 10 déposants
    top_deposants = df.groupby('Code')['AvailableBalance'].sum().reset_index().nlargest(10, 'AvailableBalance')
    top_deposants.rename(columns={'Code': 'Client code', 'AvailableBalance': 'Total Encours'}, inplace=True)
    top_deposants.to_sql('agg_top_deposants', conn, if_exists='replace', index=False)
    
    conn.close()

if __name__ == '__main__':
    pre_aggregate_data('database.db')
