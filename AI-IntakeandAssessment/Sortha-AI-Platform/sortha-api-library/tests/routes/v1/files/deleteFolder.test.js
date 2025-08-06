const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const CreateFolder = require('../../../../src/routes/v1/files/createFolder');
const DeleteFolder = require('../../../../src/routes/v1/files/deleteFolder');

const Test = async () => {
    const client = new Client('http://localhost:8000', new Authentication());
    request = client.createRequest(new CreateFolder('testFolder', null, 0));
    response = await request.invoke();

    client.createRequest(new DeleteFolder(response.id));
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;

