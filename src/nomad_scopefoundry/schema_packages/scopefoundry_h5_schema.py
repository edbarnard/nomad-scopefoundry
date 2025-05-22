
import h5py
import yaml
from nomad.metainfo import Quantity, SubSection
from nomad.datamodel import Schema
from nomad.metainfo import SchemaPackage
from nomad.datamodel import EntryArchive
from nomad.datamodel import ArchiveSection
from nomad.datamodel.hdf5 import HDF5Reference
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.eln import BasicEln

import numpy as np

class ScopeFoundryMeasurementData(ArchiveSection):
    name = Quantity(type=str)
    data = Quantity(type=HDF5Reference)

class SFLoggedQuantity(ArchiveSection):
    name = Quantity(type=str)
    value = Quantity(type=str)
    unit = Quantity(type=str)

class ScopeFoundryHW(ArchiveSection):
    name = Quantity(type=str)
    settings = SubSection(section=SFLoggedQuantity, repeats=True, description='list of configuration for hardware')

class ScopeFoundryMeasurement(ArchiveSection):
    name = Quantity(type=str)
    settings = SubSection(section=SFLoggedQuantity, repeats=True, description='list of configuration for measurement')
    datasets = SubSection(section=ScopeFoundryMeasurementData, repeats=True, description='H5 Datasets collected during measurement')

class ScopeFoundryH5(EntryData):
    time_id = Quantity(type=float)
    unique_id = Quantity(type=str, a_eln={'overview':True}, a_display={'visible': True})
    uuid_str = Quantity(type=str)
    app_name = Quantity(type=str, a_eln={'overview':True}, a_display={'visible': True})
    app_settings = SubSection(section=SFLoggedQuantity, repeats=True, description='list of configuration for app')
    hardware = SubSection(section=ScopeFoundryHW, repeats=True, description='Hardware Components', a_display={'visible': True})
    measurement = SubSection(section=ScopeFoundryMeasurement, repeats=True, description='Measurements (usually only one per h5)',a_eln={'overview':True},a_display={'visible': True})

class ScopeFoundryH5ELN(ScopeFoundryH5,BasicEln):

    h5_file = Quantity(
        type=str,
        description='HDF5 file',
        a_eln={
            "component": "FileEditQuantity",
        },
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        """
        The normalize function of the `ScopeFoundryH5` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.

        Reads h5_file and extracts ScopeFoundry data structure
        """
        #parse(mainfile=self.h5_file, archive=archive, logger=logger)
        with archive.m_context.raw_file(self.h5_file, 'rb') as f:
            #raise(IOError(f"{f}"))
            with h5py.File(f,'r') as H:
                h = self
                h.time_id = H.attrs['time_id']
                h.unique_id = H.attrs['unique_id']
                h.uuid_str = H.attrs['uuid']
                h.app_name = H['app'].attrs['name']
                h.app_settings = settingsH5_to_NomadLQlist(H['app/settings'])
                h.hardware = []
                for HW in H['hardware'].values():
                    nHW = ScopeFoundryHW(name=HW.attrs['name'])
                    nHW.settings = settingsH5_to_NomadLQlist(HW['settings'])
                    h.hardware.append(nHW)
                h.measurement = []
                for M in H['measurement'].values():
                    nM = ScopeFoundryMeasurement(name=M.attrs['name'])
                    h.measurement.append(nM)
                    nM.settings = settingsH5_to_NomadLQlist(M['settings'])
                    for name,hData in M.items():
                        if not isinstance(hData, h5py.Dataset): continue
                        nData = ScopeFoundryMeasurementData(name = name)
                        nM.datasets.append(nData)
                        nData.data = f"{self.h5_file}#{hData.name}"


def settingsH5_to_NomadLQlist(sH5):
    lqs = []
    for k,v in sH5.attrs.items():
        lq = SFLoggedQuantity(name=k, value=str(v))
        if k in sH5['units'].attrs:
            lq.unit = sH5['units'].attrs[k]
        lqs.append(lq)
    return lqs

def parse(mainfile, archive, logger):
    with h5py.File(mainfile,'r') as H:
        h = archive.data = ScopeFoundryH5(
            h5_file = mainfile,
            app_name = H['app'].attrs['name']
        )
        h.app_settings = settingsH5_to_NomadLQlist(H['app/settings'])
        for HW in H['hardware'].values():
            nHW = ScopeFoundryHW(name=HW.attrs['name'])
            nHW.settings = settingsH5_to_NomadLQlist(HW['settings'])
            h.hardware.append(nHW)
        for M in H['measurement'].values():
            nM = ScopeFoundryMeasurement(name=M.attrs['name'])
            h.measurement.append(nM)
            nM.settings = settingsH5_to_NomadLQlist(M['settings'])
            for name,hData in M.items():
                if not isinstance(hData, h5py.Dataset): continue
                nData = ScopeFoundryMeasurementData(name = name)
                nM.datasets.append(nData)
                nData.data = f'{mainfile}#{hData.name}'
