__version__ = "1.0.0"

from .database import init_db, get_db
from .config import settings

__all__ = [
    'init_db',
    'get_db',
    'settings',
    '__version__'
]