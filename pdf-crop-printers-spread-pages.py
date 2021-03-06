#!/usr/bin/env python3

# Duplicate and crop pages in a PDF that has the pages laid out in "printer's spread",
# e.g. pages 24/1, 2/23, 22/3 etc. (see http://www.fujispray.com/User%20Manual%20T-Model%20201602.pdf for an example)
#
# Input:
#
# +-------+-------+
# |       |       |
# |  p24  |  p1   |
# |       |       |
# +-------+-------+
# +-------+-------+
# |       |       |
# |  p2   |  p23  |
# |       |       |
# +-------+-------+
# ...
# +-------+-------+
# |       |       |
# |  p12  |  p13  |
# |       |       |
# +-------+-------+
#
# Output:
#
# +-------+
# |       |
# |  p1   |
# |       |
# +-------+
# +-------+
# |       |
# |  p2   |
# |       |
# +-------+
# ...
# +-------+
# |       |
# |  p24  |
# |       |
# +-------+

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import sys
import os
import re
import argparse
import logging
import PyPDF2
from pathlib import Path, PurePath

class Tool(object):

    def __init__(self, args):
        self.args = args

    def run(self):
        input_pdf_path = self.args.path
        output_pdf_name = input_pdf_path.stem + '.out' + input_pdf_path.suffix
        output_pdf_path = input_pdf_path.with_name(output_pdf_name)
        self.writer = PyPDF2.PdfFileWriter()
        print(output_pdf_path)

        reader = PyPDF2.PdfFileReader(input_pdf_path.as_posix())

        page_count = reader.getNumPages()

        first_page = reader.getPage(0)
        media_box = first_page.mediaBox

        offset = self.args.reduce_margin_offset

        crops = [PyPDF2.generic.RectangleObject([0 + offset, 0 + offset, media_box.getUpperRight_x() - offset, media_box.getUpperRight_y() / 2 - offset]), PyPDF2.generic.RectangleObject([0 + offset, media_box.getUpperRight_y() / 2 + offset, media_box.getUpperRight_x() - offset, media_box.getUpperRight_y() - offset])]

        # final page numbers [1, n/2], the first output page is on the right side
        # # of the first input page, the next output page on the left side of the
        # second input page etc. We flip back and forth for each input page.
        for i in range(page_count):
            page = reader.getPage(i)
            page.cropBox = crops[0]
            self.writer.addPage(page)
            crops = list(reversed(crops))

        # final page numbers [n/2+1, n], the first one is on the left side of the first input page.
        reader = PyPDF2.PdfFileReader(input_pdf_path.as_posix())
        for i in range(page_count - 1, -1, -1):
            page = reader.getPage(i)
            page.cropBox = crops[0]
            self.writer.addPage(page)
            crops = list(reversed(crops))

        with open(output_pdf_path, 'wb') as f:
            self.writer.write(f)

    @classmethod
    def main(cls):
        parser = argparse.ArgumentParser(description='Duplicate and crop pages in a PDF that has the pages laid out in "printer\'s spread"')
        parser.add_argument('--reduce-margin-offset', type=float, default=0, help='Offset by which to shrink the crop box to reduce blank margin space')
        parser.add_argument('path', type=PurePath, help='Path to input PDF')

        args = parser.parse_args()

        return cls(args).run()


if __name__ == "__main__":
    sys.exit(Tool.main())
