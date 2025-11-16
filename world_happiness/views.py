import plotly.express as px
import plotly.offline as opy
import plotly.graph_objects as go
from pycountry_convert import country_name_to_country_alpha3 # pip install pycountry-convert
from django.shortcuts import render
import numpy as np
import pandas as pd
from world_happiness.utils import cargar_csv
from decimal import Decimal
from world_happiness.models import Pais, Region

datos = pd.read_csv('world_happiness/2015.csv')

def happiness(request):

    qs = Pais.objects.all().values(
        'happiness_score', 'family', 'trust', 'health',
        'dystopia', 'generosity', 'economy', 'freedom'
    )

    df = pd.DataFrame(list(qs))

    df = df.rename(columns={
        'happiness_score': 'Happiness Score',
        'family': 'Family',
        'trust': 'Trust (Government Corruption)',
        'health': 'Health (Life Expectancy)',
        'dystopia': 'Dystopia Residual',
        'generosity': 'Generosity',
        'economy': 'Economy (GDP per Capita)',
        'freedom': 'Freedom'
    })

    corr = df.corr()

    labels = list(corr.columns[1:])
    data_c = corr.iloc[0, 1:].tolist()

    default_color = '#2E86AB'
    highlight_color_A = '#A23B72'
    highlight_color_B = '#F18F01'

    highlights_A = ['Economy (GDP per Capita)', 'Family', 'Health (Life Expectancy)']
    highlights_B = ['Generosity']

    colors = [
        highlight_color_A if label in highlights_A else
        highlight_color_B if label in highlights_B else
        default_color
        for label in labels
    ]

    context = {
        'labels_data': labels,
        'datac_data': data_c,
        'colors_data': colors,
        'active_page': 'happiness'
    }
    return render(request, 'world_happiness/happiness.html', context)



def economy(request):
    paises_qs = Pais.objects.select_related('id_region').all()

    paises = [p.nombre for p in paises_qs]
    gdp = [float(p.economy) for p in paises_qs]
    felicidad = [float(p.happiness_score) for p in paises_qs]
    regiones = [p.id_region.nombre for p in paises_qs]
    regiones_unicas = sorted(list(set(regiones)))

    context = {
        'paises': paises,
        'gdp': gdp,
        'felicidad': felicidad,
        'regiones': regiones,
        'regiones_unicas': regiones_unicas,
        'active_page': 'economy'
    }

    return render(request, 'world_happiness/economy.html', context)



def trust(request):
    trust_data = datos[['Country','Trust (Government Corruption)']].to_dict('list')
    context = {'active_page':'trust', 'trust_data':trust_data}
    return render(request, 'world_happiness/trust.html', context)


def generosity_freedom(request):
    paises = list(Pais.objects.all().order_by('-happiness_score'))

    happy = paises[:10]
    unhappy = list(Pais.objects.all().order_by('happiness_score')[:10])

    happy_data = {
        'Country': [p.nombre for p in happy],
        'Generosity': [float(p.generosity) for p in happy],
        'Freedom': [float(p.freedom) for p in happy],
    }

    unhappy_data = {
        'Country': [p.nombre for p in unhappy],
        'Generosity': [float(p.generosity) for p in unhappy],
        'Freedom': [float(p.freedom) for p in unhappy],
    }

    context = {
        'active_page': 'generosity',
        'happy_data': happy_data,
        'unhappy_data': unhappy_data
    }

    return render(request, 'world_happiness/generosity_freedom.html', context)


def get_iso_alpha(country_name):
    try:
        return country_name_to_country_alpha3(country_name)
    except:
        return None


def mapa_mundi(request):
    datos['iso_alpha'] = datos['Country'].apply(get_iso_alpha)
    
    metricas = ['Happiness Score', 'Family', 'Trust (Government Corruption)',
                'Health (Life Expectancy)', 'Dystopia Residual',
                'Generosity', 'Economy (GDP per Capita)']
    
    graphs = {}
    for metrica in metricas:
        fig = px.choropleth(datos,
                           locations="iso_alpha",
                           color=metrica,
                           hover_name="Country",
                           color_continuous_scale=px.colors.sequential.Plasma,
                           title=f"{metrica} por País",
                           scope="world")
        fig.update_layout(
            margin=dict(l=30, r=315, t=50, b=30),
            autosize=False,
            width=1396,
            height=600,
            paper_bgcolor="#192125",
            geo_bgcolor="#192125",
            font_color = 'white',
            font_size = 15
            )
        
        # Conversión a html
        graph_html = opy.plot(fig, auto_open=False, output_type='div')
        graphs[metrica] = graph_html
    
    context = {
        'graphs': graphs,
        'metricas': metricas,
        'active_page':'mapa_mundi'
    }
    
    return render(request, 'world_happiness/mapa_mundi.html', context)


def index(request):
    context = {'active_page':'index'}
    return render(request, 'world_happiness/index.html', context)
# bibliografia rapida
"""
https://www.coding2go.com/sidebar-menu
"""

def agregar_pais(request):
    regiones = Region.objects.all()
    msg = None

    if request.method == "POST":
        Pais.objects.create(
            nombre=request.POST["nombre"],
            id_region=Region.objects.get(id_region=request.POST["id_region"]),
            happiness_score=Decimal(request.POST["happiness_score"]),
            standard_error=Decimal(request.POST["standard_error"]),
            economy=Decimal(request.POST["economy"]),
            family=Decimal(request.POST["family"]),
            health=Decimal(request.POST["health"]),
            freedom=Decimal(request.POST["freedom"]),
            trust=Decimal(request.POST["trust"]),
            generosity=Decimal(request.POST["generosity"]),
            dystopia=Decimal(request.POST["dystopia"]),
        )

        msg = "País agregado correctamente."

    return render(request, "world_happiness/agregar_pais.html", {
        "regiones": regiones,
        "msg": msg
    })

def agregar_pais_csv(request):
    if request.method == "POST":
        if "csv_file" not in request.FILES:
            return render(request, "world_happiness/agregar_pais_csv.html", {"error": "Debe seleccionar un archivo."})

        try:
            csv_file = request.FILES["csv_file"]
            df = pd.read_csv(csv_file)

            columnas_esperadas = [
                "Country", "Region", "Happiness Score", "Family",
                "Trust (Government Corruption)", "Health (Life Expectancy)",
                "Dystopia Residual", "Generosity",
                "Economy (GDP per Capita)", "Freedom"
            ]

            if not all(col in df.columns for col in columnas_esperadas):
                return render(request, "world_happiness/subir_csv.html", {
                    "error": "El CSV no tiene el formato correcto."
                })

            cargar_csv(df)
            return render(request, "world_happiness/agregar_pais_csv.html", {"msg": "Datos cargados correctamente."})

        except Exception as e:
            return render(request, "world_happiness/agregar_pais_csv.html", {"error": f"Error: {e}"})

    return render(request, "world_happiness/agregar_pais_csv.html")