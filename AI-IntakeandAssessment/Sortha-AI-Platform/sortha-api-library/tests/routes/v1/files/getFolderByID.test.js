const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const GetFolderByID = require('../../../../src/routes/v1/files/getFolderByID');

const Test = () => {
    const client = new Client('http://localhost:8000', new Authentication());
    request = client.createRequest(new GetFolderByID(1))
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;

