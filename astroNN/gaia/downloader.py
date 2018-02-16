# ---------------------------------------------------------#
#   astroNN.gaia.downloader: download gaia files
# ---------------------------------------------------------#

import os
import urllib.request
from functools import reduce

import astroNN
import numpy as np
from astroNN.gaia.gaia_shared import gaia_env, gaia_default_dr
from astroNN.shared.downloader_tools import TqdmUpTo, md5_checksum
from astropy.io import fits

currentdir = os.getcwd()
_GAIA_DATA = gaia_env()


def tgas(dr=None, flag=None):
    """
    NAME:
        tgas
    PURPOSE:
        download the tgas files
    INPUT:
        dr (int): GAIA DR, example dr=1
    OUTPUT:
        list of file path
    HISTORY:
        2017-Oct-13 - Written - Henry Leung (University of Toronto)
    """

    # Check if dr arguement is provided, if none then use default
    dr = gaia_default_dr(dr=dr)
    fulllist = []

    if dr == 1:
        # Check if directory exists
        folderpath = os.path.join(_GAIA_DATA, 'Gaia/tgas_source/fits/')
        urlbase = 'http://cdn.gea.esac.esa.int/Gaia/tgas_source/fits/'

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        hash_filename = 'MD5SUM.txt'
        full_hash_filename = os.path.join(folderpath, hash_filename)
        if not os.path.isfile(full_hash_filename):
            urllib.request.urlretrieve(urlbase + hash_filename, full_hash_filename)

        hash_list = np.loadtxt(full_hash_filename, dtype='str').T

        for i in range(0, 16, 1):
            filename = 'TgasSource_000-000-0{:02d}.fits'.format(i)
            fullfilename = os.path.join(folderpath, filename)
            urlstr = urlbase + filename

            # Check if files exists
            if os.path.isfile(fullfilename) and flag is None:
                checksum = md5_checksum(fullfilename)
                # In some rare case, the hash cant be found, so during checking, check len(file_has)!=0 too
                file_hash = (hash_list[0])[np.argwhere(hash_list[1] == filename)]
                if checksum != file_hash and len(file_hash) != 0:
                    print(checksum)
                    print(file_hash)
                    print('File corruption detected, astroNN attempting to download again')
                    tgas(dr=dr, flag=1)
                else:
                    print(fullfilename + ' was found!')

            elif not os.path.isfile(fullfilename) or flag == 1:
                # progress bar
                with TqdmUpTo(unit='B', unit_scale=True, miniters=1, desc=urlstr.split('/')[-1]) as t:
                    # Download
                    urllib.request.urlretrieve(urlstr, fullfilename, reporthook=t.update_to)
                    checksum = md5_checksum(fullfilename)
                    if checksum != file_hash and len(file_hash) != 0:
                        print('File corruption detected, astroNN attempting to download again')
                        tgas(dr=dr, flag=1)
                print('Downloaded Gaia DR{:d} TGAS ({:d} of 15) file catalog successfully to {}'.format(dr, i,
                                                                                                        fullfilename))
            fulllist.extend([fullfilename])
    else:
        raise ValueError('tgas() only supports Gaia DR1 TGAS')

    return fulllist


def tgas_load(dr=None, filter=True):
    """
    NAME:
        tgas_load
    PURPOSE:
        to load useful parameters from multiple TGAS files
    INPUT:
        dr (int): Gaia DR, example dr=1
        filter (boolean): Whether to filter bad data (negative parallax and percentage error more than 20%)
    OUTPUT:
    HISTORY:
        2017-Dec-17 - Written - Henry Leung (University of Toronto)
    """
    dr = gaia_default_dr(dr=dr)
    tgas_list = tgas(dr=dr)

    ra = np.array([])
    dec = np.array([])
    pmra_gaia = np.array([])
    pmdec_gaia = np.array([])
    parallax_gaia = np.array([])
    parallax_error_gaia = np.array([])
    g_band_gaia = np.array([])

    for i in tgas_list:
        gaia = fits.open(i)
        ra = np.concatenate((ra, gaia[1].data['RA']))
        dec = np.concatenate((dec, gaia[1].data['DEC']))
        pmra_gaia = np.concatenate((pmra_gaia, gaia[1].data['PMRA']))
        pmdec_gaia = np.concatenate((pmdec_gaia, gaia[1].data['PMDEC']))
        parallax_gaia = np.concatenate((parallax_gaia, gaia[1].data['parallax']))
        parallax_error_gaia = np.concatenate((parallax_error_gaia, gaia[1].data['parallax_error']))
        g_band_gaia = np.concatenate((g_band_gaia, gaia[1].data['phot_g_mean_mag']))
        gaia.close()

    if filter is True:
        filtered_err_idx = np.where(parallax_error_gaia / parallax_gaia < 0.2)
        filtered_neg_idx = np.where(parallax_gaia > 0.)
        filtered_index = reduce(np.intersect1d, (filtered_err_idx, filtered_neg_idx))

        ra = ra[filtered_index]
        dec = dec[filtered_index]
        pmra_gaia = pmra_gaia[filtered_index]
        pmdec_gaia = pmdec_gaia[filtered_index]
        parallax_gaia = parallax_gaia[filtered_index]
        parallax_error_gaia = parallax_error_gaia[filtered_index]
        g_band_gaia = g_band_gaia[filtered_index]

    return {'ra': ra, 'dec': dec, 'pmra': pmra_gaia, 'pmdec': pmdec_gaia, 'parallax': parallax_gaia,
            'parallax_err': parallax_error_gaia, 'gmag': g_band_gaia}


