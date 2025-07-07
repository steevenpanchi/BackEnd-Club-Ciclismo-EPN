import pytz
from fastapi import APIRouter, BackgroundTasks
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import *
from app.crud.persona import update_persona
from app.crud.token import create_token, verify_token
from app.crud.user import get_user_id_by_email, create_user
from app.db.session import get_db
from app.models.domain.token import AuthToken
from app.models.domain.user import User, Role
from app.models.schema.persona import PersonaResponse, PersonaUpdate
from app.models.schema.user import UserCreate, UserResponse, UserWithPersonaResponse, UserUpdate, Token, TokenData
from app.services.crypt import verify_password
from app.services.email_service import send_email
from app.services.multi_crud_service import reset_password
from app.services.verify import verify_structure_password

router = APIRouter()

ALL_AUTH_ROLES = [Role.ADMIN, Role.NORMAL]


@router.post("/register", response_model=UserResponse)
def register_user(register_data: UserCreate,
                  db: Session = Depends(get_db),
                  ):
    """
    Create a new User / Crear un nuevo Usuario

    English:
    --------
    - **email** (required): Valid email address.
    - **password** (required): Must contain:
        - At least one uppercase letter.
        - At least one number.
        - Minimum 8 characters.
        - At least one special character.
    - **role** (optional): User role. Defaults to:
        - **Normal**
        - Other valid value: **Admin**
    - **persona** (required): Personal information:
        - **first_name**: First name.
        - **last_name**: Last name.
        - **phone_number**: Unique phone number (7 to 10 digits).
        - **city**: City of residence.
        - **neighborhood**: Neighborhood.
        - **blood_type**: Blood type (e.g. O+, A-, etc).
        - **skill_level** (required): Skill level in cycling. Must be one of the following:
            - **High**: High skill level.
            - **Medium**: Medium skill level.
            - **Low**: Low skill level.
        - **profile_picture** (optional): Profile image. Defaults to null.

    Español:
    --------
    - **email** (requerido): Dirección de correo electrónico válida.
    - **password** (requerido): Debe contener:
        - Al menos una letra mayúscula.
        - Al menos un número.
        - Mínimo 8 caracteres.
        - Al menos un carácter especial.
    - **role** (opcional): Rol del usuario. Por defecto:
        - **Normal**
        - Otro valor válido: **Admin**
    - **persona** (requerido): Información personal:
        - **first_name**: Nombre.
        - **last_name**: Apellido.
        - **phone_number**: Número de teléfono único (7 a 10 dígitos).
        - **city**: Ciudad de residencia.
        - **neighborhood**: Barrio.
        - **blood_type**: Tipo de sangre (ej. O+, A-, etc).
        - **skill_level** (requerido): Nivel de habilidad en ciclismo. Debe ser uno de los siguientes:
            - **Alto**: Nivel de habilidad alto.
            - **Medio**: Nivel de habilidad medio.
            - **Bajo**: Nivel de habilidad bajo.
        - **profile_picture** (opcional): Imagen de perfil. Valor por defecto es null.
    """

    new_user = create_user(db, register_data)

    return new_user


