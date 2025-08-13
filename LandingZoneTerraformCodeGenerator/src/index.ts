import * as ExcelJS from 'exceljs';
import * as fs from 'fs';
import * as path from 'path';
import { fetchModuleInfo, formatModuleDocumentation } from './terraformRegistry';
import { generateLLMContext } from './contextBuilder';
import { generateTerraformModule } from './AzureOpenAIClient'; // Updated file name

// Azure/azurerm modules configuration
const NAMESPACE = 'Azure';
const PROVIDER = 'azurerm';

// Mapping from Excel names to actual Terraform Registry module names
const MODULE_NAME_MAPPING: Record<string, string> = {
  'ResourceGroup': 'avm-res-resources-resourcegroup',
  'StorageAccount': 'avm-res-storage-storageaccount',
  'VirtualNetwork': 'avm-res-network-virtualnetwork',
  'NetworkSecurityGroup': 'avm-res-network-networksecuritygroup',
  'VirtualMachine': 'avm-res-compute-virtualmachine',
  'KeyVault': 'avm-res-keyvault-vault',
  'LoadBalancer': 'avm-res-network-loadbalancer',
  'ApplicationGateway': 'avm-res-network-applicationgateway',
  'PublicIP': 'avm-res-network-publicipaddress',
  'RouteTable': 'avm-res-network-routetable',
  'PrivateEndpoint': 'avm-res-network-privateendpoint'
};

// Reads resource names from Excel input file
async function readModulesFromExcel(filePath: string): Promise<string[]> {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);
  const worksheet = workbook.getWorksheet(1);

  if (!worksheet) {
    throw new Error('Worksheet not found');
  }

  const moduleNames: string[] = [];
  worksheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) return; // Skip header row
    const moduleName = row.getCell(1).text.trim();
    if (moduleName) {
      moduleNames.push(moduleName);
    }
  });

  return moduleNames;
}

// Main Execution Function
async function main() {
  const modules = await readModulesFromExcel('input.xlsx');
  console.log(`Modules to process: ${modules.join(', ')}`);

  for (const moduleName of modules) {
    console.log(`\n Processing module: ${moduleName}...`);

    const actualModuleName = MODULE_NAME_MAPPING[moduleName];

    if (!actualModuleName) {
      console.error(`❌ No mapping found for module: ${moduleName}`);
      console.log(`   Available mappings: ${Object.keys(MODULE_NAME_MAPPING).join(', ')}`);
      continue;
    }

    console.log(`   → Mapped to: ${actualModuleName}`);

    const moduleInfo = await fetchModuleInfo(NAMESPACE, actualModuleName, PROVIDER);

    if (moduleInfo) {
      // Generate Documentation Text from Registry Info
      const docsContent = formatModuleDocumentation(moduleName, moduleInfo.inputs, moduleInfo.outputs);

      const outputDir = path.join(__dirname, '../output');
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir);
      }

      fs.writeFileSync(path.join(outputDir, `${moduleName}.txt`), docsContent, 'utf-8');
      console.log(`✅ Saved ${moduleName}.txt`);

      // STEP 1: Build Context Instructions (Fixed + Dynamic)
      generateLLMContext(moduleName);

      // STEP 2: Call Azure OpenAI GPT API to Generate Terraform Module Files
      await generateTerraformModule(moduleName);

    } else {
      console.error(`❌ Could not fetch module info for ${actualModuleName}`);
    }
  }

  console.log('\n All modules processed successfully!');
}

main();
