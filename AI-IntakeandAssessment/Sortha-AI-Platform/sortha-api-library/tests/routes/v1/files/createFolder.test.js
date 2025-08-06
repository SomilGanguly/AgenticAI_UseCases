const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const CreateFolder = require('../../../../src/routes/v1/files/createFolder');

const Test = () => {
    const client = new Client('http://localhost:8000', new Authentication());
    request = client.createRequest(new CreateFolder('testFolder', null, 0));
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;

