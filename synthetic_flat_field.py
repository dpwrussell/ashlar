from __future__ import division
import sys
import bioformats
import javabridge
import numpy as np
import scipy.ndimage
import skimage.io


javabridge.start_vm(class_path=bioformats.JARS)
# Hack module to fix py3 assumptions which break XML parsing.
bioformats.omexml.str = unicode


paths = sys.argv[1:]

metadata0 = bioformats.OMEXML(bioformats.get_omexml_metadata(paths[0]))
mpixels0 = metadata0.image().Pixels
n_channels = mpixels0.SizeC
sx = mpixels0.SizeX
sy = mpixels0.SizeY

sum = np.zeros([n_channels, sy, sx])

for path in paths:

    metadata = bioformats.OMEXML(bioformats.get_omexml_metadata(path))
    mpixels = metadata.image().Pixels
    assert mpixels.SizeC == n_channels
    assert mpixels.SizeX == sx
    assert mpixels.SizeY == sy
    n_images = metadata.image_count
    ir = bioformats.ImageReader(path)

    print '>>>', path
    for i in range(n_images):
        print "\r  %d/%d" % (i+1, n_images),
        sys.stdout.flush()
        for c in range(n_channels):
            img = ir.read(c=c, series=i, rescale=False)
            sum[c] += img
    print

ff = sum / sum.reshape([n_channels, -1]).max(1).reshape([n_channels, 1, 1])
ff = (ff * 65536).astype('i2')

for c in range(n_channels):
    skimage.io.imsave('flat_field_ch%d.tif' % c, ff[c])

#javabridge.kill_vm()