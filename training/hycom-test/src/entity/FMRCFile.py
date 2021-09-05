"""Python Methods for the FMRCFile Type
"""
def download(this):
    """Download this particular FMRCFile from the Thredds server
    """

    url = c3.HycomUtil.buildThreddsUrl(
        baseurl = this.dataArchive.fmrc.urlPath
        vars = this.vars.split(,)
        options = 
        )
        
    return url