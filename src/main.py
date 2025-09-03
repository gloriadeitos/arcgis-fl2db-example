#!.\env\Scripts\python
from arcgis.gis import GIS
from arcgis.features.layer import Geometry
from psycopg2 import connect
from psycopg2.extensions import connection
from datetime import datetime
from yaml import safe_load
import logging


def init_config():
    """
    Initializes configuration.
    """

    with open("./config.yaml") as f:
        config = safe_load(f.read())

    return config


def init_logging(log_filename):
    """
    Initializes log.
    """

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8',
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))

    logging.getLogger().addHandler(console_handler)


def get_gis_data(gis_config, day_interval):
    """
    Gets data from AGOL.
    """

    # AGOL connection
    gis: GIS = GIS(
        url=gis_config["url"],
        username=gis_config["user"],
        password=gis_config["password"]
    )

    # retrieve feature layer
    feature_layer = gis.content.get(gis_config["feature_layer"]).layers[0]

    # query all globalids (for deletion verification)

    all_globalids = {}

    all_features = feature_layer.query(
        where="andar IS NOT NULL and local IS NOT NULL",
        return_geometry=False,
        out_fields="local,andar,GlobalID").features
    for feature in all_features:
        globalid = f'{{{feature.attributes["GlobalID"].upper()}}}'

        table_schema_key = create_table_schema_key(
            feature.attributes["local"], feature.attributes["andar"])

        if table_schema_key not in all_globalids:
            all_globalids[table_schema_key] = []

        all_globalids[table_schema_key].append(globalid)

    # query recent features in the last {day_interval} days
    recent_features = feature_layer.query(
        where=f"EditDate >= CURRENT_TIMESTAMP - INTERVAL '{day_interval}' DAY",
        return_geometry=True,
        return_z=True,
        out_sr=31982).features

    # get field domain values
    fields_domains = {}
    for field in feature_layer.properties.fields:
        if "domain" in field and field["domain"]:
            field_name = field["name"]
            fields_domains[field_name] = {}
            for field_domain in field["domain"]["codedValues"]:
                fields_domains[field_name][field_domain["code"]
                                           ] = field_domain["name"]

    return all_globalids, recent_features, fields_domains


def get_db_connection(database_config):
    """
    Initializes database connection.
    """

    conn: connection = connect(
        **database_config,
        options="-c client_encoding=UTF8"
    )

    return conn


def create_table_schema_key(campi_id, floor):
    """
    Generates table schema key (schema_name.table_name).
    """

    schema_name = campi_id.lower()
    table_name = f"{schema_name}_andar_%s" % (
        "subsolo" if floor == -1 else floor)
    return f'{schema_name}.{table_name}'


