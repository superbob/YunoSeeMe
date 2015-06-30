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

For MacOS, used (GDAL-Complete) Frameworks provided by http://www.kyngchaos.com/software:frameworks

Installed python modules in virtual env (--no-site-packages):

 * numpy
 * gdal
 * cherrypy (web.py didn't work well)
