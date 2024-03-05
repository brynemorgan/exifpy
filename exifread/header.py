from msilib.schema import Binary
import re
import struct
from typing import BinaryIO, Dict, Any

from .exif_log import get_logger
from .utils import Ratio,dms_to_dd, get_buffer, get_byte_format, bytes_to_decimal, parse_bytes
from .tags import EXIF_TAGS, DEFAULT_STOP_TAG, FIELD_TYPES, IGNORE_TAGS, makernote
from .xmp import XMP
logger = get_logger()






class ImageHeader:
    """
    
    Attributes
    ----------
    file_handle : BinaryIO

    endian : str

    offset : int

    """
    
    def __init__(
        self, file_handle: BinaryIO, endian, offset, fake_exif, strict: bool,
        debug=False, detailed=True, truncate_tags=True
    ):
        # TODO: Reduce the number of arguments to the init.

        # file_handle
        self.file_handle = file_handle
        # endian
        self.endian = endian
        # offset
        self.offset = offset
        # ifd_offsets
        self.ifd_offsets = self.get_ifd_offsets()



        def get_ifd_offsets(self) -> list:

            i = self._get_ifd0()

            ifd_list = []
            set_ifds = set()
            while i:
                if i in set_ifds:
                    logger.wardning('IFD loop detected.')
                    break
                set_ifds.add(i)
                ifd_list.append(i)
                i = self._get_next_ifd(i)
            
            return ifd_list


        def _get_ifd0(self) -> int:

            # ifd0_offset = bytes_to_decimal(
            #     self.file_handle, 
            #     self.offset, 
            #     self.endian, 
            #     offset = 4, 
            #     length = 4
            # )

            ifd0_offset = parse_bytes(
                self.endian,
                buffer = get_buffer(self.file_handle, offset = self.offset + 4, n=4),
            )
            
            return ifd0_offset + self.offset
        

        def _get_next_ifd(ifd_offset) -> int:

            # Get size of IFD
            ifd_len = bytes_to_decimal(
                self.file_handle, 
                self.offset, 
                self.endian, 
                offset=ifd_offset, 
                length=2
            )

            offset = ifd_offset + 2 + 12 * ifd_len
            # Get index of the next IFD
            next_ifd = bytes_to_decimal(
                self.file_handle, 
                self.offset, 
                self.endian, 
                offset=offset, 
                length=4
            )

            if next_ifd == ifd_offset:
                return 0
            return next_ifd


class ImageFileDirectory:

    def __init__(self, fh, offset, endian):
        # offset
        self.offset = offset
        # endian
        self.endian = endian
        # name
        self.name = None
        # n_tags
        self.n_tags = parse_bytes(
            self.endian,
            buffer = get_buffer(fh, self.offset, n=2)
        )


    
    def get_n_tags(self):






# ifd = ifd_list[0]

# tag_dict = exifread.tags.EXIF_TAGS

# #
# entries = bytes_to_decimal(fh, offset, endian, offset=ifd, length=2)    # 25    This has already been calculated...

# for i in range(entries):
#     # Offset of entry i
#     entry = ifd + 2 + 12 * i                                        # 6381786
#     tag_id = bytes_to_decimal(fh,offset,endian,offset=entry,length=2)      # 254

#     # Get the dict values for the tag...
#     tag_entry = tag_dict.get(tag_id)

#     if tag_entry:
#         # Get tag name
#         tag_name = tag_entry[0]


# self._process_tag(ifd, ifd_name, tag_entry, entry, tag, tag_name, relative, stop_tag)




# tag_bytes = get_buffer(fh,tag_offset, 12)

tag_dict = EXIF_TAGS
FIELD_TYPES = FIELD_TYPES

field_types = {
     0: {'Type': 'Proprietary', 'Abbrev': 'X', 'Size': 0},
     1: {'Type': 'Byte', 'Abbrev': 'B', 'Size': 1},
     2: {'Type': 'ASCII', 'Abbrev': 'A', 'Size': 1},
     3: {'Type': 'Short', 'Abbrev': 'S', 'Size': 2},
     4: {'Type': 'Long', 'Abbrev': 'L', 'Size': 4},
     5: {'Type': 'Ratio', 'Abbrev': 'R', 'Size': 8},
     6: {'Type': 'Signed Byte', 'Abbrev': 'SB', 'Size': 1},
     7: {'Type': 'Undefined', 'Abbrev': 'U', 'Size': 1},
     8: {'Type': 'Signed Short', 'Abbrev': 'SS', 'Size': 2},
     9: {'Type': 'Signed Long', 'Abbrev': 'SL', 'Size': 4},
    10: {'Type': 'Signed Ratio', 'Abbrev': 'SR', 'Size': 8},
    11: {'Type': 'Single-Precision Floating Point (32-bit)', 'Abbrev': 'F32', 'Size': 4, 'Format': 'f'},
    12: {'Type': 'Double-Precision Floating Point (64-bit)', 'Abbrev': 'F64', 'Size': 8, 'Format': 'd'},
    13: {'Type': 'IFD', 'Abbrev': 'L', 'Size': 4}
}
# https://docs.python.org/3/library/struct.html