@router.post("/token", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    English:
    --------
    Login for Access Token:

    - **email** (required): Email to login.
    - **password** (required): Password of the user.

    Español:
    --------
    Iniciar sesión para obtener un token de acceso:

    - **email** (requerido): Correo electrónico del usuario.
    - **password** (requerido): Contraseña del usuario.
    """

    user = get_user(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/reset_password/send')
async def send_reset_password_code(
        background_tasks: BackgroundTasks,
        email: EmailStr = Form(...),
        db: Session = Depends(get_db)
):
    """
    English:
    --------
    Send recovery password email:

    - **email** (required): Email of an existing user.

    Español:
    --------
    Enviar un correo electrónico para la recuperación de contraseña:

    - **email** (required): Correo electrónico de un usuario existente.
    """
    subject = 'Recuperación de contraseña'

    try:
        # Obtener el ID del usuario por su email
        user_id = get_user_id_by_email(db, email)

        if not user_id:
            # No revelamos si el email existe por seguridad
            return {"message": "El código fue enviado exitosamente."}

        # Generar y guardar el token
        reset_token = AuthToken()
        reset_token.generate_token(user_id)

        if not create_token(db, reset_token):
            raise HTTPException(status_code=500, detail="No se pudo generar el token de recuperación.")

        # Configurar la zona horaria para la fecha de expiración
        ecuador_tz = pytz.timezone("America/Guayaquil")
        expiration_time = reset_token.date_expiration.replace(tzinfo=pytz.utc).astimezone(ecuador_tz)

        # Crear el contexto del email
        context = {
            "body": {
                "title": "Club de Ciclismo EPN",
                "code": reset_token.value,
                "date": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }

        # Enviar el email en segundo plano
        background_tasks.add_task(send_email, email, subject, context, "email.html")

        return {"message": "El código fue enviado exitosamente."}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor.")





@router.post('/reset_password/verify', response_model=dict)
async def verify_password_code(
        code: int,
        db: Session = Depends(get_db)
):
    """
           English:
           --------
           Verify recovery password code:

           - **code** (required): Code sent.

           Español:
           --------
            Verificar código de recuperación de contraseña:

           - **code** (required): Código enviado.
    """
    is_verified, id_user = verify_token(db, code)
    if is_verified and is_verified is not None:
        return {'is_valid': True, 'message': 'Código valido'}
    if not is_verified and is_verified is not None:
        raise HTTPException(status_code=410, detail="Código expirado")
    raise HTTPException(status_code=400, detail="Código invalido")


@router.post('/reset_password/reset', response_model=dict)
async def reset_forgotten_password(
        code: int,
        new_password: str,
        db: Session = Depends(get_db)):
    """
           English:
           --------
           Reset password with a verify code:

           - **code** (required): Code sent.
           - **password** (required): New password with:
                - One Letter in UpperCase
                - One Number
                - 8 character length
                - One Special character

           Español:
           --------
            Resetear la contraseña con un código de recuperación:

           - **code** (required): Código enviado.
           - **new_password** (required): Nueva contraseña con:
                - Una letra en mayúscula
                - Un número
                - Longitud de 8 caracteres
                - Un caracter especial
        """
    if not verify_structure_password(new_password):
        raise HTTPException(status_code=400, detail="La contraseña debe contener almenos una letra y un numero")
    return reset_password(db, code, new_password)


@router.delete("/delete/{user_id}", response_model=UserResponse)
def delete_user_and_persona(user_id: int, db: Session = Depends(get_db),
                            current_user: TokenData = Depends(get_current_user)

                            ):
    """
           English:
           --------
           Delete user by id:

           - **user_id** (required): User id to be eliminated.

           Español:
           --------
            Eliminar usuario por su id:

           - **user_id** (required): Id de usuario a ser eliminado.
    """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:

        # Buscar el usuario por su ID
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Obtener la persona asociada al usuario
        persona = user.person

        # Eliminar el usuario
        db.delete(user)
        db.commit()

        # Eliminar la persona
        if persona:
            db.delete(persona)
            db.commit()  # Confirmar la eliminación de la persona

        return user  # Retornar el usuario que fue eliminado

    except SQLAlchemyError as e:
        db.rollback()  # En caso de error, deshacer los cambios
        raise HTTPException(status_code=500, detail="Error al eliminar el usuario y la persona")


@router.get("/users", response_model=list[UserWithPersonaResponse])
def get_users(db: Session = Depends(get_db),
              current_user: TokenData = Depends(get_current_user)
              ):
    """
    Get all registered users with their roles and associated personal information.

    English:
    --------
    Returns a list of all registered users, including their roles and associated personal data.

    Español:
    --------
    Obtiene una lista de todos los usuarios registrados, incluyendo su rol y la información personal asociada.
    """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Consultar todos los usuarios con la persona asociada
        users = db.query(User).all()

        if not users:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios")

        # Mapear la respuesta para incluir el rol y la persona
        user_responses = [
            UserWithPersonaResponse.from_orm_custom(user)
            for user in users
        ]

        return user_responses  # Devolvemos la lista de usuarios con la persona y el rol

    except Exception as e:
        # Agregar más detalles sobre el error
        print(f"Error al obtener los usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener los usuarios: {str(e)}")


@router.get("/my_profile", response_model=PersonaResponse)
def get_my_profile(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    """
    Obtener el perfil del usuario autenticado, solo con la información personal (persona).
    """
    try:
        if not current_user.person:
            raise HTTPException(status_code=404, detail="No se encontró información de persona asociada")

        return PersonaResponse.from_orm(current_user.person)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el perfil: {str(e)}")

@router.put("/update/basic_information/{persona_id}", response_model=PersonaResponse)
def update_basic_info(persona_id: int, persona_update: PersonaUpdate, db: Session = Depends(get_db),
                      current_user: TokenData = Depends(get_current_user)
                      ):
    """
    Update a person's information / Actualizar información de una persona

    English:
    --------
    Update the fields of a person's profile. All fields are optional and only the provided ones will be updated.

    - **first_name** (optional): First name of the person.
    - **last_name** (optional): Last name of the person.
    - **phone_number** (optional): Cellphone number (7 to 10 digits).
    - **city** (optional): City of residence.
    - **neighborhood** (optional): Neighborhood or zone.
    - **blood_type** (optional): Blood type (e.g., A+, O-).
    - **skill_level** (required): Skill level in cycling. Must be one of the following:
        - **High**: High skill level.
        - **Medium**: Medium skill level.
        - **Low**: Low skill level.
    - **profile_picture** (optional): Image of the user (PNG or JPEG). Maximum allowed size: 2 MB.

    Español:
    --------
    Actualiza los campos del perfil de una persona. Todos los campos son opcionales y solo se actualizarán los proporcionados.

    - **first_name** (opcional): Nombres de la persona.
    - **last_name** (opcional): Apellidos de la persona.
    - **phone_number** (opcional): Número de celular (7 a 10 dígitos).
    - **city** (opcional): Ciudad de residencia.
    - **neighborhood** (opcional): Barrio o zona.
    - **blood_type** (opcional): Tipo de sangre (ej. A+, O-).
    - **skill_level** (requerido): Nivel de habilidad en ciclismo. Debe ser uno de los siguientes:
        - **Alto**: Nivel de habilidad alto.
        - **Medio**: Nivel de habilidad medio.
        - **Bajo**: Nivel de habilidad bajo.
    - **profile_picture** (opcional): Imagen del usuario (PNG o JPEG). Tamaño máximo permitido: 2 MB.
    """
    if current_user.role.value not in ALL_AUTH_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Actualizar la persona utilizando la función definida
        updated_persona = update_persona(db, persona_id, persona_update)

        # Devolver la persona actualizada
        return PersonaResponse.from_orm(updated_persona)

    except Exception as e:
        # Agregar más detalles sobre el error
        print(f"Error al actualizar la información básica de la persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar la información básica: {str(e)}")


@router.put("/update/role/{user_id}", response_model=UserResponse)
def update_user_role(user_id: int, user_update: UserUpdate,
                     db: Session = Depends(get_db),
                     current_user: TokenData = Depends(get_current_user)
                     ):
    """
    Update a User's Role / Actualizar el Rol de un Usuario

    English:
    --------
    Update the role of a user by their ID.

    - **role** (required): New role to assign. Must be one of:
        - **Admin**: Administrator with full access.
        - **Normal**: Regular user with limited permissions.

    Español:
    --------
    Actualiza el rol de un usuario mediante su ID.

    - **role** (requerido): Nuevo rol a asignar. Debe ser uno de:
        - **Admin**: Administrador con acceso total.
        - **Normal**: Usuario regular con permisos limitados.
    """
    if current_user.role.value not in [Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        # Consultar el usuario por su id
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Verificar si se proporcionó un nuevo rol
        if user_update.role:
            user.role = user_update.role

        # Guardar los cambios en la base de datos
        db.commit()
        db.refresh(user)

        # Devolver la respuesta con el usuario actualizado
        return UserResponse.from_orm_custom(user)
    except Exception as e:
        print(f"Error al actualizar el rol del usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar el rol: {str(e)}")