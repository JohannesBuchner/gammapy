# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
from regions import CircleSkyRegion
from gammapy.data import DataStore
from gammapy.spectrum import SpectrumDatasetMaker
from gammapy.utils.testing import requires_data


@pytest.fixture
def observations_hess_dl3():
    """HESS DL3 observation list."""
    datastore = DataStore.from_file(
        "$GAMMAPY_DATA/hess-dl3-dr1/hess-dl3-dr3-with-background.fits.gz"
    )
    obs_ids = [23523, 23526]
    return datastore.get_observations(obs_ids)


@pytest.fixture
def observations_cta_dc1():
    """CTA DC1 observation list."""
    datastore = DataStore.from_dir("$GAMMAPY_DATA/cta-1dc/index/gps/")
    obs_ids = [110380, 111140]
    return datastore.get_observations(obs_ids)


@pytest.fixture()
def spectrum_dataset_maker_gc():
    pos = SkyCoord(0.0, 0.0, unit="deg", frame="galactic")
    radius = Angle(0.11, "deg")
    region = CircleSkyRegion(pos, radius)

    e_reco = np.logspace(0, 2, 5) * u.TeV
    e_true = np.logspace(-0.5, 2, 11) * u.TeV
    return SpectrumDatasetMaker(region=region, e_reco=e_reco, e_true=e_true)


@pytest.fixture()
def spectrum_dataset_maker_crab():
    pos = SkyCoord(83.63, 22.01, unit="deg", frame="icrs")
    radius = Angle(0.11, "deg")
    region = CircleSkyRegion(pos, radius)
    e_reco = np.logspace(0, 2, 5) * u.TeV
    e_true = np.logspace(-0.5, 2, 11) * u.TeV
    return SpectrumDatasetMaker(region=region, e_reco=e_reco, e_true=e_true)


@requires_data()
def test_spectrum_dataset_maker_hess_dl3(
    spectrum_dataset_maker_crab, observations_hess_dl3
):
    datasets = []

    for obs in observations_hess_dl3:
        dataset = spectrum_dataset_maker_crab.run(obs)
        datasets.append(dataset)

    assert_allclose(datasets[0].counts.data.sum(), 100)
    assert_allclose(datasets[1].counts.data.sum(), 92)

    assert_allclose(datasets[0].livetime.value, 1581.736758)
    assert_allclose(datasets[1].livetime.value, 1572.686724)

    assert_allclose(datasets[0].background.data.sum(), 1.737258, rtol=1e-5)
    assert_allclose(datasets[1].background.data.sum(), 1.741604, rtol=1e-5)


@requires_data()
def test_spectrum_dataset_maker_hess_cta(
    spectrum_dataset_maker_gc, observations_cta_dc1
):
    datasets = []

    for obs in observations_cta_dc1:
        dataset = spectrum_dataset_maker_gc.run(obs)
        datasets.append(dataset)

    assert_allclose(datasets[0].counts.data.sum(), 53)
    assert_allclose(datasets[1].counts.data.sum(), 47)

    assert_allclose(datasets[0].livetime.value, 1764.000034)
    assert_allclose(datasets[1].livetime.value, 1764.000034)

    assert_allclose(datasets[0].background.data.sum(), 2.238345, rtol=1e-5)
    assert_allclose(datasets[1].background.data.sum(), 2.164593, rtol=1e-5)