class ExifTag:

    def __init__(self, tag_bytes: bytes, offset: int, endian='I'):
        # bytes
        self.bytes = tag_bytes
        # offset
        self.offset = offset
        # _endian
        self._endian = endian
        # id
        self.id = parse_bytes(endian, self.bytes[0:2])
        # name
        self.name = tag_dict.get(self.id)[0]
        # count (number of values; not equal to # of bytes)
        self.count = parse_bytes(endian, self.bytes[4:8])
        # type
        self.type = parse_bytes(endian, self.bytes[2:4])

        # unknown field type
        if not 0 < self.type < len(FIELD_TYPES):
            if not self.strict:
                return
            raise ValueError('Unknown type %d in tag 0x%04X' % (self.type, XXX))

        # type_length
        self.type_length = field_types[self.type].get('Size')
        # value_offset
        self.value_offset = self._get_value_offset()

        # value_bytes
        # self.value_bytes = self._get_value_bytes(fh)


    def _get_value_offset(self):
        if self.count * self.type_length > 4:
            value_offset = parse_bytes(self._endian, self.bytes[8:])
        else:
            value_offset = self.offsest + 8
        
        return value_offset

    def _get_value_bytes(self, fh: BinaryIO):
        if self.count * self.type_length > 4:
            value_bytes = get_buffer(fh, self.value_offset, n=self.count*self.type_length)
            #         # offset is not the value; it's a pointer to the value
            #         # if relative we set things up so s2n will seek to the right
            #         # place when it adds self.offset.  Note that this 'relative'
            #         # is for the Nikon type 3 makernote.  Other cameras may use
            #         # other relative offsets, which would have to be computed here
            #         # slightly differently.
            #         if relative:
            #             tmp_offset = self.s2n(offset, 4)
            #             offset = tmp_offset + ifd - 8
            #             if self.fake_exif:
            #                 offset += 18
            #         else:
            #             offset = self.s2n(offset, 4)
        else:
            value_bytes = self.bytes[8:]
        
        return value_bytes


    def process_ascii(self, fh):
        
        value = ''
        try:
            value_bytes = self._get_value_bytes(fh)

            if self.count != 0:
                # Get rid of garbage after null
                value_bytes = value_bytes.split(b'\x00',1)[0]
                try:
                    value = value_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    print('Possibly corrupted field')
                    logger.warning('Possibly corrupted field %s in %s IFD', self.name, ifd_name)
        except OverflowError:
            logger.warning('OverflowError at position: %s', self.value_offset)
        except MemoryError:
            logger.warning('MemoryError at position: %s', self.value_offset)
        return value
















# class LongExifTag(ExifTag):

#     def __init__(self, tag_bytes: bytes, offset: int, endian='I'):
#         super().__init__(tag_bytes, offset, endian)

#     def _get_value_bytes(self, fh: BinaryIO):
#         value_offset = parse_bytes(self._endian, self.bytes[8:])
#         value_bytes = get_buffer(fh, value_offset, n=self.count*self.type_length)
#         return value_bytes


# signed = 'Signed' in field_types[field_type].get('Type')

# # If ASCII
# if field_type == 2:
#     # values = self._process_field2(ifd_name, tag_name, count, offset)
# else:
#     # values = self._process_field(tag_name, count, field_type, type_length, offset)
#     if 'Ratio' in field_types[field_type].get('Type'):
#         # a ratio
#         value = Ratio(
#             self.s2n(offset, 4, signed),
#             self.s2n(offset + 4, 4, signed)
#         )
    

# signed = 'Signed' in field_types[field_type].get('Type')

# ratio = 'Ratio' in field_types[field_type].get('Type')

class Bucket():
    """

    A container that holds a set of image, flight, or met data related to UAVs

    """
    def __init__(self, bucket_object=None, config=None):

class ImageBucket(Bucket):
    """

    A bucket of Image Data.



    """
    def __init__(self, config):
        super().__init__(FlightImage, config=config)


        # value_offset (pointer to value)
        self.value_offset = parse_bytes(endian, self.bytes[8:])




