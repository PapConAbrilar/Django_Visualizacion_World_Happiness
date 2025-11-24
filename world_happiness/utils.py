import pandas as pd
from world_happiness.models import Pais, Region
from decimal import Decimal

def cargar_csv(df):
    """Función auxiliar para cargar datos del CSV"""
    paises_creados = 0
    paises_actualizados = 0
    
    for index, row in df.iterrows():
        try:
            # Buscar o crear la región
            region, created = Region.objects.get_or_create(
                nombre=row['Region']
            )
            
            # Buscar o crear el país
            pais, created = Pais.objects.update_or_create(
                nombre=row['Country'],
                defaults={
                    'id_region': region,
                    'happiness_score': Decimal(str(row['Happiness Score'])),
                    'economy': Decimal(str(row['Economy (GDP per Capita)'])),
                    'family': Decimal(str(row.get('Family', 0))),
                    'health': Decimal(str(row.get('Health (Life Expectancy)', 0))),
                    'freedom': Decimal(str(row.get('Freedom', 0))),
                    'trust': Decimal(str(row.get('Trust (Government Corruption)', 0))),
                    'generosity': Decimal(str(row.get('Generosity', 0))),
                    'dystopia': Decimal(str(row.get('Dystopia Residual', 0))),
                    'standard_error': Decimal(str(row.get('Standard Error', 0))),
                }
            )
            
            if created:
                paises_creados += 1
            else:
                paises_actualizados += 1
                
        except Exception as e:
            print(f"Error procesando {row['Country']}: {str(e)}")
            continue
    
    return paises_creados, paises_actualizados