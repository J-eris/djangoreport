from django.shortcuts import render, redirect
from firebase_admin import firestore, auth
from django.http import JsonResponse
import datetime
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
            date_start_search = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            date_end_search = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')

            config_data = firestore.client().collection('configuracion').get()
            data = firestore.client().collection('log').get()

            contador = 1
            contador_registros = 0

            for row in data:
                data_row = row.to_dict()

                if usuario != '[TODOS]' and usuario.lower() != data_row['user'].lower():
                    continue

                date_start_row = datetime.datetime.strptime(data_row['horaInicio'], '%d/%m/%Y - %H:%M')
                date_end_row = datetime.datetime.strptime(data_row['horaFin'], '%d/%m/%Y - %H:%M')

                inserta_info = date_start_row >= date_start_search and date_end_row <= date_end_search

                for config_row in config_data:
                    config_row_data = config_row.to_dict()
                    galones = config_row_data.get('galones', '')
                    depreciacion = config_row_data.get('depreciacion', '')

                if inserta_info:
                    retorno.append([
                        contador,
                        data_row['user'],
                        data_row['llamado'],
                        data_row['destino'],
                        data_row['horaInicio'],
                        data_row['horaFin'],
                        data_row['kmRecorrido'],
                        galones,
                        depreciacion
                    ])
                    contador += 1
                    contador_registros += 1

                    galones = data_row.get('galones', '')
                    depreciacion = data_row.get('depreciacion', '')
                    retorno[-1].extend([galones, depreciacion])

            return render(request, 'report/view_report.html',
                          {'resultados': retorno, 'usuarios': usuarios, 'galones': galones, 'depreciacion': depreciacion, 'contador': contador_registros})

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
            {'user': row.to_dict()['user'], 'kmRecorrido': float(row.to_dict()['kmRecorrido'].split()[0])}
            for row in all_data
        ],
        key=lambda x: x['kmRecorrido'],
        reverse=True
    )[:10]

    # print(top_10_general_data)

    return top_10_general_data

