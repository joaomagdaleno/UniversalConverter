# Instruções para Hospedagem e Gerenciamento de Atualizações

Para que o sistema de atualização automática funcione, você precisa de um lugar online para hospedar a versão mais recente do seu aplicativo e um arquivo `version.json` que informa ao programa qual é essa versão. O **GitHub Releases** é perfeito e gratuito para isso.

Siga este passo a passo sempre que quiser lançar uma nova versão.

### Passo 1: Preparar os Arquivos para Lançamento

1.  **Incremente a Versão:** Antes de tudo, abra o arquivo `version.json` no seu projeto e aumente o número da versão (ex: de `"1.0.0"` para `"1.0.1"`).

2.  **Gere o `.exe`:** Use o PyInstaller para criar o executável da nova versão. O comando recomendado é:
    ```bash
    pyinstaller --onefile --windowed --name UniversalConverter main.py
    ```
    *   Você encontrará o `UniversalConverter.exe` dentro da pasta `dist/`.

3.  **Crie o `version.json` para o Release:** Crie uma cópia do seu `version.json` local. Edite esta **cópia** e adicione duas novas chaves: `url` e `release_notes`. O arquivo final para upload deve se parecer com isto:
    ```json
    {
        "version": "1.0.1",
        "url": "LINK_PARA_SEU_EXE_AQUI",
        "release_notes": "Corrigido bug X.\nAdicionada funcionalidade Y."
    }
    ```
    *   Deixe o `url` como um placeholder por enquanto.

### Passo 2: Criar uma Nova "Release" no GitHub

1.  **Vá para seu Repositório:** Abra a página do seu projeto no GitHub.
2.  **Encontre a Seção "Releases":** Na barra lateral direita, clique em "Releases".
3.  **Crie uma Nova Release:** Clique em "Draft a new release".
4.  **Defina a Tag da Versão:** No campo "Tag version", digite a mesma versão que você colocou no `version.json` (ex: `v1.0.1`). Clique em "Create new tag".
5.  **Dê um Título:** Um bom título é "Versão 1.0.1".
6.  **Anexe os Arquivos:** Na seção "Attach binaries by dropping them here or selecting them", arraste e solte **dois** arquivos:
    *   O `UniversalConverter.exe` que você gerou.
    *   O `version.json` **modificado** (aquele com as notas da versão).
7.  **Publique a Release:** Clique em "Publish release".

### Passo 3: Obter e Atualizar os Links

1.  **Copie os Links:** Após publicar, você verá os arquivos que anexou na sua página de release. Clique com o botão direito em cada um deles (`UniversalConverter.exe` e `version.json`) e selecione "Copiar endereço do link".

2.  **Atualize o `version.json` Online:**
    *   Volte para a edição da sua release no GitHub.
    *   Edite o `version.json` que você subiu. Cole o link que você copiou do `UniversalConverter.exe` no campo `"url"`. Salve as alterações.

3.  **Atualize o `config.json` Local:**
    *   Abra o arquivo `config.json` no seu projeto.
    *   Cole o link que você copiou do `version.json` online no campo `"config_url"`.
    *   **IMPORTANTE:** O link do GitHub pode ter `/tag/` no meio. Você precisa mudá-lo para que aponte para `latest/download` para que ele sempre pegue a última versão.
        *   **Exemplo de link copiado:** `https://github.com/SEU_USUARIO/SEU_REPO/releases/download/v1.0.1/version.json`
        *   **Como deve ficar no `config.json`:** `https://github.com/SEU_USUARIO/SEU_REPO/releases/latest/download/version.json`

Pronto! Na próxima vez que alguém abrir uma versão antiga do seu aplicativo, ele encontrará a nova versão, fará o download e se atualizará.
