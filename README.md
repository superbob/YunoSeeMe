This is a collection of tools to compute elevation profiles.

It makes an extensive use of GDAL to handle DEM files to get elevation data from.

Installed native libraries:

 * python utilities
   * python-virtualenv
   * python-pip --> Maybe useless since I end up using easy_install
 * NumPy
   * python-numpy --> Maybe useless since they provide python code that was fetched in the virtualenv using easy_install
   * python-numpy-devel --> ???
 * PROJ
   * libproj-devel --> Headers required for compiling by projection tools (osr stuff)
   * libproj0 --> Libs required for linking (already present in the system, maybe useless)
   * libproj9 --> Libs required for linking
 * GDAL
   * gdal --> Binaries (already present in the system, useful to do `gdalinfo` on GeoTIFF images)
   * gdal-devel --> Headers required for compiling
   * libgdal1 -->
   * python-gdal

For MacOS, used the GDAL Complete Framework provided by http://www.kyngchaos.com/software:frameworks

Copied gdal python binding from /Library/Frameworks/GDAL.framework/... to virtualenv

Installed python modules in virtual env (--no-site-packages):

 * numpy
 * gdal
 * cherrypy (web.py didn't work well)
 * pytest
