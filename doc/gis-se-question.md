Here is a question I wanted to ask on gis.stackexchange.com but I did not
because I found another way around: using the PROJ.4 syntax.
An example is:

    $ gdal_translate -projwin 3553060.10375 2362727.15004 3669634.65368 2195114.44213 -a_srs "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs" $DOWNLOADS/EUD_CP-DEMS_3500025000-AA.tif $DOWNLOADS/EUD_CP_DEMS_31-AA.tif -co COMPRESS=LZW

Curiously the LZW compression seem to increase the resulting file size ex: 123.1MB (uncompressed) 132.7MB (compressed).

---

### The question:

I want to extract a region from a large GeoTIFF keeping the same transform/spatial ref.

I use the following command:

    $ gdal_translate -projwin 3553060.10375 2362727.15004 3669634.65368 2195114.44213 EUD_CP-DEMS_3500025000-AA.tif out.tif

The command runs well but the output file gives me problems when I want to use its transform data.

When I open it with QGIS, it asks me for the coordinate system (it shouldn't).

When I want to use it with GDAL python bindings I have an error such as the one described in: http://gis.stackexchange.com/questions/48490/how-do-i-solve-a-no-proj-4-translation-error-with-gdal.

I have tried to specify the projection either by the EPSG code or by a WKT file and the result is always the same.

The source file is a [EU-DEM](http://www.eea.europa.eu/data-and-maps/data/eu-dem) file: `EUD_CP-DEMS_3500025000-AA.tif` that uses the `EPSG:3035` spatial ref.

Source file works well, either with QGIS or with GDAL python bindings.

It has the following information:

    $ gdalinfo EUD_CP-DEMS_3500025000-AA.tif
    Driver: GTiff/GeoTIFF
    Files: /.../EUD_CP-DEMS_3500025000-AA.tif
           /.../EUD_CP-DEMS_3500025000-AA.tif.aux.xml
    Size is 40000, 40000
    Coordinate System is:
    PROJCS["JRC-EGCS",
        GEOGCS["ETRS89",
            DATUM["unknown",
                SPHEROID["GRS 1980",6378137,298.2572221000027,
                    AUTHORITY["EPSG","7019"]],
                AUTHORITY["EPSG","6258"]],
            PRIMEM["Greenwich",0],
            UNIT["degree",0.0174532925199433],
            AUTHORITY["EPSG","4258"]],
        PROJECTION["Lambert_Azimuthal_Equal_Area"],
        PARAMETER["latitude_of_center",52],
        PARAMETER["longitude_of_center",10],
        PARAMETER["false_easting",4321000],
        PARAMETER["false_northing",3210000],
        UNIT["metre",1,
            AUTHORITY["EPSG","9001"]],
        AUTHORITY["EPSG","3035"]]
    Origin = (3000000.000000000000000,3000000.000000000000000)
    Pixel Size = (25.000000000000000,-25.000000000000000)
    Metadata:
      AREA_OR_POINT=Area
      TIFFTAG_DATETIME=2013:09:17 21:53:07
      TIFFTAG_DOCUMENTNAME=EUD_CP-DEMS_3500025000-AA.tif
      TIFFTAG_IMAGEDESCRIPTION=File written by egcs_wrgtif 2.1
      TIFFTAG_RESOLUTIONUNIT=2 (pixels/inch)
      TIFFTAG_SOFTWARE=IDL 8.2, Exelis Visual Information Solutions, Inc.
      TIFFTAG_XRESOLUTION=100
      TIFFTAG_YRESOLUTION=100
    Image Structure Metadata:
      COMPRESSION=LZW
      INTERLEAVE=BAND
    Corner Coordinates:
    Upper Left  ( 3000000.000, 3000000.000) (  8d 7'39.52"W, 48d38'23.47"N)
    Lower Left  ( 3000000.000, 2000000.000) (  5d28'46.07"W, 39d52'33.70"N)
    Upper Right ( 4000000.000, 3000000.000) (  5d31' 4.07"E, 50d 1'26.83"N)
    Lower Right ( 4000000.000, 2000000.000) (  6d11'52.97"E, 41d 1'36.49"N)
    Center      ( 3500000.000, 2500000.000) (  0d27' 3.13"W, 45d 5'35.85"N)
    Band 1 Block=40000x1 Type=Float32, ColorInterp=Gray
      Min=-11.800 Max=3149.704
      Minimum=-11.800, Maximum=3149.704, Mean=373.886, StdDev=427.816
      Metadata:
        STATISTICS_MAXIMUM=3149,7043457031
        STATISTICS_MEAN=373,88616978417
        STATISTICS_MINIMUM=-11,800000190735
        STATISTICS_STDDEV=427,81560418455

The generated file has the following information:

    $ gdalinfo out.tif
    Driver: GTiff/GeoTIFF
    Files: out.tif
    Size is 4663, 6705
    Coordinate System is:
    LOCAL_CS["ETRS89 / LAEA Europe",
        GEOGCS["ETRS89",
            DATUM["unknown",
                SPHEROID["unretrievable - using WGS84",6378137,298.257223563],
                TOWGS84[0,0,0,0,0,0,0]],
            PRIMEM["Greenwich",0],
            UNIT["degree",0.0174532925199433]],
        AUTHORITY["EPSG","3035"],
        UNIT["metre",1]]
    Origin = (3553050.000000000000000,2362750.000000000000000)
    Pixel Size = (25.000000000000000,-25.000000000000000)
    Metadata:
      AREA_OR_POINT=Area
      TIFFTAG_DATETIME=2013:09:17 21:53:07
      TIFFTAG_DOCUMENTNAME=EUD_CP-DEMS_3500025000-AA.tif
      TIFFTAG_IMAGEDESCRIPTION=File written by egcs_wrgtif 2.1
      TIFFTAG_RESOLUTIONUNIT=2 (pixels/inch)
      TIFFTAG_SOFTWARE=IDL 8.2, Exelis Visual Information Solutions, Inc.
      TIFFTAG_XRESOLUTION=100
      TIFFTAG_YRESOLUTION=100
    Image Structure Metadata:
      INTERLEAVE=BAND
    Corner Coordinates:
    Upper Left  ( 3553050.000, 2362750.000)
    Lower Left  ( 3553050.000, 2195125.000)
    Upper Right ( 3669625.000, 2362750.000)
    Lower Right ( 3669625.000, 2195125.000)
    Center      ( 3611337.500, 2278937.500)
    Band 1 Block=4663x1 Type=Float32, ColorInterp=Gray

It has a LOCAL_CS instead of the expected PROJCS.
It misses a lot of information such as PROJECTION and PARAMETER and the SPHEROID is wrong.

I tried to gdalwarp it but I always have the same output.

I feel that the problem comes from `gdal_translate`, when it writes it, it seems to loose some informations. Funny thing is that everything is in the source file and displays well in `gdalinfo`.

I have the openSUSE version of GDAL from the Application:Geo repository: `1.11.2-16.2`

A minor problem also is the LZW compression that is missing in the output file. Is there a way to specify it to gdal_translate?
