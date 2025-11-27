

from prisma import Prisma
from typing import Optional


class DatabaseConnection:

    
    _instance: Optional[Prisma] = None
    
    @classmethod
    async def get_instance(cls) -> Prisma:

        if cls._instance is None:
            cls._instance = Prisma()
            await cls._instance.connect()
        
        return cls._instance
    
    @classmethod
    async def disconnect(cls) -> None:

        if cls._instance is not None:
            await cls._instance.disconnect()
            cls._instance = None


async def get_db() -> Prisma:

    return await DatabaseConnection.get_instance()