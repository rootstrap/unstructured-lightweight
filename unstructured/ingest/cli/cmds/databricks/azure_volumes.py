import typing as t
from dataclasses import dataclass

import click

from unstructured.ingest.cli.base.src import BaseSrcCmd
from unstructured.ingest.cli.cmds.databricks.base_src import DatabricksSrcCmd
from unstructured.ingest.cli.cmds.databricks.interfaces import (
    AuthConfig,
    DatabricksVolumesWriteConfig,
)

CMD_NAME = "databricks-azure-volumes"


@dataclass
class DatabricksAzureVolumesAuthCliConfig(AuthConfig):
    azure_resource_id: t.Optional[str] = None
    azure_client_secret: t.Optional[str] = None
    azure_client_id: t.Optional[str] = None
    azure_tenant_id: t.Optional[str] = None
    azure_environment: t.Optional[str] = None

    @staticmethod
    def get_cli_options() -> t.List[click.Option]:
        options = [
            click.Option(
                ["--azure-resource-id"],
                type=str,
                default=None,
                help="The Azure Resource Manager ID for the Azure Databricks workspace, "
                "which is exchanged for a Databricks host URL.",
            ),
            click.Option(
                ["--azure-client-secret"],
                type=str,
                default=None,
                help="The Azure AD service principal’s client secret.",
            ),
            click.Option(
                ["--azure-client-id"],
                type=str,
                default=None,
                help="The Azure AD service principal’s application ID.",
            ),
            click.Option(
                ["--azure-tenant-id"],
                type=str,
                default=None,
                help="The Azure AD service principal’s tenant ID.",
            ),
            click.Option(
                ["--azure-environment"],
                type=str,
                default=None,
                help="The Azure environment type (such as Public, UsGov, China, and Germany) "
                "for a specific set of API endpoints. Defaults to PUBLIC.",
            ),
        ]
        return options


def get_base_src_cmd() -> BaseSrcCmd:
    cmd_cls = DatabricksSrcCmd(
        cmd_name=CMD_NAME,
        auth_cli_config=DatabricksAzureVolumesAuthCliConfig,
    )
    return cmd_cls


def get_base_dest_cmd():
    from unstructured.ingest.cli.cmds.databricks.base_dest import DatabricksDestCmd

    cmd_cls = DatabricksDestCmd(
        cmd_name=CMD_NAME,
        auth_cli_config=DatabricksAzureVolumesAuthCliConfig,
        additional_cli_options=[DatabricksVolumesWriteConfig],
    )
    return cmd_cls