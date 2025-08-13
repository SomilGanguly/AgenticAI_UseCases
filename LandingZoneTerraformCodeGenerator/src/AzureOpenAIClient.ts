import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

dotenv.config();

const AZURE_OPENAI_ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT;
const AZURE_OPENAI_API_KEY = process.env.AZURE_OPENAI_KEY; // Fixed: matching .env file
const DEPLOYMENT_NAME = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;
const API_VERSION = process.env.AZURE_OPENAI_API_VERSION;

export async function generateTerraformModule(resourceName: string) {
    const contextFilePath = path.join(__dirname, '../generatedContext', `${resourceName}_context.txt`);
    const contextContent = fs.readFileSync(contextFilePath, 'utf-8');

    // Create the terraform-configuration directory structure
    const outputDir = path.join(__dirname, '../terraform-configuration', resourceName);
    
    // Clean existing files to ensure fresh generation
    if (fs.existsSync(outputDir)) {
        const existingFiles = fs.readdirSync(outputDir);
        existingFiles.forEach(file => {
            if (file.endsWith('.tf') || file.endsWith('.tfvars') || file.endsWith('.md')) {
                fs.unlinkSync(path.join(outputDir, file));
                console.log(`🗑️  Removed old file: ${file}`);
            }
        });
    } else {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const payload = {
        messages: [
            { 
                role: "system", 
                content: `You are a Senior Terraform DevOps Engineer with expertise in Azure Verified Modules (AVM).

Your task is to generate complete, production-ready Terraform module files based on Azure resource documentation.

CRITICAL FORMATTING RULES:
1. Use EXACTLY these delimiters to separate files:
   === FILE: main.tf ===
   === FILE: variables.tf ===
   === FILE: outputs.tf ===
   === FILE: terraform.tfvars ===

2. Generate clean Terraform code WITHOUT:
   - Markdown code blocks (\`\`\`)
   - Extra explanatory text
   - Comments outside the code
   
3. Follow Terraform best practices:
   - Proper indentation (2 spaces)
   - Valid HCL syntax
   - Descriptive variable names
   - Production-ready structure

Generate high-quality, working Terraform modules that can be deployed immediately.`
            },
            { role: "user", content: contextContent }
        ],
        max_tokens: 6000,
        temperature: 0.1,
        top_p: 0.9,
        frequency_penalty: 0,
        presence_penalty: 0,
    };

    try {
        const response = await axios.post(
            `${AZURE_OPENAI_ENDPOINT}/openai/deployments/${DEPLOYMENT_NAME}/chat/completions?api-version=2024-12-01-preview`,
            payload,
            {
                headers: {
                    'api-key': AZURE_OPENAI_API_KEY,
                    'Content-Type': 'application/json'
                }
            }
        );

        const generatedCode = response.data.choices[0].message.content;
        
        // Parse the response and create individual files
        parseAndCreateTerraformFiles(generatedCode, outputDir, resourceName);
        
    } catch (error) {
        console.error(`❌ Error calling Azure OpenAI API for ${resourceName}:`, error instanceof Error ? error.message : String(error));
        
        // Save error details for debugging
        const errorPath = path.join(outputDir, 'error-log.txt');
        fs.writeFileSync(errorPath, `Error: ${error}\nTimestamp: ${new Date().toISOString()}`, 'utf-8');
    }
}

// Helper function to parse LLM response and create individual Terraform files
function parseAndCreateTerraformFiles(content: string, outputDir: string, resourceName: string) {
    const fileDelimiters = [
        { delimiter: '=== FILE: main.tf ===', filename: 'main.tf' },
        { delimiter: '=== FILE: variables.tf ===', filename: 'variables.tf' },
        { delimiter: '=== FILE: outputs.tf ===', filename: 'outputs.tf' },
        { delimiter: '=== FILE: terraform.tfvars ===', filename: 'terraform.tfvars' }
    ];

    console.log(`🔍 Parsing response for ${resourceName}...`);
    
    // Clean the content first
    let cleanContent = content.trim();
    
    const files: { [key: string]: string } = {};
    
    // Split content by delimiters
    for (let i = 0; i < fileDelimiters.length; i++) {
        const currentDelimiter = fileDelimiters[i].delimiter;
        const nextDelimiter = i + 1 < fileDelimiters.length ? fileDelimiters[i + 1].delimiter : null;
        
        const startIndex = cleanContent.indexOf(currentDelimiter);
        if (startIndex !== -1) {
            const contentStart = startIndex + currentDelimiter.length;
            let endIndex = cleanContent.length;
            
            if (nextDelimiter) {
                const nextIndex = cleanContent.indexOf(nextDelimiter, contentStart);
                if (nextIndex !== -1) {
                    endIndex = nextIndex;
                }
            }
            
            if (endIndex > contentStart) {
                let fileContent = cleanContent.substring(contentStart, endIndex).trim();
                
                // Remove any markdown code blocks
                fileContent = fileContent.replace(/^```[a-zA-Z]*\n?/, '').replace(/\n?```$/, '').trim();
                
                // Remove any extra delimiters that might have leaked in
                fileContent = fileContent.replace(/=== FILE: .* ===/g, '').trim();
                
                // Only add if content is substantial
                if (fileContent.length > 20 && !fileContent.includes('=== FILE:')) {
                    files[fileDelimiters[i].filename] = fileContent;
                    console.log(`📝 Found content for ${fileDelimiters[i].filename} (${fileContent.length} chars)`);
                } else {
                    console.log(`⚠️  Insufficient content for ${fileDelimiters[i].filename}`);
                }
            }
        } else {
            console.log(`❌ Delimiter not found: ${currentDelimiter}`);
        }
    }

    // Write individual files
    let filesCreated = 0;
    for (const [filename, fileContent] of Object.entries(files)) {
        if (fileContent && fileContent.length > 20) {
            const filePath = path.join(outputDir, filename);
            fs.writeFileSync(filePath, fileContent, 'utf-8');
            console.log(`✅ Created: ${filename} (${fileContent.length} chars)`);
            filesCreated++;
        }
    }

    if (filesCreated === 0) {
        // Save raw response for debugging
        const debugPath = path.join(outputDir, 'raw-response.md');
        fs.writeFileSync(debugPath, content, 'utf-8');
        console.log(`⚠️  No files parsed successfully. Raw response saved to: ${debugPath}`);
        console.log(`📋 Response preview: ${content.substring(0, 500)}...`);
    } else {
        console.log(`🎉 Successfully created ${filesCreated}/4 Terraform files for ${resourceName}!`);
    }
}
