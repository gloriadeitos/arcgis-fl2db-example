# 🇺🇸 UCM-ArcGISpythonDB

The purpose of this script is to update the database using the Feature Layer published on ArcGIS Online.

This update ensures that data remains synchronized and reflects the most recent information available on the platform.

## Development

To facilitate development and ensure code standardization, we recommend using Visual Studio Code (VS Code) with the following extensions:

1. **[Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)**: Provides support for Python development, including IntelliSense, debugging, and script execution.

2. **[autopep8](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8)**: Automates code formatting to follow PEP 8 standards.

3. Configure VS Code's `settings.json` to apply Autopep8 automatically on save:

   ```json
   {
     "python.formatting.provider": "autopep8",
     "editor.formatOnSave": true
   }
   ```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/CEPAG-UFPR/UCM-ArcGISpythonBD.git
   cd UCM-ArcGISpythonBD
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a file named `config.yaml` and configure it according to the template file `config_example.yaml`. Make sure to keep this file in the same directory as the `main.py` file.

5. Run the script:

   ```bash
   python src/main.py
   ```

## Notes

### Retrieving Stored Codes vs Displayed Labels

When using the following pattern:

```python
feature.attributes.get(""),
```

It retrieves the **stored code** of the domain, not the displayed label.

For example:

- Displayed label: "Batel" → Stored code: "CCBA"
- Displayed label: "Cabral" → Stored code: "CCBR"

To obtain the displayed label, use this pattern:

```python
fields_domains[""].get(feature.attributes.get("")),
```

**Note:** "Domain" in this context refers to the field domain in ArcGIS Online.

### Field Information

- Since each field can be associated with only one domain, it's important to note that in situations where there are fields like "campo", "sigla_campo", and "cod_campo", only "campo" and "sigla_campo" are linked to a domain.
- The "cod_campo" field, on the other hand, is treated as an independent field and does not have a direct association with a domain.

<br>

---

<br>

# 🇧🇷 UCM-ArcGISpythonBD

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
