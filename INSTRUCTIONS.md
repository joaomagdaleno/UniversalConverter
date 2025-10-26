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

O projeto está configurado com um workflow de GitHub Actions que automatiza o processo de build e release. Para lançar uma nova versão, siga os passos abaixo.

### Passo 1: Atualize o Número da Versão

Abra o arquivo `VERSION.txt` e atualize o número da versão (ex: de `1.1.0` para `2.0.0`).

### Passo 2: Faça o Commit da Nova Versão

```bash
git add VERSION.txt
git commit -m "Bump version to 2.0.0"
git push
```

### Passo 3: Crie e Envie uma Tag do Git

O workflow de release é acionado pela criação de uma **tag** que começa com `v`.

1.  **Crie a tag localmente:** `git tag v2.0.0`
2.  **Envie a tag para o repositório remoto:** `git push origin v2.0.0`

### Passo 4: Verifique o Release no GitHub

Após enviar a tag, a GitHub Action será iniciada. Quando o processo terminar, uma nova "Release" será criada na página do repositório, contendo um arquivo `.zip` com o programa.
