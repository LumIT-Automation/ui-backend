# Jira.
JIRA_ENABLED = False
JIRA_HOST = "jiraprd.crif.com"
JIRA_TOKEN = "OTgxNDU1MzE4NTkwOi8nvhmu4Y08ZCaB+2U0Rx9xuR7g"
JIRA_TLS_VERIFY= True
JIRA_JQL_FILTER = "project = \"ITIO Service Management\" and (status = \"CR Approved\" or status= \"CR Planned\" or status= \"CR In Progress\") and issuetype = Firewall"

# Cisco Spark.
PLUGINS = [
    'ui_backend.plugins.CiscoSpark'
]

CONCERTO_ENVIRONMENT = "Development"
CISCO_SPARK_URL = "https://webexapis.com/v1"
CISCO_SPARK_TOKEN = ""
CISCO_SPARK_ROOM_ID = ""
