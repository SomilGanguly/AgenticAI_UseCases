class Request {
    constructor(url, method = 'GET', jwt = null, body = null, formatterFunction = null) {
        this.url = url;
        this.method = method;
        this.jwt = jwt;
        this.body = body;
        this.formatterFunction = formatterFunction;
    }
    async invoke() {
        let headers = {};
        if(this.body!==null && !(this.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }
        if (this.jwt!== null) {
            headers['Authorization'] = `Bearer ${this.jwt}`;
        }
        const response = await fetch(this.url, {
            method: this.method,
            headers: headers,
            body: this.body===null? null: this.body instanceof FormData ? this.body : JSON.stringify(this.body)
        })
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        let responseBody = await response.text();
        try {
            responseBody = JSON.parse(responseBody);
        }
        catch (error) {
            // do nothing, responseBody is not JSON
        }
        if (this.formatterFunction) {
            return this.formatterFunction(responseBody);
        }
        return responseBody;
    }
}

module.exports = Request;