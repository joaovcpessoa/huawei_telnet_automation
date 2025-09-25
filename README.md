# SSH AUTOMATION

## Objetivo

Fornecer uma automação robusta para gerenciamento remoto de dispositivos Huawei via SSH, permitindo execução controlada de comandos, extração de informações operacionais e centralização de logs para análise.

## Requisitos funcionais

1. Autenticação e Sessões
- Suportar autenticação por chave pública/privada e usuário/senha.
- Reuso de conexões (connection pooling) e limite configurável de sessões concorrentes.

2. Execução de Comandos
- Execução síncrona e assíncrona de comandos.
- Timeout por comando e políticas de retry com backoff.

3. Opção para comandos condicionais (ex.: executar X somente se saída de Y contiver Z).
- Coleta e Processamento de Logs
- Captura de stdout/stderr de cada comando.

4. Parsers configuráveis para transformar saídas em estruturas (JSON/CSV/DB).
- Extração de campos: timestamp, nível, código de evento, descrição, interface, etc.

5. Armazenamento e Integração
- Persistência em banco relacional/NoSQL ou exportação para arquivos (CSV/JSON).
- Integração opcional com sistemas de logging/observability (ex.: ELK, Prometheus, SIEM).

6. Observabilidade e Auditoria
- Logs de auditoria com usuário, comando executado, target, horário e resultado.
- Métricas operacionais exportáveis (taxa de sucesso, latência média, falhas por host).

7. Resiliência e Segurança
- Criptografia de credenciais em repouso.
- Tratamento de exceções e fallback em caso de indisponibilidade.
- Rate limiting para evitar sobrecarga das gerências.

8. Operação e Configuração
- Arquivo de configuração central (hosts, credenciais, comandos, schedule).
- Modo de execução manual e por agendamento (cron-like).
- Modo verbose/debug para troubleshooting.

Entregáveis esperados:
- Código-fonte bem documentado e testado.
- Documentação de configuração e operação.
- Scripts de deploy e instruções para integração com o repositório de logs.
