from c3python import get_c3, C3Migrate
import os

from_tenant = "dev"
from_tag = "tc02d"
base_url = "tc02d-dev.c3dti.ai"
from_url = "https://" + base_url
from_keyfile = "/home/dadams/.c3/c3-rsa-"+ base_url

do_files = True
do_notebooks = False

c3 = get_c3(from_url, from_tenant, from_tag, keyfile=from_keyfile)

# make a directory for this tag-tenant and download the files there
os.makedirs(from_tag + "-" + from_tenant, exist_ok=True)
os.chdir(from_tag + "-" + from_tenant)
if do_notebooks:
    os.makedirs("meta", exist_ok=True)
    notebooks = c3.JupyterNotebook.fetch(spec={
        "filter":c3.Filter.inst().not_().startsWith('path','tutorials/'),
        "limit":-1
        }).objs
    paths = [notebook.path for notebook in notebooks]
    result = c3.JupyterNotebook.downloadToLocalClient(paths,'./','./meta',True,False)
    print(result)
    os.system("rm -rf meta")
if do_files:
    files = c3.JupyterFile.fetch(spec={
        "filter":c3.Filter.inst().not_().startsWith('path','tutorial'),
        "limit":-1
        }).objs
    paths = [file.path for file in files]
    # check the contentSize of each file, if it is > 30MB, do not download it.
    # Remove it from the list of files to download. Instead, create a file with 
    # the same name and path, but with a .html extension and write the externameFile.url 
    # in the form of a link to the file in that file.
    for file in files:
        if file.contentSize > 30000000:
            url = file.externalFile.url
            path = file.path
            filename = path.split("/")[-1]
            os.system("echo '<a href=\"" + url + "\">" + filename + "</a>' > " + filename + ".html")
            paths.remove(path)
    os.makedirs("meta", exist_ok=True)
    result = c3.JupyterFile.downloadToLocalClient(paths,'./','./meta',True,False)
    print(result)
    os.system("rm -rf meta")

# result = c3.JupyterFile.downloadToLocalClient(paths,'./','./meta',True,False)
# print(result)
# os.system("rm -rf meta")
# Look at all files Recusively and sort by size.  List the top 10 largest files
# find . -type f -exec du -Sh {} + | sort -rh | head -n 10