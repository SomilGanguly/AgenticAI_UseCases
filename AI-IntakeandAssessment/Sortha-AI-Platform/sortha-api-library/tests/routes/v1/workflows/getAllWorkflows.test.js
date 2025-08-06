const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const GetAllWorkflows = require('../../../../src/routes/v1/workflows/getAllWorkflows');

const Test = () => {
    const client = new Client('http://localhost:8000', new Authentication());
    request = client.createRequest(new GetAllWorkflows())
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;