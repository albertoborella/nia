import uuid
from sqlmodel import Session, select, func

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.auth_service import hash_password
from app.utils.errors import NotFoundError, ConflictError, ValidationError


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Usuario:
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise NotFoundError("Usuario", str(user_id))
    return user


def list_users(db: Session, page: int = 1, limit: int = 20, rol: str | None = None) -> tuple[list[Usuario], int]:
    query = select(Usuario).where(Usuario.activo == True)
    count_query = select(func.count()).select_from(Usuario).where(Usuario.activo == True)

    if rol:
        query = query.where(Usuario.rol == rol)
        count_query = count_query.where(Usuario.rol == rol)

    total = db.exec(count_query).one()
    offset = (page - 1) * limit
    users = db.exec(query.offset(offset).limit(limit)).all()

    return list(users), total


def create_user(db: Session, data: UsuarioCreate) -> Usuario:
    if data.rol not in ("director", "colaborador"):
        raise ValidationError("VAL_ENUM_INVALID", "Role must be 'director' or 'colaborador'")

    existing = db.query(Usuario).filter(Usuario.email == data.email).first()
    if existing:
        raise ConflictError("Email already registered")

    user = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=data.rol,
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: uuid.UUID, data: UsuarioUpdate) -> Usuario:
    user = get_user_by_id(db, user_id)

    if data.email is not None and data.email != user.email:
        existing = db.query(Usuario).filter(Usuario.email == data.email).first()
        if existing:
            raise ConflictError("Email already registered")

    if data.rol is not None and data.rol not in ("director", "colaborador"):
        raise ValidationError("VAL_ENUM_INVALID", "Role must be 'director' or 'colaborador'")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user_id: uuid.UUID) -> None:
    user = get_user_by_id(db, user_id)
    temp_password = uuid.uuid4().hex[:12]
    user.password_hash = hash_password(temp_password)
    db.add(user)
    db.commit()
