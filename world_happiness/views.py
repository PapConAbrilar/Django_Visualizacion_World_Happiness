import plotly.express as px
import plotly.offline as opy
import plotly.graph_objects as go
from pycountry_convert import country_name_to_country_alpha3 # pip install pycountry-convert
from django.shortcuts import render
import numpy as np
import pandas as pd
import json
from world_happiness.utils import cargar_csv
from decimal import Decimal
from world_happiness.models import Pais, Region
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

datos = pd.read_csv('world_happiness/2015.csv')

def happiness(request):
    try:
        qs = Pais.objects.all().values(
            'happiness_score', 'family', 'trust', 'health',
            'dystopia', 'generosity', 'economy', 'freedom'
        )

        # Verificar si hay datos
        if not qs:
            return render(request, 'world_happiness/happiness.html', {
                'error': 'No hay datos disponibles en la base de datos.',
                'active_page': 'happiness'
            })

        df = pd.DataFrame(list(qs))

        # Verificar que el DataFrame no esté vacío
        if df.empty:
            return render(request, 'world_happiness/happiness.html', {
                'error': 'El DataFrame está vacío.',
                'active_page': 'happiness'
            })

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

        # Calcular correlación
        corr = df.corr()

        # DEBUG: Verificar la forma de la matriz de correlación
        print(f"Forma de corr: {corr.shape}")
        print(f"Columnas de corr: {corr.columns.tolist()}")

        # Verificar que la matriz de correlación tenga datos
        if corr.empty or corr.shape[0] == 0 or corr.shape[1] == 0:
            return render(request, 'world_happiness/happiness.html', {
                'error': 'No se pudo calcular la matriz de correlación.',
                'active_page': 'happiness'
            })

        # Verificar que haya suficientes columnas para el slicing [1:]
        if corr.shape[1] <= 1:
            labels = []
            data_c = []
        else:
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

    except Exception as e:
        # Capturar cualquier error y mostrar información detallada
        import traceback
        error_details = traceback.format_exc()
        
        return render(request, 'world_happiness/happiness.html', {
            'error': f'Error al generar el gráfico: {str(e)}',
            'error_details': error_details,
            'active_page': 'happiness'
        })



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
            scope="world"
            )
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


# 'SORPRENDAME'

def dashboard_interactivo(request):
    # Obtener todos los países con sus regiones
    paises = Pais.objects.select_related('id_region').all()
    
    # Preparar los datos para el gráfico
    datos_list = []
    for pais in paises:
        datos_list.append({
            'Country': pais.nombre,
            'Region': pais.id_region.nombre,
            'Happiness Score': float(pais.happiness_score),
            'Economy (GDP per Capita)': float(pais.economy),
            'Family': float(pais.family),
            'Health (Life Expectancy)': float(pais.health),
            'Freedom': float(pais.freedom),
            'Trust (Government Corruption)': float(pais.trust) if pais.trust else 0,
            'Generosity': float(pais.generosity),
            'Dystopia Residual': float(pais.dystopia),
        })
    
    # Obtener regiones únicas
    regiones = Region.objects.values_list('nombre', flat=True).distinct()
    
    metricas = ['Happiness Score', 'Economy (GDP per Capita)', 'Family', 
                'Health (Life Expectancy)', 'Freedom', 'Trust (Government Corruption)', 
                'Generosity']
    
    context = {
        'datos_json': json.dumps(datos_list),
        'regiones': list(regiones),
        'metricas': metricas,
        'active_page': 'dashboard'
    }
    return render(request, 'world_happiness/dashboard.html', context)
# bibliografia rapida
"""
https://www.coding2go.com/sidebar-menu
"""



def agregar_pais(request):
    regiones = Region.objects.all()
    
    if request.method == "POST":
        nombre_pais = request.POST["nombre"]
        
        # Validar que el país no exista
        if Pais.objects.filter(nombre=nombre_pais).exists():
            messages.error(request, f"El país '{nombre_pais}' ya existe en la base de datos.")
            return render(request, "world_happiness/agregar_pais.html", {
                "regiones": regiones
            })
        
        try:
            # Validar que la región exista
            region = Region.objects.get(id_region=request.POST["id_region"])
            
            # Crear el nuevo país
            Pais.objects.create(
                nombre=nombre_pais,
                id_region=region,
                happiness_score=Decimal(request.POST["happiness_score"]),
                standard_error=Decimal(request.POST.get("standard_error", 0)),
                economy=Decimal(request.POST["economy"]),
                family=Decimal(request.POST["family"]),
                health=Decimal(request.POST["health"]),
                freedom=Decimal(request.POST["freedom"]),
                trust=Decimal(request.POST.get("trust", 0)),
                generosity=Decimal(request.POST["generosity"]),
                dystopia=Decimal(request.POST["dystopia"]),
            )
            
            messages.success(request, f"País '{nombre_pais}' agregado correctamente.")
            return redirect('agregar_pais')  # Redirigir para limpiar el formulario
            
        except Region.DoesNotExist:
            messages.error(request, "La región seleccionada no existe.")
        except InvalidOperation:
            messages.error(request, "Error en los formatos numéricos. Use puntos para decimales.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    return render(request, "world_happiness/agregar_pais.html", {
        "regiones": regiones
    })


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

def agregar_pais_csv(request):
    if request.method == "POST":
        if "csv_file" not in request.FILES:
            messages.error(request, "Debe seleccionar un archivo.")
            return render(request, "world_happiness/agregar_pais_csv.html")

        try:
            csv_file = request.FILES["csv_file"]
            
            # Validar extensión del archivo
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "El archivo debe ser un CSV.")
                return render(request, "world_happiness/agregar_pais_csv.html")
            
            df = pd.read_csv(csv_file)

            columnas_esperadas = [
                "Country", "Region", "Happiness Score", "Family",
                "Trust (Government Corruption)", "Health (Life Expectancy)",
                "Dystopia Residual", "Generosity",
                "Economy (GDP per Capita)", "Freedom"
            ]

            if not all(col in df.columns for col in columnas_esperadas):
                messages.error(request, "El CSV no tiene el formato correcto.")
                return render(request, "world_happiness/agregar_pais_csv.html")

            paises_creados, paises_actualizados = cargar_csv(df)
            
            messages.success(request, 
                f"Datos cargados correctamente. "
                f"Países creados: {paises_creados}, "
                f"Países actualizados: {paises_actualizados}"
            )
            return redirect('agregar_pais_csv')

        except Exception as e:
            messages.error(request, f"Error procesando el archivo: {str(e)}")
            return render(request, "world_happiness/agregar_pais_csv.html")

    return render(request, "world_happiness/agregar_pais_csv.html")

def inicio(request):
    return render(request, 'inicio.html')


@login_required
def panel_privado(request):
    return render(request, 'panel_privado.html')
