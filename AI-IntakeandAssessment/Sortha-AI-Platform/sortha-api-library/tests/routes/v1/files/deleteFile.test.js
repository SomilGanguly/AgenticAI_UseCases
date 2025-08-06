const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const CreateFile = require('../../../../src/routes/v1/files/createFile');
const DeleteFile = require('../../../../src/routes/v1/files/deleteFile');

const { readFile } = require("node:fs/promises");

const Test = async () => {
    const client = new Client('http://localhost:8000', new Authentication());
    const file = new Blob([await readFile('../README.md')]);

    request = client.createRequest(new CreateFile(file, 'README.md', 0, 0));
    response = await request.invoke()

    client.createRequest(new DeleteFile(response.id));
    request.invoke()
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;

