import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.config import settings
from app.database import create_db_and_tables, engine
from app.routers import auth, usuarios, boletines, notas, prompts, incidentes, auspiciantes, auditoria, health, dashboard
from app.services.auth_service import hash_password
from app.models.usuario import Usuario
from app.models.prompt import Prompt


DEFAULT_PROMPTS = [
    {
        "nombre": "Consulta Incidentes Mensual",
        "descripcion": "Busca incidentes de inocuidad alimentaria en un período dado. Retorna JSON estructurado para importar al sistema.",
        "template": (
            "Actúa como un investigador de seguridad alimentaria. "
            "Busca incidentes de inocuidad alimentaria ocurridos entre {{periodo_inicio}} y {{periodo_fin}}. "
            "Para cada incidente, devolvé un JSON con este formato exacto:\n\n"
            "[\n"
            "  {\n"
            '    "incidente": "Nombre del incidente",\n'
            '    "producto": "Producto afectado",\n'
            '    "patogeno": "Agente causal",\n'
            '    "organismo": "Empresa u organismo",\n'
            '    "pais": "País donde ocurrió",\n'
            '    "riesgo": "alto|medio|bajo",\n'
            '    "fecha_inicio": "YYYY-MM-DD",\n'
            '    "observaciones": "Detalles adicionales",\n'
            '    "fuente_url": "URL de la fuente",\n'
            '    "fuente_nombre": "Nombre del organismo fuente",\n'
            '    "severidad": "critico|alto|medio|bajo"\n'
            "  }\n"
            "]\n\n"
            "Importante: Solo devolvé el JSON, sin texto adicional. "
            "Incluí al menos 5 incidentes reales del período."
        ),
        "tipo": "consulta_incidentes",
        "configuracion": {"modelo": "gpt-4", "temperatura": 0.3, "max_tokens": 2000},
    },
    {
        "nombre": "Redacción Editorial",
        "descripcion": "Ayuda a redactar la editorial del boletín. Uso manual, la respuesta NO se guarda en el sistema.",
        "template": (
            "Sos editor de una publicación especializada en inocuidad alimentaria llamada "
            "'Noticias sobre Inocuidad Alimentaria'.\n\n"
            "Escribí una editorial para la edición de {{mes}} {{anio}} con las siguientes directrices:\n\n"
            "- Extensión: 300-500 palabras\n"
            "- Tono: profesional pero accesible\n"
            "- Tema central: {{tema_central}}\n"
            "- Incluí: al menos 2 eventos o tendencias relevantes del período\n"
            "- Cierre: invitar al lector a profundizar en las secciones del boletín\n\n"
            "Formato: Markdown con títulos y párrafos separados."
        ),
        "tipo": "otro",
        "configuracion": {"modelo": "gpt-4", "temperatura": 0.7, "max_tokens": 1500},
    },
    {
        "nombre": "Resumen Ejecutivo para Directorio",
        "descripcion": "Genera un resumen ejecutivo de incidentes para el directorio. Uso manual.",
        "template": (
            "Sos asesor de comunicación especializado en seguridad alimentaria.\n\n"
            "Generá un resumen ejecutivo de 200 palabras sobre los incidentes de "
            "inocuidad más relevantes del período {{periodo_inicio}} a {{periodo_fin}}.\n\n"
            "El resumen debe:\n"
            "- Destacar los 3-5 incidentes más críticos\n"
            "- Mencionar tendencias\n"
            "- Incluir recomendaciones breves\n"
            "- Tono ejecutivo, directo\n\n"
            "Formato: Texto plano"
        ),
        "tipo": "otro",
        "configuracion": {"modelo": "gpt-4", "temperatura": 0.5, "max_tokens": 800},
    },
    {
        "nombre": "Revisión de Normativa",
        "descripcion": "Analiza normativa alimentaria argentina. Uso manual.",
        "template": (
            "Sos experto en regulación alimentaria de Argentina.\n\n"
            "Analizá la siguiente normativa y explicá:\n"
            "{{normativa}}\n\n"
            "1. Objeto de la norma\n"
            "2. Alcance\n"
            "3. Requisitos principales\n"
            "4. Plazos de cumplimiento\n"
            "5. Sanciones por incumplimiento\n\n"
            "Formato: Markdown con secciones claras"
        ),
        "tipo": "otro",
        "configuracion": {"modelo": "gpt-4", "temperatura": 0.3, "max_tokens": 1500},
    },
    {
        "nombre": "Redacción de Artículos de Colaboradores",
        "descripcion": "Ayuda a redactar artículos para la sección de colaboradores. Uso manual.",
        "template": (
            "Sos editor de la publicación 'Noticias sobre Inocuidad Alimentaria'.\n\n"
            "Redactá un artículo de 800-1200 palabras sobre el siguiente tema:\n"
            "{{tema}}\n\n"
            "Estructura:\n"
            "1. Título atractivo\n"
            "2. Introducción con contexto\n"
            "3. Desarrollo con datos y fuentes\n"
            "4. Conclusiones\n"
            "5. Referencias\n\n"
            "Tono: profesional, técnico pero accesible para profesionales del sector alimentario.\n"
            "Formato: Markdown"
        ),
        "tipo": "otro",
        "configuracion": {"modelo": "gpt-4", "temperatura": 0.7, "max_tokens": 2500},
    },
]


def seed_default_director():
    with Session(engine) as db:
        existing = db.query(Usuario).filter(Usuario.email == "director@nia.com").first()
        if not existing:
            user = Usuario(
                nombre="Director",
                email="director@nia.com",
                password_hash=hash_password("Director123!"),
                rol="director",
                activo=True,
            )
            db.add(user)
            db.commit()


def seed_default_prompts():
    with Session(engine) as db:
        for prompt_data in DEFAULT_PROMPTS:
            existing = db.query(Prompt).filter(Prompt.nombre == prompt_data["nombre"]).first()
            if not existing:
                prompt = Prompt(
                    nombre=prompt_data["nombre"],
                    descripcion=prompt_data["descripcion"],
                    template=prompt_data["template"],
                    tipo=prompt_data["tipo"],
                    activo=True,
                    configuracion=prompt_data["configuracion"],
                )
                db.add(prompt)
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("NIA_TESTING"):
        create_db_and_tables()
        seed_default_director()
        seed_default_prompts()
    yield


app = FastAPI(
    title="NIA API",
    description="Noticias Inocuidad Alimentaria - Editorial Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if hasattr(exc, "detail") and isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=getattr(exc, "status_code", 500),
            content={"detail": exc.detail},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": {"code": "SYS_INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(boletines.router)
app.include_router(notas.router)
app.include_router(prompts.router)
app.include_router(incidentes.router)
app.include_router(auspiciantes.router)
app.include_router(auditoria.router)
app.include_router(health.router)
app.include_router(dashboard.router)
