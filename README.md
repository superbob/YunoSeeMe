YunoSeeMe
=========

This is a collection of tools to compute elevation profiles between two points.

It makes an extensive use of GDAL to handle DEM files to get elevation data from.

Run
---

 1. Clone this repository
 2. Check the requirements (python >= 2.7 and the libraries listed bellow)
 3. Download a DEM (see _DEM maps_ and _Tests_)
 4. Run
   > ```$ ./profile.py lat1 long1 lat2 long2 path/to/dem/file```

Dependencies
------------

It needs the following python libraries to work correctly:

 * NumPy (1.9.2)
 * GDAL (1.11.2 <- not the last one)
 * CherryPy (3.8.0) (to run the web server)
 * pytest (2.7.2) (to run tests)

These libraries can be obtained by pip or easy\_install. They _may_ need two following system packages to work correctly:

 * GDAL headers (gdal-devel), libs (libgdal1) and python bindings (python-gdal), main binaries can be useful too (gdal)
 * NumPy headers (python-numpy-devel) and libs (python-numpy)
 * PROJ headers (libproj-devel) and libs (libproj0 and libproj9)

See https://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries to know how to get GDAL.

virtualenv
----------

A virtualenv can be used (in fact, I use one). Consider using the `--no-site-packages` option.

MacOS X
-------

The MacOS X link (http://www.kyngchaos.com/software:frameworks) contains a package that bundles all the GDAL requirements (GDAL Complete Framework) except NumPy that should already be installed in the system.

The gdal python library may not work (especially when using a virtualenv),
in that case, you can copy the library included in the GDAL Framework using the following command inside your environment:

    cp -R /Library/Frameworks/GDAL.framework/Versions/1.11/Python/2.7/site-packages/* <env>/lib/python2.7/site-packages

DEM maps
--------

The elevation related tools need a data elevation model (DEM) to work correctly.

These DEMs are known to work:

[Digital Elevation Model over Europe (EU-DEM)](http://www.eea.europa.eu/data-and-maps/data/eu-dem)

> The EU-DEM dataset is a realisation of the Copernicus programme, managed by the European Commission, DG Enterprise and Industry.
>
> The EU-DEM is a hybrid product based on SRTM and ASTER GDEM data fused by a weighted averaging approach and it has been generated as a contiguous dataset divided into 1 degree by 1 degree tiles, corresponding to the SRTM naming convention.

_http://www.eea.europa.eu/data-and-maps/data/eu-dem#tab-metadata_

[Shuttle Radar Topography Mission (SRTM)](http://www2.jpl.nasa.gov/srtm/)

> SRTM was a joint project of NASA, the German and Italian space agencies, and the National Geospatial-Intelligence Agency.
>
> It was managed by NASA's Jet Propulsion Laboratory, Pasadena, California, for NASA's Science Mission Directorate, Washington, D.C.
>
> SRTM flew aboard the Space Shuttle Endeavour in February 2000, mapping Earth's topography between 56 degrees south and 60 degrees north of the equator

_http://www.jpl.nasa.gov/news/news.php?release=2014-321_

Tests
-----

Tests use the following DEM: `_dem/N43E001.hgt` from SRTM.

It can be downloaded from the following link: http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Eurasia/N43E001.hgt.zip

Download, unzip and copy it to the `_dem` folder at the root of the project.

It is also the default DEM when running the tools (specified in the `config.ini` file). It can be changed either in the config file or by command line.

TODO
----

 * Add more tests (as always).
 * Generate graphs with _matplotlib_ or similar
 * Draw the line of sight between elevated points
 * Add some scoring about the probable visibility between two elevated points

Q&A
---

**Q:** Why not use existing tools or websites such as [heywhatsthat](http://www.heywhatsthat.com/), Google Maps or [OpenStreetMap](https://www.openstreetmap.org/)?

**A:** I wanted to propose an alternative that could be completely independent. It could be run on a notebook without an Internet connection if needed.

**Q:** Why python?

**A:** When I searched for elevation profile dev topics on the Internet, I saw a lot of source code written in python, so I choose it to have more support in case of problems. Moreover it was a good occasion to learn python because I'm a newb.

**Q:** What is that name?!? (YunoSeeMe)

**A:** It comes from a popular meme (Y U NO...), the letter case is similar to [YunoHost](https://yunohost.org/). It is the question that these tools try to answer => Why don't you se me? In fact the real question answered is: How well do you see me?

License
-------

All files provided here are licensed under the Simplified BSD "2-Clause" License. See the [LICENSE](LICENSE) file for the complete copyright notice.
