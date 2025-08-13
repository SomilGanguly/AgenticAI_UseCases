import * as fs from 'fs';
import * as path from 'path';

// This builds the combined context for LLM (Dynamic + Fixed Instructions)
export function generateLLMContext(resourceName: string) {
  const outputDir = path.join(__dirname, '../generatedContext');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }

  const dynamicContextPath = path.join(__dirname, '../output', `${resourceName}.txt`);
  if (!fs.existsSync(dynamicContextPath)) {
    console.error(`❌ Dynamic documentation not found for ${resourceName}. Skipping context build.`);
    return;
  }

  const dynamicContext = fs.readFileSync(dynamicContextPath, 'utf-8');

  // Fixed Instructions to guide the LLM on Terraform Structure Generation
  const fixedInstructions = `
You are a Terraform Expert specializing in Azure Verified Modules (AVM).

TASK: Generate a complete, production-ready Terraform module for "${resourceName}" based on the detailed AVM documentation provided.

CRITICAL OUTPUT FORMAT:
You MUST generate EXACTLY 4 separate files using these EXACT delimiters:

=== FILE: main.tf ===
[main.tf content here - NO markdown code blocks, just pure Terraform code]

=== FILE: variables.tf ===
[variables.tf content here - NO markdown code blocks, just pure Terraform code]

=== FILE: outputs.tf ===
[outputs.tf content here - NO markdown code blocks, just pure Terraform code]

=== FILE: terraform.tfvars ===
[terraform.tfvars content here - NO markdown code blocks, just example values]

DETAILED REQUIREMENTS:

1. **main.tf**:
   - Include terraform block with required_providers (azurerm >= 3.0)
   - Use module call to the AVM module (source = "Azure/avm-res-{service}-{resource}/azurerm")
   - Use latest version of the AVM module
   - Pass all required variables from variables.tf
   - Include data sources if needed (e.g., resource group)
   - Follow AVM best practices

2. **variables.tf**:
   - Define ALL variables used in main.tf
   - Include proper descriptions from the documentation
   - Set appropriate types (string, bool, object, map, etc.)
   - Add default values where specified in documentation
   - Mark required variables with no default
   - Include validation blocks where appropriate

3. **outputs.tf**:
   - Export ALL important outputs from the module
   - Use descriptive names matching the resource
   - Include proper descriptions
   - Output resource ID, name, and other key attributes
   - Match the outputs listed in the documentation

4. **terraform.tfvars**:
   - Provide realistic example values for ALL variables
   - Use proper Azure naming conventions
   - Include realistic resource group names, locations
   - Set boolean values appropriately
   - Use proper object/map structures for complex variables
   - ENSURE all strings are properly quoted and closed
   - ENSURE all object blocks have closing braces
   - Format example: key = "value" (with proper quotes)

QUALITY STANDARDS:
- Use proper Terraform formatting and indentation
- Follow Azure naming conventions
- Include meaningful comments where helpful
- Ensure all syntax is valid
- Use latest Terraform features (>= 1.3.0)
- Make the module production-ready

RESOURCE DOCUMENTATION (Use this as your reference):
=======================
${dynamicContext}

Remember: Generate clean Terraform code without any markdown formatting, code blocks, or extra text.
`;

  const contextFilePath = path.join(outputDir, `${resourceName}_context.txt`);
  fs.writeFileSync(contextFilePath, fixedInstructions, 'utf-8');
  console.log(`📄 Context generated: ${contextFilePath}`);
}