import logging, os, uuid, asyncio, telnetlib3, re
from utils.support_functions import EnvironmentHelper

helper = EnvironmentHelper()

def create_rawcapture_file(nename: str):
    short_uuid = str(uuid.uuid4())[:8]
    timestamp = helper.get_current_date().strftime('%Y%m%d_%H%M%S')

    base_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "logs"))
    log_dir = os.path.join(base_dir, "huawei_equipment_log")

    os.makedirs(log_dir, exist_ok=True)
    raw_filename = f"huawei_{nename}_{short_uuid}_{timestamp}.rawcapture"

    return os.path.join(log_dir, raw_filename)

def setup_logger(name: str, path: str, level=logging.DEBUG, fmt: str = '%(asctime)s - %(message)s'):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.FileHandler(path)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)

    return logger

class TelnetClient:
    def __init__(self, host, port, login, password, ne_name):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.ne_name = ne_name
        self.reader = None
        self.writer = None

        self.prompt = b'---    END\r\n'
        self.prompt2 = b' reports in total\r\n---    END\r\n'

        self.raw_path = create_rawcapture_file(ne_name)
        self.cmd_logger = setup_logger('cmd_logger', self.raw_path)

    async def connect(self):
        try:
            logger.info(f"Conectando na gerencia...")
            self.reader, self.writer = await telnetlib3.open_connection(
                self.host, self.port, shell=None, encoding='utf8', connect_maxwait=60
            )
            await self._login()
            self.cmd_logger.info('Conexao com a gerencia Huawei MAE estabelecida com sucesso.')
        except Exception:
            self.cmd_logger.exception('Falha na tentativa de conexao.')
            raise

    async def disconnect(self):
        try:
            if self.writer:
                await self._logout()
                self.writer.close()
                self.cmd_logger.info('Desconectado da gerencia Huawei MAE.')
        except Exception:
            self.cmd_logger.exception('Falha na tentativa de desconectar.')
            raise

    async def _login(self):
        response = await self.send_command(f'LGI:OP="{self.login}",PWD="{self.password}";')
        if not response['success']:
            raise Exception('Login failed')

    async def _logout(self):
        await self.send_command(f'LGO:OP="{self.login}";')

    async def register_ne(self):
        result = await self.send_command(f'REG NE:NAME={self.ne_name};')
        if not result['success']:
            raise Exception(f'Failed to register NE: {self.ne_name}')

    async def unregister_ne(self):
        if not self.ne_name:
            return
        result = await self.send_command(f'UNREG NE:NAME={self.ne_name};')
        if not result['success']:
            raise Exception(f'Failed to unregister NE: {self.ne_name}')

    async def send_command(self, command: str):
        try:
            self.writer.write(command + "\r\n")
            response = await self.reader.readuntil(self.prompt)

            if b'To be continued...' in response:
                response += await self.reader.readuntil(self.prompt2)

            decoded = response.decode(errors='ignore').strip()
            self.cmd_logger.info(f">> {command}")
            self.cmd_logger.info(decoded)

            success = bool(re.search(r'RETCODE\s*=\s*0\s+Success', decoded, re.IGNORECASE))

            return {
                'success': success,
                'command': command,
                'response': decoded
            }
        except Exception as e:
            self.cmd_logger.error(f'[ERRO] Comando falhou: {command} | Erro: {e}')
            return {
                'success': False,
                'command': command,
                'response': str(e)
            }
