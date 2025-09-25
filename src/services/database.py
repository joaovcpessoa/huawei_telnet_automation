import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, text
from infraestructure.set_log_system import logger

class DatabaseManager:
    def __init__(self, env_file_path=None):
        dotenv_path = env_file_path or os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)

    def get_connection_string(self, db_key: str) -> str:
        try:
            prefix = db_key.upper()

            driver = os.getenv(f'DB_DRIVER_{prefix}')
            user = os.getenv(f'DB_USER_{prefix}')
            password = quote_plus(os.getenv(f'DB_PASSWORD_{prefix}', ''))
            host = os.getenv(f'DB_HOST_{prefix}')
            port = os.getenv(f'DB_PORT_{prefix}')
            dbname = os.getenv(f'DB_NAME_{prefix}')

            if not all([driver, user, password, host, port, dbname]):
                raise ValueError(f'Parâmetros ausentes para o banco: {prefix}')

            return f'{driver}://{user}:{password}@{host}:{port}/{dbname}'

        except Exception as e:
            logger.error(f'Erro ao montar a connection string para o banco {prefix}: {e}')
            raise

    def execute_query(self, query, db_key: str, params=None):
        try:
            logger.info(f'Iniciando execução de query no banco [{db_key.upper()}].')
            conn_str = self.get_connection_string(db_key)
            engine = create_engine(conn_str)

            with engine.begin() as conn:
                result = conn.execute(query, params or {})

                if result.returns_rows:
                    rows = result.mappings().all()
                    logger.info(f'{len(rows)} linha(s) retornada(s).')
                    return rows
                else:
                    logger.info('Query executada com sucesso. Nenhuma linha retornada.')
                    return None

        except SQLAlchemyError as e:
            logger.error(f'Erro SQLAlchemy: {e}')
            raise
        except Exception as e:
            logger.error(f'Erro inesperado ao executar query no banco [{db_key}]: {e}')
            raise

