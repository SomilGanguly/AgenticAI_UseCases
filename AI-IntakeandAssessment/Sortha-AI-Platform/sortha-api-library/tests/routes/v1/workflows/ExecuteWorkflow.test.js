const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const ExecuteWorkflow = require('../../../../src/routes/v1/workflows/executeWorkflow');

const Test = () => {
    const client = new Client('http://localhost:8000', new Authentication());
    request = client.createRequest(new ExecuteWorkflow(1, {
            workflow_id:1,
            input_data:{
                inputs:{
                    transcript_file:{
                        type:'text',
                        file_id:14
                    }
                }
            }
        }))
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;