from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


# class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
#     parameter: int = Field(0, description='Custom configuration parameter')

#     def load(self):
#         from nomad_scopefoundry.schema_packages.schema_package import m_package

#         return m_package


# schema_package_entry_point = NewSchemaPackageEntryPoint(
#     name='NewSchemaPackage',
#     description='New schema package entry point configuration.',
# )

class ScopeFoundryH5SchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_scopefoundry.schema_packages.scopefoundry_h5_schema import m_package
        return m_package

scopefoundry_h5_schema_entry_point = ScopeFoundryH5SchemaPackageEntryPoint(
    name = 'ScopeFoundry H5 Schema',
    description = 'ScopeFoundry HDF5 schema package.',
)
