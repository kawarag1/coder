from chainlit.data import BaseDataLayer
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.coder.database.database import get_session

class SQLAlchemyDataLayer(BaseDataLayer):
    def __init__(self, session: AsyncSession):
        self.session = session;

    