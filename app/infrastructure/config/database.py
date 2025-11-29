
from prisma import Prisma
from typing import Optional
import logging

logger = logging.getLogger(__name__)



_prisma_client: Optional[Prisma] = None


def get_prisma_client() -> Prisma:

    global _prisma_client
    
    if _prisma_client is None:
        raise RuntimeError(
            "Prisma client not initialized. "
            "Call initialize_database() during application startup."
        )
    
    return _prisma_client


async def initialize_database() -> None:

    global _prisma_client
    
    try:
        logger.info("Iniciando Prisma client...")
        
        _prisma_client = Prisma()
        
        await _prisma_client.connect()
        
        logger.info(" DB conectado exitosamente")
        
    except Exception as e:
        logger.error(f" Error al conectar a la base de datos: {str(e)}")
        raise


async def close_database() -> None:

    global _prisma_client
    
    if _prisma_client is not None:
        try:
            logger.info("Cerrando conexión a la base de datos...")
            await _prisma_client.disconnect()
            _prisma_client = None
            logger.info("Conexión a la base de datos cerrada exitosamente")
            
        except Exception as e:
            logger.error(f"Error al cerrar la base de datos: {str(e)}")



async def check_database_health() -> dict:

    try:
        prisma = get_prisma_client()
        
        await prisma.execute_raw("SELECT 1")
        
        return {
            "status": "healthy",
            "connected": prisma.is_connected()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
        }




async def execute_in_transaction(callback):

    prisma = get_prisma_client()
    
    async with prisma.tx() as transaction:
        return await callback(transaction)