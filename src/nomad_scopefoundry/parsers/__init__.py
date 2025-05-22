from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field

class ScopeFoundryH5ParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_scopefoundry.parsers.parser import ScopeFoundryH5Parser

        return ScopeFoundryH5Parser(**self.model_dump())
    
parser_entry_point = ScopeFoundryH5ParserEntryPoint(
    name='ScopeFoundryH5Parser',
    description='ScopeFoundry H5 parser entry point configuration.',
    mainfile_name_re=r'.*\.h5',
)
