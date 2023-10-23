from django.shortcuts import render, redirect
from firebase_admin import firestore, auth
from django.http import JsonResponse
import datetime
import re
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Create your views here.
def getData(request):    
    db = firestore.client()
    coleccion = db.collection('user')
    datos = coleccion.stream() 

    datos_procesados = [{'administrador': dato.get("administrador"), 'email': dato.get("email")} for dato in datos]

    return render(request, 'report/index.html', {'datos': datos_procesados})


# @csrf_exempt
def view_report(request):
    try:
        usuarios_ref = firestore.client().collection('user')
        usuarios_docs = usuarios_ref.stream()

        usuarios = [doc.to_dict()['email'] for doc in usuarios_docs]
        # print(f'Lista de Usuarios: {usuarios}')

        if request.method == 'POST':
            fecha_inicio = request.POST.get('fechaInicio')
            fecha_fin = request.POST.get('fechaFin')
            usuario = request.POST.get('usuario')
            # print(f'Fecha de Inicio: {fecha_inicio}')
            # print(f'Fecha de Fin: {fecha_fin}')
            # print(f'Usuario seleccionado: {usuario}')

            # Consultar en Firebase
            retorno = []
            date_start_search = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            date_end_search = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            # print(date_start_search)
            # print(date_end_search)

            config_data = firestore.client().collection('configuracion').get()
            data = firestore.client().collection('log').get()

            contador = 1
            contador_registros = 0
            sumatoria_glns = 0
            sumatoria_km = 0

            for row in data:
                data_row = row.to_dict()

                if usuario != '[TODOS]' and usuario.lower() != data_row['user'].lower():
                    continue

                date_start_row = datetime.datetime.strptime(data_row['horaInicio'], '%d/%m/%Y - %H:%M')
                date_end_row = datetime.datetime.strptime(data_row['horaFin'], '%d/%m/%Y - %H:%M')
                               
                # print(date_start_row)
                # print(date_end_row)

                inserta_info = date_start_row >= date_start_search and date_end_row <= date_end_search

                for config_row in config_data:
                    config_row_data = config_row.to_dict()
                    galones = config_row_data.get('galones', '')
                    depreciacion = config_row_data.get('depreciacion', '')                    
               
                if inserta_info:
                    km_rec_str = data_row['kmRecorrido']
                    numbers = re.findall(r'\d+\.\d+|\d+', km_rec_str)
                    if numbers:
                      # Tomar el primer conjunto de números encontrado y convertirlo a entero
                      km_rec_num = Decimal(numbers[0])
                      # Multiplicar por 2
                      multiplied_km = round(km_rec_num * Decimal(2), 3)  
                      multiplied_glns = round(km_rec_num * Decimal(0.5), 3)  
                    retorno.append([
                        contador,
                        data_row['departamento'],
                        data_row['destino'],
                        data_row['idDestino'],
                        data_row['noBoleta'],
                        data_row['user'],
                        data_row['horaInicio'],
                        data_row['llamado'],
                        data_row['kmRecorrido'],
                        multiplied_glns,
                        multiplied_km,
                        data_row['horaInicio'],
                        data_row['horaFin'],
                        data_row['boletaCaf'],
                        data_row['tipoServicio'],
                        galones,
                        depreciacion
                    ])
                    contador += 1
                    contador_registros += 1
                    sumatoria_glns += multiplied_glns
                    sumatoria_km += multiplied_km

                    galones = data_row.get('galones', '')
                    depreciacion = data_row.get('depreciacion', '')
                    retorno[-1].extend([galones, depreciacion])            

            return render(request, 'report/view_report.html',
                          {'resultados': retorno, 'usuarios': usuarios, 'galones': galones, 
                           'depreciacion': depreciacion, 'contador': contador_registros, 'sumatoria_glns': round(sumatoria_glns, 3),
                            'sumatoria_km': round(sumatoria_km, 3), 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})

    except Exception as e:
        return render(request, 'report/view_report.html', {'error': str(e)})

    return render(request, 'report/view_report.html', {'usuarios': usuarios, 'error': 'Método no permitido'})


def top_10(request):
    try:
        top_10_general_data = get_top_10()

        return render(request, 'report/top_10.html', {'top_10': top_10_general_data})

    except Exception as e:
        return render(request, 'report/top_10.html', {'error': str(e)})

def get_top_10():
    top_10_general_data = []

    all_data = firestore.client().collection('log').get()

    top_10_general_data = sorted(
        [
            row.to_dict()  # Obtén todos los datos de la fila
            for row in all_data
        ],
        key=lambda x: float(x['kmRecorrido'].split()[0]),
        reverse=True
    )[:10]

    # print(top_10_general_data)

    return top_10_general_data

# def convertir_a_datetime(fecha_hora_str):
#     formato = "%d/%m/%Y - %H:%M"
#     return datetime.strptime(fecha_hora_str, formato)

