from .State import TerraformConfig

class TerraformCodeParser:
    def __init__(self, terraformCodeObject: list[TerraformConfig]):
        self.__terraformCodeObject = terraformCodeObject
        self.__parsedCode = {}

    def compile(self):
        for resource in self.__terraformCodeObject:
            code = ''
            code += f'resource "{resource.resource_type}" "{resource.resource_name}" {{\n'
            for config in resource.attributes:
                code += f'  {config.name} = "{config.value}"'
                if config.comments:
                    code += f'  # {config.comments}'
                code += '\n'
            
            for dynamic_block in resource.dynamic_blocks:
                code += f'  {dynamic_block.block_type} {{\n'
                for attr in dynamic_block.content:
                    code += f'    {attr.name} = "{attr.value}"'
                    if attr.comments:
                        code += f'  # {attr.comments}'
                    code += '\n'
                code += '  }\n'

            code += '}\n'
            self.__parsedCode[resource.resource_name] = code

    def getParsedCode(self, resourceName: str = None):
        if not self.__parsedCode:
            self.compile()
        return self.__parsedCode[resourceName]
    
    def getAllParsedCode(self):
        if not self.__parsedCode:
            self.compile()
        return self.__parsedCode
    
    def getCodeString(self):
        if not self.__parsedCode:
            self.compile()
        return '\n'.join(self.__parsedCode.values())