def gaia_source(dr=None, flag=None):
    """
    NAME:
        gaia_source
    PURPOSE:
        download the gaia_source files
    INPUT:
        dr (int): Gaia DR, example dr=1
    OUTPUT:
        list of file path
    HISTORY:
        2017-Oct-13 - Written - Henry Leung (University of Toronto)
        2017-Nov-26 - Update - Henry Leung (University of Toronto)
    """
    dr = gaia_default_dr(dr=dr)
    fulllist = []

    if dr == 1:

        # Check if directory exists
        folderpath = os.path.join(_GAIA_DATA, 'Gaia/tgas_source/fits/')
        urlbase = 'http://cdn.gea.esac.esa.int/Gaia/gaia_source/fits/'

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        hash_filename = 'MD5SUM.txt'
        full_hash_filename = os.path.join(folderpath, hash_filename)
        if not os.path.isfile(full_hash_filename):
            urllib.request.urlretrieve(urlbase + hash_filename, full_hash_filename)

        hash_list = np.loadtxt(full_hash_filename, dtype='str').T

        for j in range(0, 20, 1):
            for i in range(0, 256, 1):
                filename = 'GaiaSource_000-0{:02d}-{:03d}.fits'.format(j, i)
                urlstr = urlbase + filename

                fullfilename = os.path.join(folderpath, filename)

                # Check if files exists
                if os.path.isfile(fullfilename) and flag is None:
                    checksum = md5_checksum(fullfilename)
                    # In some rare case, the hash cant be found, so during checking, check len(file_has)!=0 too
                    file_hash = (hash_list[0])[np.argwhere(hash_list[1] == filename)]
                    if checksum != file_hash and len(file_hash) != 0:
                        print(checksum)
                        print(file_hash)
                        print('File corruption detected, astroNN attempting to download again')
                        gaia_source(dr=dr, flag=1)
                    else:
                        print(fullfilename + ' was found!')
                elif not os.path.isfile(fullfilename) or flag == 1:
                    # progress bar
                    with TqdmUpTo(unit='B', unit_scale=True, miniters=1, desc=urlstr.split('/')[-1]) as t:
                        urllib.request.urlretrieve(urlstr, fullfilename, reporthook=t.update_to)
                        checksum = md5_checksum(fullfilename)
                        if checksum != file_hash and len(file_hash) != 0:
                            print('File corruption detected, astroNN attempting to download again')
                            gaia_source(dr=dr, flag=1)
                    print('Downloaded Gaia DR{:d} Gaia Source ({:d} of {:d}) file catalog successfully to {}') % (
                        dr, (j * 256 + i), 256 * 20 + 112, fullfilename)
                fulllist.extend([fullfilename])

        for i in range(0, 111, 1):
            filename = 'GaiaSource_000-020-{:03d}.fits'.format(i)
            urlstr = urlbase + filename

            fullfilename = os.path.join(folderpath, filename)

            # Check if files exists
            if os.path.isfile(fullfilename) and flag is None:
                checksum = md5_checksum(fullfilename)
                # In some rare case, the hash cant be found, so during checking, check len(file_has)!=0 too
                file_hash = (hash_list[0])[np.argwhere(hash_list[1] == filename)]
                if checksum != file_hash and len(file_hash) != 0:
                    print(checksum)
                    print(file_hash)
                    print('File corruption detected, astroNN attempting to download again')
                    gaia_source(dr=dr, flag=1)
                else:
                    print(fullfilename + ' was found!')
            elif not os.path.isfile(fullfilename) or flag == 1:
                # progress bar
                with TqdmUpTo(unit='B', unit_scale=True, miniters=1, desc=urlstr.split('/')[-1]) as t:
                    urllib.request.urlretrieve(urlstr, fullfilename, reporthook=t.update_to)
                    checksum = md5_checksum(fullfilename)
                    if checksum != file_hash and len(file_hash) != 0:
                        print('File corruption detected, astroNN attempting to download again')
                        gaia_source(dr=dr, flag=1)
                    print('Downloaded Gaia DR{:d} Gaia Source ({:d} of {:d}) file catalog successfully to {}') % (
                        dr, (20 * 256 + i), 256 * 20 + 112, currentdir)
            fulllist.extend([fullfilename])

    else:
        raise ValueError('gaia_source() only supports Gaia DR1 Gaia Source')

    return fulllist


def anderson_2017_parallax(filter=True):
    """
    NAME:
        anderson_2017_parallax
    PURPOSE:
        download Anderson et al 2017 improved parallax from data-driven stars model
    INPUT:
        filter (boolean): whether to filter those parallax err larger than 20% or not
    OUTPUT:
        ra (ndarray)
        dec (ndarray)
        parallax (ndarray): parallax in mas
        parallax_err (ndarray): 1-standard derivation parallax error in mas
    HISTORY:
        2017-Dec-22 - Written - Henry Leung (University of Toronto)
    """
    fullfilename = os.path.join(os.path.dirname(astroNN.__path__[0]), 'astroNN', 'data', 'anderson_2017_parallax.npz')
    print(
        'anderson_2017_parallax: Original dataset at: http://voms.simonsfoundation.org:50013/8kM7XXPCJleK2M02B9E7YIYmvu5l2rh/ServedFiles/')

    hdu = np.load(fullfilename)
    ra = hdu['ra']
    dec = hdu['dec']
    parallax = hdu['parallax']
    parallax_err = hdu['parallax_err']

    if filter is True:
        good_index = [parallax_err / parallax < 0.2]
        ra = ra[good_index]
        dec = dec[good_index]
        parallax = parallax[good_index]
        parallax_err = parallax_err[good_index]
    return ra, dec, parallax, parallax_err
