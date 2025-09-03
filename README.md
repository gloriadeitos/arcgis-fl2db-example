# UCM-ArcGISpythonBD

O objetivo deste script é atualizar o banco de dados utilizando o Feature Layer publicado no ArcGIS Online.

Essa atualização garante que os dados estejam sincronizados e reflitam as informações mais recentes disponíveis na plataforma.

## Desenvolvimento

Para facilitar o desenvolvimento e garantir a padronização do código, recomendamos o uso do Visual Studio Code (VS Code) com as seguintes extensões:

1. **[Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)**: Fornece suporte ao desenvolvimento em Python, incluindo IntelliSense, depuração e execução de scripts.

2. **[autopep8](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8)**: Automatiza a formatação do código para seguir o padrão PEP 8.

3. Configure o `settings.json` do VS Code para aplicar o Autopep8 automaticamente ao salvar:

   ```json
   {
     "python.formatting.provider": "autopep8",
     "editor.formatOnSave": true
   }
   ```

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/CEPAG-UFPR/UCM-ArcGISpythonBD.git
   cd UCM-ArcGISpythonBD
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo chamado `config.yaml` e configure-o conforme o arquivo padrão `config_example.yaml`. Certifique-se de deixar este arquivo na mesma pasta do arquivo `main.py`.

5. Execute o script:

   ```bash
   python src/main.py
   ```

## Observações

### Recuperando Códigos Armazenados vs Labels Exibidos

Ao utilizar o seguinte padrão:

```python
feature.attributes.get(""),
```

Ele recupera o **código armazenado** do domínio, e não o rótulo exibido.

Por exemplo:

- Rótulo exibido: "Batel" → Código armazenado: "CCBA"
- Rótulo exibido: "Cabral" → Código armazenado: "CCBR"

Para obter o rótulo exibido, utilize este padrão:

```python
fields_domains[""].get(feature.attributes.get("")),
```

**Nota:** "domínio" neste contexto refere-se ao domínio do campo no ArcGIS Online.

### Informações sobre os campos

- Como cada campo pode estar associado a apenas um domínio, é importante observar que, em situações onde existem campos como "campo", "sigla_campo" e "cod_campo", somente "campo" e "sigla_campo" estão vinculados a um domínio.
- O campo "cod_campo", por sua vez, é tratado como um campo independente e não possui associação direta com um domínio.
