# Universal Converter

O Universal Converter é uma aplicação de desktop para Windows, construída com Flet (Python), que permite a conversão de formatos de mídia. Atualmente, a aplicação suporta a conversão entre os formatos WebP e GIF.

A aplicação conta com um sistema de atualização automática que notifica o usuário sobre novas versões e permite a instalação de forma simples e direta.

## 📝 Para Desenvolvedores

Esta seção descreve como configurar o ambiente de desenvolvimento para trabalhar no projeto.

### Pré-requisitos

-   Python 3.11 ou superior.
-   Git instalado e configurado.

### Configuração do Ambiente

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/joaomagdaleno/UniversalConverter.git
    cd UniversalConverter
    ```

2.  **Instale as Dependências:**
    É altamente recomendado usar um ambiente virtual (`venv`) para isolar as dependências do projeto.
    ```bash
    # Crie um ambiente virtual (opcional, mas recomendado)
    python -m venv .venv

    # Ative o ambiente virtual
    # No Windows (PowerShell):
    . \.venv\Scripts\Activate.ps1
    # No macOS/Linux:
    # source .venv/bin/activate

    # Instale as dependências do projeto
    pip install -r requirements.txt
    ```

3.  **Execute a Aplicação:**
    Para iniciar a aplicação em modo de desenvolvimento, execute o seguinte comando no terminal:
    ```bash
    python main.py
    ```

## 🚀 Como Lançar Novas Versões

O projeto está configurado com um workflow de GitHub Actions que automatiza o processo de build e release. Para lançar uma nova versão, siga os passos abaixo.

### Passo 1: Atualize o Número da Versão

Abra o arquivo `VERSION.txt` na raiz do projeto e atualize o número da versão seguindo o padrão de [Versionamento Semântico](https://semver.org/lang/pt-BR/) (ex: de `1.0.0` para `1.0.1` ou `1.1.0`).

### Passo 2: Faça o Commit da Nova Versão

Salve a alteração no `VERSION.txt` e faça o commit para o seu branch principal.
```bash
git add VERSION.txt
git commit -m "Bump version to 1.0.1"
git push
```

### Passo 3: Crie e Envie uma Tag do Git

O workflow de release é acionado pela criação de uma **tag** que começa com `v`. A tag deve corresponder à versão definida no `VERSION.txt`.

1.  **Crie a tag localmente:**
    ```bash
    # Exemplo para a versão 1.0.1
    git tag v1.0.1
    ```

2.  **Envie a tag para o repositório remoto:**
    ```bash
    # Exemplo para a versão 1.0.1
    git push origin v1.0.1
    ```

### Passo 4: Verifique o Release no GitHub

Após enviar a tag, a GitHub Action será iniciada automaticamente. Você pode acompanhar o progresso na aba "Actions" do seu repositório.

Quando o processo terminar (geralmente em alguns minutos), uma nova "Release" será criada na página do seu repositório. Esta release conterá um arquivo `.zip` com o programa.

## 👨‍💻 Para Usuários Finais

-   **Instalação:** O arquivo `.zip` da versão mais recente pode ser encontrado na seção de [Releases](https://github.com/joaomagdaleno/UniversalConverter/releases) do repositório no GitHub. Baixe e descompacte o arquivo, e execute `UniversalConverter.exe` para iniciar o programa.
-   **Atualizações:** A aplicação verifica automaticamente se há novas versões ao ser iniciada. Se uma atualização for encontrada, ela será baixada e extraída em segundo plano. Uma notificação aparecerá perguntando se você deseja fechar o aplicativo atual e iniciar a nova versão.
