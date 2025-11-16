from django.apps import AppConfig
import pandas as pd
import os


class WorldHappinessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'world_happiness'

    def ready(self):
        from world_happiness.models import Pais
        from world_happiness.utils import cargar_csv

        if Pais.objects.count() == 0:
            csv_path = os.path.join(
                os.path.dirname(__file__),
                "2015.csv"
            )

            df = pd.read_csv(csv_path)
            cargar_csv(df)
            print("Datos del CSV original cargados automáticamente.")