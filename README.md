# Monitor Linux

Aplicação web para monitorar um sistema Linux em tempo real pelo navegador.

## O que faz

- Gráfico de uso de CPU e memória RAM em tempo real
- Visualização de uso por núcleo de CPU
- Listagem de processos com opção de finalizar
- Consultar, alterar permissões (`chmod`) e dono (`chown`) de arquivos

## Tecnologias

- **Backend:** Python 3 + Flask + psutil
- **Frontend:** HTML, CSS e JavaScript puro

## Estrutura

```
monitoramento-linux/
├── monitor.py   # classes que leem os dados do sistema (CPU, memória, processos, permissões)
├── app.py       # API Flask com as rotas HTTP
└── index.html   # interface web
```

## Como rodar

### 1. Clonar ou baixar os arquivos

Coloque os três arquivos (`monitor.py`, `app.py`, `index.html`) na mesma pasta.

### 2. Criar o ambiente virtual

```bash
cd ~/caminho/da/pasta
python3 -m venv .venv
```

### 3. Ativar o ambiente virtual

```bash
source .venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install flask flask-cors psutil
```

### 5. Rodar o projeto

Você vai precisar de **dois terminais abertos ao mesmo tempo**.

**Terminal 1 — backend:**
```bash
source .venv/bin/activate
python3 app.py
```

**Terminal 2 — frontend:**
```bash
python3 -m http.server 8080
```

### 6. Abrir no navegador

```
http://localhost:8080
```

## Observações

- O backend roda na porta `5000` e o frontend na porta `8080`
- Para encerrar, pressione `CTRL+C` em cada terminal
- Operações de `chmod` e `chown` exigem permissão sobre o arquivo alvo
