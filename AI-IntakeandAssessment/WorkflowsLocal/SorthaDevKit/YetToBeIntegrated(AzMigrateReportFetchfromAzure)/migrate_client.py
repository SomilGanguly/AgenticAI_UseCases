import httpx
from azure_auth import get_azure_token

async def get_assessment_report_url(subscription_id: str, resource_group: str, project_name: str,
                                     group_name: str, assessment_name: str) -> str:
    token = await get_azure_token()

    url = (f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/assessmentProjects/{project_name}/groups/{group_name}/assessments/{assessment_name}/downloadUrl?api-version=2024-01-15")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("🧾 Headers:", headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        print(response.text)  # Debugging line to see the response content
        response.raise_for_status()
        return response.json().get("assessmentReportUrl")


