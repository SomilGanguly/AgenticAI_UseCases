const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const GetStatus = require('../../../../src/routes/v1/workflows/getStatus');

const Test = () => {
    const client = new Client('http://localhost:8000', new Authentication());
    request = client.createRequest(new GetStatus('9d907495-d023-4f2a-827c-33787c15423c'))
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;