import requests
import urllib.parse
import base64
import re
import uuid

# Fetch all wiki pages from Azure DevOps

def get_wiki_pages(organization, project, wiki_name, pat_token):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_name}/pages?api-version=7.1"
    headers = {"Authorization": f"Basic {pat_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

def get_wiki_repo_id(organization, project, wiki_name, pat_token):
    # Get the repositoryId for the wiki
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_name}?api-version=7.1"
    pat_bytes = f":{pat_token}".encode("utf-8")
    pat_base64 = base64.b64encode(pat_bytes).decode("utf-8")
    headers = {"Authorization": f"Basic {pat_base64}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data.get("repositoryId")

# Extract text and image URLs from a wiki page

def extract_text_and_images(page_path, organization, project, wiki_name, pat_token):
    import re
    import uuid
    wiki_name_encoded = urllib.parse.quote(wiki_name, safe='')
    path_encoded = urllib.parse.quote(page_path, safe='')
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_name_encoded}/pages?path={path_encoded}&includeContent=true&api-version=7.1"
    pat_bytes = f":{pat_token}".encode("utf-8")
    pat_base64 = base64.b64encode(pat_bytes).decode("utf-8")
    headers = {"Authorization": f"Basic {pat_base64}"}
    print(f"[DEBUG] Fetching wiki page content: {url}")
    response = requests.get(url, headers=headers)
    print(f"[DEBUG] Raw content response for path {page_path}: {response.text[:500]}...")
    response.raise_for_status()
    data = response.json()
    text = data.get("content", "")
    print(f"[DEBUG] Extracted text (first 500 chars): {text[:500]}")

    # Regex to find all markdown image links: ![alt](url)
    image_pattern = r'!\[.*?\]\((.*?)\)'
    image_links = re.findall(image_pattern, text)
    print(f"[DEBUG] Image links found: {image_links}")
    images = []

    # Get the repositoryId for the wiki
    repo_id = get_wiki_repo_id(organization, project, wiki_name, pat_token)
    print(f"[DEBUG] Wiki repo_id: {repo_id}")

    for img_url in image_links:
        if img_url.startswith("/.attachments/"):
            # Avoid double encoding
            if '%' in img_url:
                attachment_path = img_url
            else:
                attachment_path = urllib.parse.quote(img_url, safe='')
            git_items_url = (
                f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo_id}/Items"
                f"?path={attachment_path}&download=false&resolveLfs=true&%24format=octetStream&api-version=5.0-preview.1"
            )
            filename = img_url.split("/")[-1]
        else:
            git_items_url = img_url
            filename = img_url.split("/")[-1]

        print(f"[DEBUG] Attempting to download image from: {git_items_url}")
        try:
            img_resp = requests.get(git_items_url, headers=headers)
            print(f"[DEBUG] Image download status: {img_resp.status_code}, content length: {len(img_resp.content)}")
            img_resp.raise_for_status()
            img_b64 = base64.b64encode(img_resp.content).decode("utf-8")
            image_id = str(uuid.uuid4())
            images.append({
                "id": image_id,
                "filename": filename,
                "url": img_url,
                "base64": img_b64
            })
            print(f"[DEBUG] Downloaded and encoded image: {img_url} (id: {image_id})")
        except Exception as e:
            print(f"[ERROR] Failed to download image {img_url}: {e}")

    return text, images

# NEW: Extract and combine content from multiple page paths
def extract_all_text_and_images(page_paths, organization, project, wiki_name, pat_token):
    all_text = ""
    all_images = []
    for page_path in page_paths:
        text, images = extract_text_and_images(page_path, organization, project, wiki_name, pat_token)
        all_text += f"\n\n---\n\n# Page: {page_path}\n\n{text}"
        all_images.extend(images)
    return all_text, all_images
