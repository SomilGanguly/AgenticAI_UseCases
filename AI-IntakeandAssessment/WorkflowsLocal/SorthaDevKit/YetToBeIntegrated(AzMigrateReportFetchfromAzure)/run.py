from fastmcp import Client
import asyncio
import traceback
import zipfile
import os
import asyncio
import tempfile
import shutil
import win32com.client

async def main():
    async with Client("http://127.0.0.1:4200/mcp") as client:
        try:
            # result = await client.call_tool("fetch_assessment_report_url", {
            #     "resource_group": "blueberry-bluebird",
            #     "project_name": "bluebird-vm9650project",
            #     "group_name": "aws-assessment",
            #     "assessment_name": "aws-yellowtail-assessment",
            #     "download": True
            # })

            visio_result = await client.call_tool("generate_visio_xml_from_migration", {
            "migration_plan": [
                {
                "source": "OnPrem-VM1",
                "target": "Azure-VM1",
                "type": "VirtualMachine"
                },
                {
                "source": "OnPrem-DB",
                "target": "Azure-SQL",
                "type": "Database"
                }
            ]
            }) 
            xml_string = visio_result.data

            with open("migration_diagram.vdx", "w", encoding="utf-8") as f:
                f.write(xml_string)

            print("Visio XML Result:", visio_result)
            temp_dir = tempfile.mkdtemp()
            visio_folder = os.path.join(temp_dir, "visio")
            os.makedirs(visio_folder, exist_ok=True)

            # Save Drawing.xml (the core content)
            drawing_path = os.path.join(visio_folder, "drawing.xml")
            with open(drawing_path, "w", encoding="utf-8") as f:
                f.write(xml_string)

            # [Minimal .vsdx structure] — Create [Content_Types].xml and _rels
            content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
        <Override PartName="/visio/drawing.xml" ContentType="application/vnd.ms-visio.drawing.main+xml"/>
        </Types>'''

            rels_dir = os.path.join(temp_dir, "_rels")
            os.makedirs(rels_dir, exist_ok=True)
            rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        </Relationships>'''

            with open(os.path.join(temp_dir, "[Content_Types].xml"), "w", encoding="utf-8") as f:
                f.write(content_types)

            with open(os.path.join(rels_dir, ".rels"), "w", encoding="utf-8") as f:
                f.write(rels_xml)

            # Step 2: Zip everything to .vsdx
            vsdx_path = os.path.abspath("migration_diagram.vsdx")
            with zipfile.ZipFile(vsdx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, temp_dir)
                        zf.write(abs_path, rel_path)

            # Cleanup temp
            shutil.rmtree(temp_dir)

            print(f"Saved diagram to: {vsdx_path}")

            # Step 3: Open in Visio Desktop
            visio = win32com.client.Dispatch("Visio.Application")
            visio.Visible = True
            visio.Documents.Open(vsdx_path)
            print("Opened in Visio!")

            # print("Download URL:", result)
        except Exception as e:
            print("Tool failed with exception:")
            print(e)
            traceback.print_exc()


asyncio.run(main())
