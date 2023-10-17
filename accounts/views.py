import firebase_admin

import warnings
from firebase_admin import auth, firestore, db, credentials
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
import hashlib

warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud.firestore")
# firebase_admin.initialize_app()
# Create your views here.

def hash_password(password):
    # Utilizar hashlib para generar un hash de la contraseña
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        administrador = bool(request.POST.get('administrador', False))
        supervisor = bool(request.POST.get('supervisor', False))
        tecnico = bool(request.POST.get('tecnico', False))

        if not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'registration/signup.html')
        
        db = firestore.client()
        user_exists = db.collection('user').where('email', '==', email).limit(1).stream()

        if any(user_exists):
            messages.error(request, 'Correo electrónico ya registrado.')
            return render(request, 'registration/signup.html')

        # Crear un nuevo usuario en Firebase Authentication
        try:
            hashed_password = hash_password(password)
            user = auth.create_user(
                email=email,
                email_verified=False,
                password=password,
            )
            print(f'Datos del formulario: Email={email}, Password={password}, Admin={administrador}, Supervisor={supervisor}')
            link = auth.generate_email_verification_link(email)
            print(f'Enlace de verificación generado: {link}')
            
            # Crear un nuevo documento en Firebase Firestore            
            user_ref = db.collection('user').document(user.uid)
            user_ref.set({
                'email': email,
                'password': hashed_password,
                'administrador': administrador,
                'supervisor': supervisor,
                'tecnico': tecnico,
            })

            # User = get_user_model()
            # custom_user = User(email=email, username=email)
            # custom_user.set_password(password)
            # custom_user.save()
            # print(f'Usuario Django creado: {custom_user}')

            # auth.update_user(user.uid, email_verified=True)            
            messages.success(request, 'Usuario creado exitosamente.')
            print(f'Usuario creado exitosamente')
            return redirect('login')

        except Exception as e:
            # Manejar errores de autenticación
            messages.error(request, 'Error al crear el usuario. Inténtalo de nuevo más tarde.')
            return render(request, 'registration/signup.html')

    return render(request, 'registration/signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        print(f'Datos {email}, {password}, {role}')

        try:
            user_ref = firestore.client().collection('user').where('email', '==', email).limit(1)
            user = user_ref.get()

            if user:
                user_data = user[0].to_dict()

                hashed_password_input = hash_password(password)
               
                if user_data.get('password') == hashed_password_input:
                    print(f'Usuario logueado exitosamente')
                    messages.success(request, 'Usuario logueado exitosamente.')
                    request.session['email'] = user_data.get('email')
                    print(request.session['email'])
                    return redirect('view_report')
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            else:
                messages.error(request, 'Usuario no encontrado.')

        except Exception as e:
            print(f'Error: {e}')
            messages.error(request, 'Error al autenticar el usuario.')

    return render(request, 'registration/login.html')

def logout(request):
    try:
        # print(request.session['email'])        
        if 'email' in request.session:
            user = auth.get_user_by_email(request.session['email'])            
            
            auth.revoke_refresh_tokens(user.uid)
            
            del request.session['email']
            messages.success(request, 'Has cerrado sesión exitosamente.')
        else:
            messages.warning(request, 'No hay sesión activa.')
    except Exception as e:
        print(f'Error al cerrar sesión: {e}')
        messages.error(request, 'Error al cerrar sesión.')

    return redirect('login')

