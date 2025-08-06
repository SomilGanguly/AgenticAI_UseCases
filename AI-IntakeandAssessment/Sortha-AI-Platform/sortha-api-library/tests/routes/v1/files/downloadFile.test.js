const Client = require('../../../../src/client');
const Authentication = require('../../../../src/auth/authentication');
const DownloadFile = require('../../../../src/routes/v1/files/downloadFile');
const CreateFile = require('../../../../src/routes/v1/files/createFile');

const { readFile } = require("node:fs/promises");

const Test = async () => {
    const client = new Client('http://localhost:8000', new Authentication());
    const file = new Blob([await readFile('../README.md')]);
    let request = await client.createRequest(new CreateFile(file, 'README.md', 0, 0));
    const response = await request.invoke();

    request = client.createRequest(new DownloadFile(response.id));
    request.invoke()
        .then(data => {
            console.log('Success');
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

module.exports = Test;

