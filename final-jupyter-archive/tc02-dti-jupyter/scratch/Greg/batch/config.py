# -------------------------------------------------------------------------
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
# ----------------------------------------------------------------------------------
# The example companies, organizations, products, domain names,
# e-mail addresses, logos, people, places, and events depicted
# herein are fictitious. No association with any real company,
# organization, product, domain name, email address, logo, person,
# places, or events is intended or should be inferred.
# --------------------------------------------------------------------------

# Global constant variables (Azure Storage account/Batch details)

# import "config.py" in "python_quickstart_client.py "

_BATCH_ACCOUNT_NAME = 'gregbatchaccount'  # Your batch account name
_BATCH_ACCOUNT_KEY = 'koz8n5TKez2RR0hPOWsBR4w/PImkt4yztB7PyVJi99EmxAybu+/U9j+vubTYi280AnqE+DrPLsklG/zY/3bgnQ=='  # Your batch account key
_BATCH_ACCOUNT_URL = 'https://gregbatchaccount.westus2.batch.azure.com'  # Your batch account URL
_STORAGE_ACCOUNT_NAME = 'gregbatchstorage'
_STORAGE_ACCOUNT_KEY = 'WU/kYlSodzdat+0TLUCu+UstLBpPNIxGH+HEU+yhLYojVTVee/58bz8zDqoxScFrzgU1iHgvHLsv1nNsZtmC7w=='
_STORAGE_ACCOUNT_DOMAIN = 'blob.core.windows.net' # Your storage account blob service domain

_POOL_ID = 'ffmpeg-pool'  # Your Pool ID
_POOL_NODE_COUNT = 1  # Pool node count
_POOL_VM_SIZE = 'Standard_A1_v2'  # VM Type/Size
_JOB_ID = 'PythonQuickstartJobFfmpeg'  # Job ID
_STANDARD_OUT_FILE_NAME = 'stdout.txt'  # Standard Output file