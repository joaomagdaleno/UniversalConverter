# Universal Converter

O Universal Converter é uma aplicação de desktop para Windows, construída com PySide6 (Python), que permite a conversão de formatos de mídia.

A aplicação suporta a conversão de **imagens**, **áudio** e **vídeo**, com opções para controlar a qualidade, resolução e bitrate.

## 📝 Para Desenvolvedores

Esta seção descreve como configurar o ambiente de desenvolvimento para trabalhar no projeto.

### Pré-requisitos

-   Python 3.11 ou superior.
-   Git instalado e configurado.
-   **FFmpeg:** A aplicação depende do FFmpeg para as conversões de áudio e vídeo. Siga as instruções de instalação para o seu sistema. Para Windows, é recomendado baixar a versão "full build" do [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) e adicionar a pasta `bin` ao PATH do sistema.

### Configuração do Ambiente

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/joaomagdaleno/UniversalConverter.git
    cd UniversalConverter
    ```

2.  **Instale as Dependências:**
    É altamente recomendado usar um ambiente virtual (`venv`).
    ```bash
    # Crie e ative um ambiente virtual
    python -m venv .venv
    # No Windows (PowerShell): .\.venv\Scripts\Activate.ps1
    # No macOS/Linux: source .venv/bin/activate

    # Instale as dependências
    pip install -r requirements.txt
    ```

3.  **Execute a Aplicação:**
    Para iniciar a aplicação em modo de desenvolvimento, execute:
    ```bash
    python main_pyside.py
    ```

## 🚀 Como Lançar Novas Versões

O projeto está configurado com um workflow de GitHub Actions que automatiza o processo de build e release. A versão do aplicativo é determinada **diretamente pela tag do Git**.

Para lançar uma nova versão, siga os passos abaixo:

### Passo 1: Crie e Envie uma Tag do Git

O workflow de release é acionado pela criação de uma **tag** que começa com `v`.

1.  **Certifique-se de que seu branch principal está atualizado:**
    ```bash
    git checkout main
    git pull origin main
    ```

2.  **Crie a tag localmente:**
    O nome da tag se tornará a versão oficial. Use o formato `vX.Y.Z`.
    ```bash
    git tag v2.1.0
    ```

3.  **Envie a tag para o repositório remoto:**
    ```bash
    git push origin v2.1.0
    ```

### Passo 2: Verifique o Release no GitHub

Após enviar a tag, a GitHub Action será iniciada. O workflow irá automaticamente:
-   Atualizar o arquivo `VERSION.txt` com a versão da tag.
-   Empacotar a aplicação.
-   Criar uma nova "Release" na página do repositório, contendo um arquivo `.zip` com o programa.
