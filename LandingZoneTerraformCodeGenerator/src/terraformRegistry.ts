import axios from 'axios';

const TERRAFORM_REGISTRY_API = 'https://registry.terraform.io/v1/modules';

export interface TerraformModule {
  name: string;
  namespace: string;
  provider: string;
  version: string;
}

export interface ModuleInput {
  name: string;
  description?: string;
  type?: string;
  default?: any;
  required?: boolean;
}

export interface ModuleOutput {
  name: string;
  description?: string;
}

export async function fetchModuleInfo(namespace: string, moduleName: string, provider: string): Promise<{inputs: ModuleInput[], outputs: ModuleOutput[]} | null> {
  try {
    // Get the latest version first
    const versionsResponse = await axios.get(`${TERRAFORM_REGISTRY_API}/${namespace}/${moduleName}/${provider}/versions`);
    const versions = versionsResponse.data.modules?.[0]?.versions;
    
    if (!versions || versions.length === 0) {
      console.error(`No versions found for module ${namespace}/${moduleName}/${provider}`);
      return null;
    }

    const latestVersion = versions[0].version;
    
    // Get module details for the latest version
    const moduleResponse = await axios.get(`${TERRAFORM_REGISTRY_API}/${namespace}/${moduleName}/${provider}/${latestVersion}`);
    const moduleData = moduleResponse.data;

    return {
      inputs: moduleData.root?.inputs || [],
      outputs: moduleData.root?.outputs || []
    };

  } catch (error) {
    console.error(`Error fetching module info for ${namespace}/${moduleName}/${provider}:`, error instanceof Error ? error.message : String(error));
    return null;
  }
}

export function formatModuleDocumentation(moduleName: string, inputs: ModuleInput[], outputs: ModuleOutput[]): string {
  const result: string[] = [];

  result.push(`Module: ${moduleName}`);
  result.push(`${'='.repeat(50)}`);
  result.push('');

  if (inputs.length > 0) {
    result.push('INPUTS (Arguments):');
    result.push('-'.repeat(30));
    inputs.forEach((input) => {
      result.push(`• ${input.name}`);
      if (input.description) {
        result.push(`  Description: ${input.description}`);
      }
      if (input.type) {
        result.push(`  Type: ${input.type}`);
      }
      if (input.default !== undefined) {
        result.push(`  Default: ${JSON.stringify(input.default)}`);
      }
      result.push(`  Required: ${input.required !== false ? 'Yes' : 'No'}`);
      result.push('');
    });
  } else {
    result.push('No inputs found.');
    result.push('');
  }

  if (outputs.length > 0) {
    result.push('OUTPUTS:');
    result.push('-'.repeat(30));
    outputs.forEach((output) => {
      result.push(`• ${output.name}`);
      if (output.description) {
        result.push(`  Description: ${output.description}`);
      }
      result.push('');
    });
  } else {
    result.push('No outputs found.');
    result.push('');
  }

  result.push(`Generated on: ${new Date().toISOString()}`);
  result.push('');

  return result.join('\n');
}
