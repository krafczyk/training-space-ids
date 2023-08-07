from c3python import get_c3, C3Migrate
import os

from_url = "https://tc01d-dev.c3dti.ai"
from_tenant = "dev"
from_tag = "tc01d"
from_keyfile = "/home/dadams/.c3/c3-rsa-tc01d-dev.c3dti.ai"

c3 = get_c3(from_url, from_tenant, from_tag, keyfile=from_keyfile)

# make a directory for this tag-tenant and download the files there
os.makedirs(from_tag + "-" + from_tenant, exist_ok=True)
os.chdir(from_tag + "-" + from_tenant)
# os.makedirs("notebooks", exist_ok=True)
os.makedirs("meta", exist_ok=True)
notebooks = c3.JupyterNotebook.fetch(spec={
    "filter":c3.Filter.inst().not_().startsWith('path','tutorials/'),
    "limit":-1
    }).objs
paths = [notebook.path for notebook in notebooks]
result = c3.JupyterNotebook.downloadToLocalClient(paths,'./','./meta',True,False)

print(result)
# Remove the files in the meta directory and the meta directory
os.system("rm -rf meta")