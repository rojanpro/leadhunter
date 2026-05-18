import os
import sys

from a2wsgi import ASGIMiddleware

ROOT = os.path.dirname(__file__)
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from app.db.seed import seed
from app.db.session import Base, engine
from app.main import app as fastapi_app
from app.models import entities  # noqa: F401

Base.metadata.create_all(bind=engine)
seed()

application = ASGIMiddleware(fastapi_app)
