import azure.functions as func
import logging
import json
import os
import sys

# Add the parent directories to the Python path to import your tools
# This adds the ArchitectureAgent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="wikiDataExtractor", methods=["POST"])
def wiki_data_extractor(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Wiki Data Extractor function processing a request.')
    try:
        req_body = req.get_json()
        project_url = req_body.get('project_url')
        if not project_url:
            return func.HttpResponse(
                json.dumps({"error": "Please provide a project_url"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Import from ArchitectureAgent tools - corrected path
        from tools.ado_wiki_extractor import extract_wiki_subtree_content
        from tools.image_extractor import analyze_architecture_with_gpt4o
        
        ADO_PAT_TOKEN = os.environ.get("ADO_PAT_TOKEN")
        VISION_ENDPOINT = os.environ.get("VISION_ENDPOINT")
        VISION_API_KEY = os.environ.get("VISION_API_KEY")
        
        if not all([ADO_PAT_TOKEN, VISION_ENDPOINT, VISION_API_KEY]):
            return func.HttpResponse(
                json.dumps({"error": "Missing required environment variables"}),
                status_code=500,
                mimetype="application/json"
            )
        
        all_text, all_images = extract_wiki_subtree_content(project_url, ADO_PAT_TOKEN)
        image_descriptions = []
        for img in all_images:
            try:
                description = analyze_architecture_with_gpt4o(img, VISION_ENDPOINT, VISION_API_KEY)
                image_descriptions.append(description)
            except Exception as e:
                logging.error(f"Error analyzing image: {str(e)}")
                image_descriptions.append(f"Error analyzing image: {str(e)}")
        
        result = {
            "text": all_text,
            "image_descriptions": image_descriptions,
            "total_images": len(all_images),
            "status": "success"
        }
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error in wiki_data_extractor: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "failed"}),
            status_code=500,
            mimetype="application/json"
        )