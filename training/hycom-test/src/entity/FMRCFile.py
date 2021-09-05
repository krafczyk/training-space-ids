"""Python Methods for the FMRCFile Type
"""
def download(this):
    """Download this particular FMRCFile from the Thredds server
    """
    if this.dataArchive.subsetOptions is None or this.dataArchive.fmrc is None:
        dataArchive = c3.FMRCDataArchive.get(this.dataArchive.id)
    else:
        dataArchive = this.dataArchive
    fmrc = dataArchive.fmrc

    if fmrc.urlPath is None:
        fmrc = c3.HycomFMRC.get(this.dataArchive.fmrc.id)

    url_path = fmrc.urlPath

    url = c3.HycomUtil.buildThreddsUrl(
        baseurl = url_path,
        vars = this.vars.split(','),
        subset = dataArchive.subsetOptions
        )

    return url