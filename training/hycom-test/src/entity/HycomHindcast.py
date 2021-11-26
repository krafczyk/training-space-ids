# from urllib.parse import urlencode,urljoin

# def downloadLocal(this, hycomSubsetOptions, localDir):

#     url_path = this.urlPath
    
#     baseurl = urljoin('https://ncss.hycom.org/thredds/ncss/grid',url_path)

#     # Convert FMRCSubsetOptions object to a dictionary
#     options = {
#         'disableLLSubset': hycomSubsetOptions.disableLLSubset,
#         'disableProjSubset': hycomSubsetOptions.disableProjSubset,
#         'horizStride': hycomSubsetOptions.horizStride,
#         'timeStride': hycomSubsetOptions.timeStride,
#         'vertStride': hycomSubsetOptions.vertStride,
#         'addLatLon': hycomSubsetOptions.addLatLon,
#         'accept': hycomSubsetOptions.accept
#         }
    
#     # Handle time coverage separately
#     time_start = hycomSubsetOptions.timeRange.start
#     time_end = hycomSubsetOptions.timeRange.start

#     if time_start == time_end:
#         options ['time'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
#         filename = this.id + '-' + time_start.strftime("%Y-%m-%dT%H:%M:%SZ") + '.nc'
#     else:
#         options['time_start'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
#         options['time_end'] = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")
#         filename = this.id + '-' + time_start.strftime("%Y-%m-%dT%H:%M:%SZ") + '-' + time_end.strftime("%Y-%m-%dT%H:%M:%SZ") + '.nc'

#     # Construt query url
#     vars_list = hycomSubsetOptions.vars.split(',')
#     vvars = [('var',v) for v in vars_list]
#     url1 = urlencode(vvars,{'d':2})
#     url2 = urlencode(options)
#     url = baseurl + '?' + url1 + '&' + url2
    
#     #print(url)

#     localPath = c3.HycomUtil.downloadToLocal(url, filename, localDir)
    
#     return localPath

# from datetime import datetime
# import numpy as np

# def getDataSubset(imin,jmin,imax,jmax,metric,start,end,batchSize=100):
#     """Returns a subset for the given metric data from the given start and end time.

#     Args:
#         imin (int): Minimum longitude from lat-long pair indices
#         jmin (int): Minimum latitude from lat-long pair indices
#         imax (int): Maximum longitude from lat-long pair indices
#         jmax (int): Maximum latitude from lat-long pair indices
#         metric (str): Metric to be extracted from the dataset
#         start (datetime): Start time of the subset
#         end (datetime): End time of the subset
#         batchSize (int): Number of lat-long pairs to be extracted in each batch

#     Returns:
#         array: Numpy array of the subsetted data ordered as [time,lat,lon]

#     Notes:
#         - Currently limited to hour resolution
#         - Only handles a single metric
#         - The data indexing is not efficient since the indices must be parsed from the
#         lat-long pair ids.  If the HycomLatLong pair table was ordered by i,j, then
#         the pairs would get extracted in i,j order and there would be no need to parse.
#         this could be done by defining a new id that is a simple ascending integer.

#     """
    
#     my_spec = c3.EvalMetricsSpec(
#             filter = "i>="+str(imin)+" && i<="+str(imax)+" && j>="+str(jmin)+" && j<="+str(jmax),
#             limit = -1,
#             expressions = [metric],
#             start = start.strftime("%Y-%m-%d"),
#             end = end.strftime("%Y-%m-%d"),
#             interval = "HOUR" 
#         )
#     # Evaluate the Spec using EvalSourceSpec which returns a stream of numpy arrays
#     sourceType = c3.TypeRef(typeName="HycomLatLongPair")
#     em_source_spec = c3.EvalMetricsSourceSpec.createNdArraySourceSpec(my_spec, sourceType)
#     em_source_spec.batchExport()
#     stream_spec = c3.BatchStreamSpec(batchSize=batchSize)
#     source_stream = em_source_spec.toStream(stream_spec)
    
#     # Process the data in to a (time,long,lat) data array
#     duration = end - start
#     duration_in_s = duration.total_seconds()
#     nt = int(divmod(duration_in_s, 3600)[0]) # total duration in hours
#     data = np.zeros((nt,imax-imin+1,jmax-jmin+1))
#     while source_stream.hasNext():
#         stream = source_stream.next()
#         idi = -1
#         # Transpose time series
#         for id in stream.indices[0]:
#             idi += 1
#             istr,jstr = id.split('_')[1].split('-')
#             i = int(istr) - imin
#             j = int(jstr) - jmin
#             ti = 0
#             for t in stream.indices[2]:
#                 data[ti,i,j] = stream.data[idi,0,ti]
#                 ti += 1
    
#     # Cleans up any persisted files storing snapshot of data source
#     em_source_spec.cleanUp()
#     # Removes spec from database
#     em_source_spec.remove()
#     return data