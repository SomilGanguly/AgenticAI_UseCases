import xml.etree.ElementTree as ET
from fastapi import FastAPI
from fastmcp import FastMCP
from migrate_client import get_assessment_report_url
from utils import download_file
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()
mcp = FastMCP("azure_migrate")

@mcp.custom_route("/", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Azure Migrate MCP is running", status_code=200)

@mcp.tool
async def fetch_assessment_report_url(
    resource_group: str,
    project_name: str,
    group_name: str,
    assessment_name: str,
    download: bool = False,
    download_path: str = "assessment_report2.xlsx",
) -> str:
    """Fetches the Azure Migrate assessment report URL and optionally downloads the report."""
    
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

    report_url = await get_assessment_report_url(
        subscription_id,
        resource_group,
        project_name,
        group_name,
        assessment_name,
    )

    if download:
        await download_file(report_url, download_path)

    return report_url

@mcp.tool
def generate_visio_xml_from_migration(migration_plan: list) -> str:
    """
    Generate Visio XML from migration plan.
    """

    def create_shape(shape_id, name, x, y):
        shape = ET.Element("Shape", ID=str(shape_id), Name=name, Type="Shape")
        xform = ET.SubElement(shape, "XForm")
        ET.SubElement(xform, "PinX").text = str(x)
        ET.SubElement(xform, "PinY").text = str(y)
        text = ET.SubElement(shape, "Text")
        text.text = name
        return shape

    visio_xml = ET.Element("VisioDocument", xmlns="http://schemas.microsoft.com/office/visio/2003/core")

    # Add Pages
    pages = ET.SubElement(visio_xml, "Pages")
    page = ET.SubElement(pages, "Page", ID="1", Name="Migration Diagram")
    shapes = ET.SubElement(page, "Shapes")

    x = 1.0
    y = 5.0
    shape_id = 1
    connections = []

    for migration in migration_plan:
        # Source
        source_shape = create_shape(shape_id, migration["source"], x, y)
        shapes.append(source_shape)
        src_id = shape_id
        shape_id += 1

        # Target
        target_shape = create_shape(shape_id, migration["target"], x + 3, y)
        shapes.append(target_shape)
        tgt_id = shape_id
        shape_id += 1

        # Connectors (you can later expand this to use Connects section properly)
        connection = ET.Element("Connect", FromSheet=str(src_id), ToSheet=str(tgt_id), FromCell="EndX", ToCell="BeginX")
        connections.append(connection)

        y -= 1.5  # shift Y for next row

    # Add Connections
    connects = ET.SubElement(page, "Connects")
    for conn in connections:
        connects.append(conn)

    # Output XML string
    xml_str = ET.tostring(visio_xml, encoding="utf-8", method="xml").decode("utf-8")
    return xml_str


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=4200,
        path="/mcp",
        log_level="debug",
    )