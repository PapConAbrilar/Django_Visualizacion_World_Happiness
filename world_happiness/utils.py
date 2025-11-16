import pandas as pd
from world_happiness.models import Pais, Region

def cargar_csv(df):

    # Renombrar columnas EXACTAS del CSV a nombres más simples
    df = df.rename(columns={
        "Happiness Rank": "happiness_rank",
        "Happiness Score": "happiness_score",
        "Standard Error": "standard_error",
        "Economy (GDP per Capita)": "economy",
        "Family": "family",
        "Health (Life Expectancy)": "health",
        "Freedom": "freedom",
        "Trust (Government Corruption)": "trust",
        "Generosity": "generosity",
        "Dystopia Residual": "dystopia",
        "Country": "country",
        "Region": "region",
    })

    for _, row in df.iterrows():

        region_obj, _ = Region.objects.get_or_create(
            nombre=row["region"]
        )

        Pais.objects.create(
            nombre=row["country"],
            id_region=region_obj,
            happiness_score=row["happiness_score"],
            standard_error=row["standard_error"],
            economy=row["economy"],
            family=row["family"],
            health=row["health"],
            freedom=row["freedom"],
            trust=row["trust"],
            generosity=row["generosity"],
            dystopia=row["dystopia"],
        )
