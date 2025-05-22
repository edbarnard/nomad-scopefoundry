from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.parsing.parser import MatchingParser

configuration = config.get_plugin_entry_point(
    'nomad_scopefoundry.parsers:parser_entry_point'
)

from nomad_scopefoundry.schema_packages.scopefoundry_h5_schema import (
    ScopeFoundryH5, ScopeFoundryHW, 
    ScopeFoundryMeasurement, 
    settingsH5_to_NomadLQlist,
    ScopeFoundryMeasurementData)


# class NewParser(MatchingParser):
#     def parse(
#         self,
#         mainfile: str,
#         archive: 'EntryArchive',
#         logger: 'BoundLogger',
#         child_archives: dict[str, 'EntryArchive'] = None,
#     ) -> None:
#         logger.info('NewParser.parse', parameter=configuration.parameter)

#         archive.workflow2 = Workflow(name='test')

class ScopeFoundryH5Parser(MatchingParser):

    def parse(
        self, mainfile: str, archive: 'EntryArchive', logger=None, child_archives=None
    ) -> None:

        import h5py
        import os

        with open(mainfile, 'rb') as f:
            #raise(IOError(f"{f}"))
            with h5py.File(f,'r') as H:
                h = ScopeFoundryH5()
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
                        nData.data = f"{os.path.split(mainfile)[-1]}#{hData.name}"

        archive.data = h