# Como Executar o Projeto no Visual Studio

Este guia descreve os passos necessários para compilar e executar a aplicação `UniversalConverter` em um ambiente de desenvolvimento usando o Visual Studio 2022.

## Pré-requisitos

- **Visual Studio 2022:** Certifique-se de ter o Visual Studio instalado.
- **Carga de Trabalho de Desenvolvimento para UWP:** Durante a instalação do Visual Studio, é necessário ter selecionado a carga de trabalho "Desenvolvimento para Plataforma Universal do Windows".
- **SDK do Windows 11:** Instale o SDK do Windows 11 (versão 10.0.22621.0 ou superior).

## Passos para Executar

1.  **Abrir a Solução:**
    -   Abra o Visual Studio.
    -   Vá em `File > Open > Project/Solution` (ou `Arquivo > Abrir > Projeto/Solução`).
    -   Navegue até a pasta do projeto e selecione o arquivo `UniversalConverter.sln`.

2.  **Definir o Projeto de Inicialização:**
    -   A solução contém dois projetos: `UniversalConverter` (o código da aplicação) e `UniversalConverter.Packager` (o projeto de empacotamento).
    -   Para executar o aplicativo em modo de depuração, o projeto de empacotamento deve ser definido como o projeto de inicialização.
    -   No **Solution Explorer** (Gerenciador de Soluções), clique com o botão direito do mouse no projeto **`UniversalConverter.Packager`**.
    -   No menu de contexto, selecione **"Set as Startup Project"** (Definir como Projeto de Inicialização).

3.  **Selecionar a Arquitetura Correta:**
    -   Na barra de ferramentas superior do Visual Studio, certifique-se de que a arquitetura da solução (por exemplo, `x64` ou `x86`) corresponde à do seu sistema. `x64` é a escolha mais comum.

4.  **Executar o Projeto:**
    -   Pressione a tecla **F5** ou clique no botão verde de "Play" com o nome `UniversalConverter.Packager` na barra de ferramentas.
    -   O Visual Studio irá compilar ambos os projetos, criar um pacote de instalação de teste, assiná-lo com um certificado temporário e instalar/executar o aplicativo no seu computador.

Na primeira vez que você executar, o Windows pode solicitar a instalação do certificado de teste. Se isso acontecer, aceite para permitir que o aplicativo seja instalado.