def update_insert_features(db_cursor, recent_features, fields_domains):
    """
    Updates or inserts features into the database.
    """

    # sector mapping
    sector_mapping = {
        "AC": 1,
        "AG": 2,
        "BL": 3,
        "SD": 4,
        "CT": 5,
        "ET": 6,
        "CH": 7,
        "JD": 8,
        "SA": 9,
        "ED": 10,
        "SEPT": 11,
        "CJS": 12,
        "TC": 13,
        "LT": 14,
        "PL": 15,
        "P": 16,
        "ADM": 17,
        "CEM": 18,
    }

    # department mapping
    department_mapping = {
        "DEARTES": 1,
        "DECOM": 2,
        "DEDESIGN": 3,
        "DECIF": 4,
        "DERE": 5,
        "DEFT": 6,
        "DFF": 7,
        "DMV": 8,
        "DSEA": 9,
        "DZ": 10,
        "DANAT": 11,
        "DBIOCEL": 12,
        "DBIOQ": 13,
        "DBOT": 14,
        "DEDFIS": 15,
        "DFARM": 16,
        "DFISIO": 17,
        "DGEN": 18,
        "DPAT": 19,
        "DPRF": 20,
        "DZOO": 21,
        "DAC": 22,
        "DPJ": 23,
        "DCIR": 24,
        "DCM": 25,
        "DENF": 26,
        "DESTO": 27,
        "DFAR": 28,
        "DMI": 30,
        "DMFP": 31,
        "DNUT": 32,
        "DOR": 33,
        "DPM": 34,
        "DPED": 35,
        "DSC": 36,
        "DTG": 37,
        "DOFOT": 38,
        "DTO": 39,
        "DGEOG": 40,
        "DGEOL": 41,
        "DGEOM": 42,
        "DEST": 44,
        "DEGRAF": 45,
        "DFIS": 46,
        "DINF": 47,
        "DMAT": 48,
        "DQUI": 49,
        "DEAN": 50,
        "DECP": 51,
        "DECISO": 52,
        "DEFI": 53,
        "DEHIS": 54,
        "DELI": 55,
        "DELEM": 56,
        "DELLIN": 57,
        "DEPAC": 58,
        "DEPSI": 59,
        "DETUR": 60,
        "DDCIV": 61,
        "DDPEN": 62,
        "DDPRIV": 63,
        "DDPUB": 64,
        "DAGA": 65,
        "DECONT": 66,
        "DEPECON": 67,
        "DECIGI": 68,
        "DTPEN": 69,
        "DTFE": 70,
        "DEPLAE": 71,
        "CAU": 72,
        "DCC": 73,
        "DELT": 74,
        "DEMEC": 75,
        "DEQ": 76,
        "DHS": 77,
        "DEA": 78,
        "DEBB": 79,
        "DEP": 80,
        "DTT": 81,
        "DBC": 82,
        "DBD": 83,
        "DCA": 84,
        "DCV": 85,
        "DEE": 86,
        "DEC": 87,
        "DZO": 88
    }

    # optimization for table checking...
    table_checking_cache = {}

    for feature in recent_features:

        globalid = f'{{{feature.attributes["GlobalID"].upper()}}}'

        # skip if there's no 'local' field
        if feature.attributes.get("local") is None:
            logging.warning(
                f"Feature does not have 'local' field. Skipping {globalid}.")
            continue

        # skip if there's no 'andar' field
        if feature.attributes.get("andar") is None:
            logging.warning(
                f"Feature does not have 'andar' field. Skipping {globalid}.")
            continue

        table_schema_key = create_table_schema_key(
            feature.attributes["local"], feature.attributes["andar"])

        # caching check for table existence
        if table_schema_key not in table_checking_cache:
            schema_name, table_name = table_schema_key.split('.')

            db_cursor.execute(
                f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s);",
                (schema_name, table_name)
            )
            table_checking_cache[table_schema_key] = db_cursor.fetchone()[0]

        if not table_checking_cache[table_schema_key]:
            logging.warning(
                f"{table_schema_key} does not exist. Skipping {globalid}.")
            continue

        db_cursor.execute(
            f"SELECT EXISTS (SELECT 1 FROM {table_schema_key} WHERE globalid = %s);",
            (globalid,)
        )

        # feature geometry WKT
        geom_wkt = Geometry(feature.geometry).WKT

        # edit date
        edit_date = datetime.fromtimestamp(
            feature.attributes.get("EditDate") // 1000)

        # update row
        if db_cursor.fetchone()[0]:

            db_cursor.execute(
                f"""
                    UPDATE {table_schema_key}
                    SET
                        geom = ST_GeomFromText(%s, 31982),
                        local = %s,
                        cod_local = %s,
                        edificio = %s,
                        cod_edif = %s,
                        sigla_edif = %s,
                        setor = %s,
                        cod_setor = %s,
                        sigla_setor = %s,
                        departamento = %s,
                        sigla_dep = %s,
                        cod_dep = %s,
                        ambiente = %s,
                        capacidade = %s,
                        sigla_amb = %s,
                        tipo_amb = %s,
                        sub_tp_amb = %s,
                        cod_amb = %s,
                        nome_prof = %s,
                        area = %s,
                        "label" = %s,
                        data_atualizacao = %s
                    WHERE globalid = %s;
                """,
                # for details, see the README file
                (
                    geom_wkt,
                    fields_domains["local"].get(feature.attributes.get("local")),
                    feature.attributes.get("local"),
                    feature.attributes.get("edificio"),
                    feature.attributes.get("cod_edif"),
                    feature.attributes.get("sigla_edif"),
                    fields_domains["setor"].get(feature.attributes.get("setor")),
                    sector_mapping.get(feature.attributes.get("setor")),
                    feature.attributes.get("setor"),
                    fields_domains["departamento"].get(feature.attributes.get("departamento")),
                    feature.attributes.get("departamento"),
                    department_mapping.get(feature.attributes.get("departamento")),
                    feature.attributes.get("ambiente"),
                    feature.attributes.get("capacidade"),
                    feature.attributes.get("sigla_amb"),
                    fields_domains["tipo_amb"].get(feature.attributes.get("tipo_amb")),
                    feature.attributes.get("sub_tp_amb"),
                    feature.attributes.get("cod_amb"),
                    feature.attributes.get("nome_prof"),
                    feature.attributes.get("SHAPE__Area"),
                    feature.attributes.get("label"),
                    edit_date,
                    globalid
                )
            )

            logging.info(f"Updated {globalid} at {table_schema_key}.")

        else:

            db_cursor.execute(
                f"""
                INSERT INTO {table_schema_key} (
                    geom, andar, local, cod_local, edificio, cod_edif, sigla_edif, setor,   
                    cod_setor, sigla_setor, departamento, sigla_dep, cod_dep, ambiente, capacidade,
                    sigla_amb, tipo_amb, sub_tp_amb, cod_amb, nome_prof, area, "label",
                    data_atualizacao, globalid) VALUES (
                    ST_GeomFromText(%s, 31982), %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    geom_wkt,
                    feature.attributes.get("andar"),
                    fields_domains["local"].get(feature.attributes.get("local")),
                    feature.attributes.get("local"),
                    feature.attributes.get("edificio"),
                    feature.attributes.get("cod_edif"),
                    feature.attributes.get("sigla_edif"),
                    fields_domains["setor"].get(feature.attributes.get("setor")),
                    sector_mapping.get(feature.attributes.get("setor")),
                    feature.attributes.get("setor"),
                    fields_domains["departamento"].get(feature.attributes.get("departamento")),
                    feature.attributes.get("departamento"),
                    department_mapping.get(feature.attributes.get("departamento")),
                    feature.attributes.get("ambiente"),
                    feature.attributes.get("capacidade"),
                    feature.attributes.get("sigla_amb"),
                    fields_domains["tipo_amb"].get(feature.attributes.get("tipo_amb")),
                    feature.attributes.get("sub_tp_amb"),
                    feature.attributes.get("cod_amb"),
                    feature.attributes.get("nome_prof"),
                    feature.attributes.get("SHAPE__Area"),
                    feature.attributes.get("label"),
                    edit_date,
                    globalid
                )
            )

            logging.info(f"Added {globalid} to {table_schema_key}.")


def delete_features(db_cursor, all_globalids):
    """
    Deletes features from the database.
    """

    for table_schema_key, globalids in all_globalids.items():
        schema_name, table_name = table_schema_key.split('.')

        db_cursor.execute(
            f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s);",
            (schema_name, table_name)
        )

        if not db_cursor.fetchone()[0]:
            logging.warning(
                f"{table_schema_key} does not exist. Skipping deletion.")
        else:

            db_cursor.execute(f"SELECT globalid FROM {table_schema_key};")
            existing_globalids = {row[0] for row in db_cursor.fetchall()}

            globalids_to_delete = existing_globalids - set(globalids)

            if globalids_to_delete:
                db_cursor.execute(
                    f"DELETE FROM {table_schema_key} WHERE globalid IN %s RETURNING *;",
                    (tuple(globalids_to_delete),)
                )
                deleted_rows = db_cursor.fetchall()
                logging.info(
                    f"Deleted {len(deleted_rows)} features from {table_schema_key}.")


if __name__ == "__main__":

    config = init_config()

    init_logging(config["log_file"])

    logging.info("Integration started.")

    try:

        logging.info("GIS query started.")

        all_globalids, recent_features, fields_domains = get_gis_data(
            config["gis"], config["day_interval"])

        logging.info("GIS query finished.")

        with get_db_connection(config["database"]) as db_conn:
            with db_conn.cursor() as db_cursor:

                if len(recent_features) > 0:
                    update_insert_features(
                        db_cursor, recent_features, fields_domains)

                delete_features(db_cursor, all_globalids)

                # TODO: I suggest to have a function in the database that updates all empty key values.
                # This function can be executed here...

            db_conn.commit()

        logging.info("Integration finished.")

    except Exception as e:
        logging.error(e)
