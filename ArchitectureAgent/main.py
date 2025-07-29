from architecture_agent.config import *
from architecture_agent.ado_wiki_extractor import get_wiki_pages, extract_text_and_images
from architecture_agent.image_extractor import analyze_architecture_with_gpt4o
from architecture_agent.Agent_integration import analyze_with_foundry_agent
import requests
import base64


import urllib.parse

def get_pat_header(pat_token):
    pat_token = pat_token.replace('"', '')  # Remove quotes if present
    pat_bytes = f":{pat_token}".encode("utf-8")
    pat_base64 = base64.b64encode(pat_bytes).decode("utf-8")
    return {"Authorization": f"Basic {pat_base64}"}

def get_wiki_list(organization, project, pat_token):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis?api-version=7.1"
    headers = get_pat_header(pat_token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

def extract_wiki_name_or_id_from_url(project_url, pat_token):
    """
    Given a project URL, fetches the list of wikis and returns the best match (name or id).
    """
    # Example project_url: https://dev.azure.com/org/project/_wiki/wikis/wiki-name
    # Parse organization and project from URL
    try:
        parts = urllib.parse.urlparse(project_url)
        path_parts = parts.path.strip("/").split("/")
        organization = path_parts[0]
        project = path_parts[1]
    except Exception:
        raise ValueError("Could not parse organization/project from URL.")

    wikis = get_wiki_list(organization, project, pat_token)
    # If only one wiki, return its name or id
    if len(wikis) == 1:
        return organization, project, wikis[0].get("name") or wikis[0].get("id")
    # Try to match wiki name from URL
    for wiki in wikis:
        if "wiki-name" in project_url and wiki.get("name") in project_url:
            return organization, project, wiki.get("name")
    # Fallback: return first wiki name
    if wikis:
        return organization, project, wikis[0].get("name") or wikis[0].get("id")
    raise ValueError("No wiki found for this project.")

def parse_url(project_url):
    return extract_wiki_name_or_id_from_url(project_url, ADO_PAT_TOKEN)


def get_all_page_paths(organization, project, wiki_name, pat_token):
    """
    Recursively fetch all page paths from a wiki using the subPages tree.
    """
    import urllib.parse
    wiki_name_encoded = urllib.parse.quote(wiki_name, safe='')
    # Add recursionLevel=all to get all subpages
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_name_encoded}/pages?includeContent=false&recursionLevel=full&api-version=7.1"
    pat_bytes = f":{pat_token}".encode("utf-8")
    pat_base64 = base64.b64encode(pat_bytes).decode("utf-8")
    headers = {"Authorization": f"Basic {pat_base64}"}
    response = requests.get(url, headers=headers)
    print("[DEBUG] Wiki pages list URL:", url)
    print("[DEBUG] Raw response:", response.text)
    response.raise_for_status()
    data = response.json()

    def collect_paths(page):
        paths = []
        if "path" in page:
            paths.append(page["path"])
        for subpage in page.get("subPages", []):
            paths.extend(collect_paths(subpage))

        print("[DEBUG] paths are:", paths)
        return paths

    # The root response is a single page with possible subPages
    all_paths = collect_paths(data)
    return all_paths

def get_all_wiki_page_paths(organization, project, pat_token):
    """Fetch all page paths from all wikis in the project."""
    all_page_paths = []
    wikis = get_wiki_list(organization, project, pat_token)
    print(f"Found {len(wikis)} wikis in project.")
    for wiki in wikis:
        wiki_name_or_id = wiki.get("name") or wiki.get("id")
        print(f"Fetching page paths for wiki: {wiki_name_or_id}")
        page_paths = get_all_page_paths(organization, project, wiki_name_or_id, pat_token)
        print(f"  Page paths found: {len(page_paths)}")
        all_page_paths.extend([(wiki_name_or_id, path) for path in page_paths])
    return all_page_paths

def main(project_url):
    organization, project, wiki_name_or_id = parse_url(project_url)
    print(f"Organization: {organization}, Project: {project}, Wiki: {wiki_name_or_id}")
    page_tuples = get_all_wiki_page_paths(organization, project, ADO_PAT_TOKEN)
    print(f"Total pages found: {len(page_tuples)}")
    if not page_tuples:
        print("No wiki pages found. Check your wiki name/id and permissions.")
        return
    # kernel = create_kernel(FOUNDRY_PROJECT_ID, FOUNDRY_AGENT_NAME, OPENAI_API_KEY)
    for wiki_name, page_path in page_tuples:
        print(f"Processing page: {page_path} (wiki: {wiki_name})")
        text, images = extract_text_and_images(page_path, organization, project, wiki_name, ADO_PAT_TOKEN)
        print(f"[DEBUG] Extracted text for page {page_path} (first 500 chars):\n{text[:500]}\n---")
        print(f"[DEBUG] Extracted images for page {page_path}:")
        image_descriptions = [analyze_architecture_with_gpt4o(img, VISION_ENDPOINT, VISION_API_KEY) for img in images]
        print(f"[DEBUG] Image descriptions for page {page_path}: {image_descriptions}")
        # Skip analyze_with_foundry_agent if both text and image_descriptions are empty
        if (not text.strip()) and (not any(desc.strip() for desc in image_descriptions)):
            print(f"[INFO] Skipping page {page_path} as both text and image data are empty.")
            continue
        result = analyze_with_foundry_agent(text, image_descriptions, FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_AGENT_ID)
        print(f"Page: {page_path}\nResult: {result}\n")


def get_wiki_pages(organization, project, wiki_name, pat_token):
    import urllib.parse
    wiki_name_encoded = urllib.parse.quote(wiki_name, safe='')
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_name_encoded}/pages?api-version=7.1"
    # Correct Basic Auth header
    pat_bytes = f":{pat_token}".encode("utf-8")
    pat_base64 = base64.b64encode(pat_bytes).decode("utf-8")
    headers = {"Authorization": f"Basic {pat_base64}"}
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json().get("value", [])
    except Exception as e:
        print("Error fetching wiki pages:")
        print("Status code:", response.status_code)
        print("Response text:", response.text)
        raise


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python main.py <project_url>")
