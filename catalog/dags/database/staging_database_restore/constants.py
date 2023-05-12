import os

from common.constants import AWS_CONN_ID


_ID_FORMAT = "{}-openverse-db"

DAG_ID = "staging_database_restore"
PROD_IDENTIFIER = _ID_FORMAT.format("prod")
STAGING_IDENTIFIER = _ID_FORMAT.format("dev")
TEMP_IDENTIFIER = _ID_FORMAT.format("dev-next")
SKIP_VARIABLE = "SKIP_STAGING_DATABASE_RESTORE"
AWS_RDS_CONN_ID = os.environ.get("AWS_RDS_CONN_ID", AWS_CONN_ID)
