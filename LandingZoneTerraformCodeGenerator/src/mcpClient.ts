import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

const MCP_SERVER_URL = process.env.MCP_SERVER_URL || 'http://127.0.0.1:8080/mcp';

/**
 * Calls the resolveProviderDocID MCP Tool.
 */
export async function resolveProviderDocID(serviceSlug: string): Promise<string | null> {
  try {
    const payload = {
      method: 'tools/call',
      params: {
        name: 'resolve_provider_doc_id',
        arguments: {
          provider_name: process.env.PROVIDER_NAME,
          provider_namespace: process.env.PROVIDER_NAMESPACE,
          service_slug: serviceSlug,
          provider_data_type: 'resources',
          provider_version: process.env.PROVIDER_VERSION || 'latest'
        }
      }
    };

    const response = await axios.post(`${MCP_SERVER_URL}`, payload);
    const resultText = response.data.result?.text || '';
    
    // Extract providerDocID (assuming it appears as 'providerDocID: 123456')
    const match = resultText.match(/providerDocID:\s*(\d+)/);
    return match ? match[1] : null;

  } catch (error) {
    console.error(`Error resolving providerDocID for ${serviceSlug}:`, error instanceof Error ? error.message : String(error));
    return null;
  }
}

/**
 * Calls the getProviderDocs MCP Tool.
 */
export async function getProviderDocs(providerDocID: string): Promise<string> {
  try {
    const payload = {
      method: 'tools/call',
      params: {
        name: 'get_provider_docs',
        arguments: {
          provider_doc_id: providerDocID
        }
      }
    };

    const response = await axios.post(`${MCP_SERVER_URL}`, payload);
    return response.data.result?.text || '';

  } catch (error) {
    console.error(`Error fetching documentation for providerDocID ${providerDocID}:`, error instanceof Error ? error.message : String(error));
    return '';
  }
}
