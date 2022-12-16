import os

from unittest import mock

import intake
import numpy as np
import pandas as pd
import pytest

import ocean_model_skill_assessor as omsa


@mock.patch("ocean_model_skill_assessor.CAT_PATH")
def test_make_catalog_local(mock_cat_path, tmpdir):

    catloc2 = tmpdir / "projectA" / "catAlocal.yaml"
    mock_cat_path.return_value = catloc2

    kwargs = {"filenames": "filename.csv", "skip_entry_metadata": True}
    cat1 = omsa.make_catalog(
        catalog_type="local",
        project_name="projectA",
        catalog_name="catAlocal",
        description="test local description",
        kwargs=kwargs,
        return_cat=True,
        save_cat=True,
    )
    assert os.path.exists(catloc2)
    assert list(cat1) == ["filename"]
    assert cat1.name == "catAlocal"
    assert cat1["filename"].urlpath == "filename.csv"
    assert cat1["filename"].describe()["driver"] == ["csv"]
    assert cat1.description == "test local description"

    cat2 = intake.open_catalog(catloc2)
    assert cat1["filename"].describe() == cat2["filename"].describe()

    kwargs = {"filenames": "filenamenc.nc", "skip_entry_metadata": True}
    cat3 = omsa.make_catalog(
        catalog_type="local",
        project_name="projectA",
        catalog_name="catAlocal",
        description="test local description",
        kwargs=kwargs,
        return_cat=True,
        save_cat=False,
    )
    assert cat3["filenamenc"].urlpath == "filenamenc.nc"
    assert cat3["filenamenc"].describe()["driver"] == ["netcdf"]

    kwargs = {
        "filenames": ["filenamenc.nc", "filename.csv"],
        "skip_entry_metadata": True,
    }
    cat4 = omsa.make_catalog(
        catalog_type="local",
        project_name="projectA",
        catalog_name="catAlocal",
        description="test local description",
        kwargs=kwargs,
        return_cat=True,
        save_cat=False,
    )
    assert sorted(list(cat4)) == ["filename", "filenamenc"]

    with pytest.raises(ValueError):
        omsa.make_catalog(
            catalog_type="local",
            project_name="projectA",
        )


@mock.patch("intake.source.csv.CSVSource.read")
def test_make_catalog_local_read(read):

    source = intake.open_csv("filename.csv")

    df = pd.DataFrame(
        data={"time": np.arange(9), "longitude": np.arange(9), "latitude": np.arange(9)}
    )
    read.return_value = df

    kwargs = {"filenames": "filename.csv", "skip_entry_metadata": False}
    cat = omsa.make_catalog(
        catalog_type="local",
        project_name="projectA",
        kwargs=kwargs,
        return_cat=True,
        save_cat=False,
    )
    assert cat["filename"].metadata["minLongitude"] == 0.0
    assert cat["filename"].metadata["maxLatitude"] == 8.0
    assert cat["filename"].metadata["minTime"] == "0"