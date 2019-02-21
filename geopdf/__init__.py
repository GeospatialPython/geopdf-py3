# -*- coding: utf-8 -*-
"""Adds GeoPDF functionality to ReportLab"""

from reportlab.lib.colors import black
from reportlab.pdfbase.pdfdoc import PDFArray, PDFDictionary, PDFName, PDFString
from reportlab.pdfbase import pdfdoc
from reportlab.pdfgen import canvas


class GeoPDFBase(PDFDictionary):
    """
    Base class for GeoPDF dicts.
    """

    def __init__(self, dict=None):
        """dict should be namestring to value eg "a": 122 NOT pdfname to value NOT "/a":122"""
        if dict is None:
            self.dict = {}
        else:
            self.dict = dict.copy()

        self.set_defaults()

    def set_defaults(self):
        """
        A hook for creating default values.
        """
        return

    def is_valid(self):
        """
        Test the validity of the dict.
        """
        return True


class Projection(GeoPDFBase):
    """
    A Projection dict.
    """

    def set_defaults(self):
        self.dict.setdefault('ProjectionType', PDFString('GEOGRAPHIC'))
        self.dict.setdefault('Type', PDFName('Projection'))


class LGIDict(GeoPDFBase):
    """
    The LGI dict.
    """

    def set_defaults(self):
        self.dict.setdefault('Type', PDFString('LGIDict'))
        self.dict.setdefault('Version', PDFString('2.1'))
        self.dict.setdefault('Projection', Projection({'Datum': PDFString('WE')}))

    def is_valid(self):
        if not any(map(lambda key: key in self.dict, 'Registration CTM'.split())):
            return False

        for key, value in self.dict.items():
            if hasattr(value, 'is_valid') and getattr(value, 'is_valid')() is False:
                return False

        return True


class GeoCanvas(canvas.Canvas):

    LGIDict = PDFArray([])

    def _startPage(self):
        # now get ready for the next one
        super(GeoCanvas, self)._startPage()
        self.LGIDict = PDFArray([])

    def showPage(self):
        """Close the current page and possibly start on a new page."""
        # ensure a space at the end of the stream - Acrobat does
        # not mind, but Ghostscript dislikes 'Qendstream' even if
        # the length marker finishes after 'Q'

        pageWidth = self._pagesize[0]
        pageHeight = self._pagesize[1]
        cM = self._cropMarks
        code = self._code
        if cM:
            bw = max(0, getattr(cM, 'borderWidth', 36))
            if bw:
                markLast = getattr(cM, 'markLast', 1)
                ml = min(bw, max(0, getattr(cM, 'markLength', 18)))
                mw = getattr(cM, 'markWidth', 0.5)
                mc = getattr(cM, 'markColor', black)
                mg = 2 * bw - ml
                cx0 = len(code)
                if ml and mc:
                    self.saveState()
                    self.setStrokeColor(mc)
                    self.setLineWidth(mw)
                    self.lines([
                        (bw, 0, bw, ml),
                        (pageWidth + bw, 0, pageWidth + bw, ml),
                        (bw, pageHeight + mg, bw, pageHeight + 2 * bw),
                        (pageWidth + bw, pageHeight + mg, pageWidth + bw, pageHeight + 2 * bw),
                        (0, bw, ml, bw),
                        (pageWidth + mg, bw, pageWidth + 2 * bw, bw),
                        (0, pageHeight + bw, ml, pageHeight + bw),
                        (pageWidth + mg, pageHeight + bw, pageWidth + 2 * bw, pageHeight + bw)
                    ])
                    self.restoreState()
                    if markLast:
                        # if the marks are to be drawn after the content
                        # save the code we just drew for later use
                        L = code[cx0:]
                        del code[cx0:]
                        cx0 = len(code)

                bleedW = max(0, getattr(cM, 'bleedWidth', 0))
                self.saveState()
                self.translate(bw - bleedW, bw - bleedW)
                if bleedW:
                    # scale everything
                    self.scale(1 + (2.0 * bleedW) / pageWidth, 1 + (2.0 * bleedW) / pageHeight)

                # move our translation/expansion code to the beginning
                C = code[cx0:]
                del code[cx0:]
                code[0:0] = C
                self.restoreState()
                if markLast:
                    code.extend(L)
                pageWidth = 2 * bw + pageWidth
                pageHeight = 2 * bw + pageHeight

        code.append(' ')
        page = pdfdoc.PDFPage()
        page.__NoDefault__ = """Parent
        MediaBox Resources Contents CropBox Rotate Thumb Annots B Dur Hid Trans AA
        PieceInfo LastModified SeparationInfo ArtBox TrimBox BleedBox ID PZ
        Trans LGIDict""".split()
        page.pagewidth = pageWidth
        page.pageheight = pageHeight

        if getattr(self, 'LGIDict', None):
            if len(self.LGIDict.sequence) == 1:
                page.LGIDict = self.LGIDict.sequence[0]
            else:
                page.LGIDict = self.LGIDict

        page.Rotate = self._pageRotation
        page.hasImages = self._currentPageHasImages
        page.setPageTransition(self._pageTransition)
        page.setCompression(self._pageCompression)
        if self._pageDuration is not None:
            page.Dur = self._pageDuration

        strm = self._psCommandsBeforePage + [self._preamble] + code + self._psCommandsAfterPage
        page.setStream(strm)
        self._setColorSpace(page)
        self._setExtGState(page)
        self._setXObjects(page)
        self._setShadingUsed(page)
        self._setAnnotations(page)
        self._doc.addPage(page)

        if self._onPage:
            self._onPage(self._pageNumber)
        self._startPage()

    def addGeo(self, **kwargs):
        """
        Adds the LGIDict to the document.
        :param kwargs: Keyword arguments that are used to update the LGI Dictionary.
        """

        lgi = LGIDict()
        lgi.dict.update(kwargs)

        if not lgi.is_valid():
            return

        pdf_obj = lgi.format(self._doc)
        self.LGIDict.sequence.append(pdf_obj)
        return pdf_obj
