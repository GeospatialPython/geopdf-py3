GeoPDF
======

[![Build Status](https://travis-ci.org/garnertb/geopdf.svg?branch=master)](https://travis-ci.org/garnertb/geopdf)

GeoPDF is a simple wrapper around [ReportLab](http://www.reportlab.com/) that allows developers to create basic GeoPDFs by
following the [GeoPDF Encoding Best Practices](http://portal.opengeospatial.org/files/?artifact_id=33332)
published by the Open Geospatial Consortium.  In its current state, this project only exposes the bare minimum needed for
developers to create a GeoPDF in reportlab.

Installation
============

Install this project from PyPI by running the command below:

```$ pip install geopdf```

or alternatively from source (github master):

```$ pip install git+https://github.com/garnertb/geopdf.git#egg=geopdf```


Creating a GeoPDF
=================
If you have worked with reportlab before, GeoPDF should feel familiar.  GeoPDF subclasses the reportlab Canvas so you get all
of the API methods you are used to along with some additional geospatial methods!

Example
-------
In this example, we create a 200 x 200 empty rectangle with the bounds of the earth in WGS 1984 (-180, -90, 180, 90).  The main
interface you need to be familiar with is the `canvas.addGeo` method which adds the GeoPDF dictionary (called `LGIDict`)
to the PDF.  GeoPDF uses a geographic projection by default so in a minimal example you only have set the
registration points (which tie PDF pixel locations to map locations) and you're done.  The `addGeo` method updates the LGIDict with any
keyword arguments that you pass it so refer to the [GeoPDF Encoding Best Practices](http://portal.opengeospatial.org/files/?artifact_id=33332)
document to learn about all of the things that the GeoPDF supports.

```python
from geopdf import GeoCanvas
from reportlab.pdfbase.pdfdoc import PDFString, PDFArray

canvas = GeoCanvas('example1.pdf')
canvas.rect(200, 400, 200, 200, stroke=1)

# A series of registration point pairs (pixel x, pixel y, x, y)
registration = PDFArray([
    PDFArray(map(PDFString, ['200', '400', '-180', '-90'])),
    PDFArray(map(PDFString, ['200', '600', '-180', '90'])),
    PDFArray(map(PDFString, ['400', '600', '180', '90'])),
    PDFArray(map(PDFString, ['400', '400', '180', '-90']))
])

canvas.addGeo(Registration=registration)
canvas.save()
```

Issues
======
Please report any bugs or requests that you have using the GitHub issue tracker!


Notes
=====
- http://portal.opengeospatial.org/files/?artifact_id=33332


Contributing
============

- Fork the repository on GitHub
- Create a named feature branch (like `add_component_x`)
- Write your change
- Write tests for your change (if applicable)
- Run the tests, ensuring they all pass
- Submit a Pull Request using GitHub

