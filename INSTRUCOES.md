# Instruções para Lançamento de Novas Versões (Automatizado)

Com a automação via GitHub Actions, o processo de lançar uma nova versão do seu aplicativo se tornou extremamente simples. Todo o trabalho manual de compilar o `.exe` e fazer upload foi eliminado.

### O Processo Automatizado

O fluxo de trabalho do GitHub Actions (`.github/workflows/release.yml`) está configurado para ser ativado sempre que uma nova **"tag"** de versão (ex: `v1.0.1`) é enviada para o repositório.

Quando isso acontece, um robô no GitHub irá:
1.  Criar uma máquina virtual segura com Windows.
2.  Baixar seu código-fonte.
3.  Instalar todas as dependências do `requirements.txt`.
4.  Compilar o `UniversalConverter.exe` usando o PyInstaller.
5.  Criar um `version.json` específico para o release, já com os links e notas da versão corretos.
6.  Criar uma nova "Release" na página do seu GitHub.
7.  Fazer o upload do `.exe` e do `version.json` para essa Release.

O seu aplicativo, ao verificar por atualizações, encontrará esses arquivos e se atualizará sozinho.

### Como Lançar uma Nova Versão

Seu único trabalho agora é dizer ao Git qual é a nova versão.

**Passo 1: Incremente a Versão Local**

*   Abra o arquivo `version.json` no seu projeto e aumente o número da versão (ex: de `"1.0.0"` para `"1.0.1"`).
*   Faça o commit desta pequena alteração:
    ```bash
    git add version.json
    git commit -m "Bump version to 1.0.1"
    ```

**Passo 2: Crie e Envie a "Tag"**

*   No seu terminal, use o comando `git tag` para criar uma tag com o **mesmo número de versão**, prefixado com `v`.
    ```bash
    git tag v1.0.1
    ```

*   Agora, envie seus commits e a nova tag para o GitHub:
    ```bash
    git push
    git push --tags
    ```

**E é isso!** Assim que você executar o `git push --tags`, o robô do GitHub Actions começará a trabalhar. Você pode ir para a aba "Actions" no seu repositório para assistir ao progresso. Em alguns minutos, a nova release aparecerá na seção "Releases" do seu GitHub, pronta para ser baixada pelos seus usuários.
