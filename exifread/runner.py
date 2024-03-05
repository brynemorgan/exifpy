

file = '/Users/brynmorgan/dev/exif-samples/drone/MicaAltum_MS.tif'

fh = open(file, 'rb')



# ARGUMENTS PASSED TO PROCESS_FILE
# stop_tag=DEFAULT_STOP_TAG
details=True
strict=False
debug=False
truncate_tags=False
auto_seek=True
xmp=True
clean=False

if auto_seek:
    fh.seek(0)

#-------------------------------------------------------------------------------
# 2. GET OFFSET, ENDIAN, and set a FAKE_EXIF
#-------------------------------------------------------------------------------

fake_exif = 0

data = fh.read(12)

# TIFF
# if data[0:2] in [b'II', b'MM']:
#     # it's a TIFF file
#     offset, endian = _find_tiff_exif(fh)
# in _find_tiff_exif(fh):
fh.seek(0)
endian = fh.read(1)
offset = 0

# Get unicode character for endian
endian = chr(exifread.utils.ord_(endian[0])) 