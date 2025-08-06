const Request = require('./request');

class RequestBuilder {
    constructor() {
        this.jwt = null;
        this.url = null;
        this.method = 'GET'; // Default method
        this.body = null; // Default body
        this.formatterFunction = null; // Default formatter function
    }
    setJWT(jwt) {
        this.jwt = jwt;
        return this;
    }
    setURL(url) {
        this.url = url;
        return this;
    }
    setMethod(method) {
        this.method = method;
        return this;
    }
    setBody(body) {
        this.body = body;
        return this;
    }
    setFormatterFunction(formatterFunction) {
        this.formatterFunction = formatterFunction;
        return this;
    }
    build() {
        return new Request(this.url, this.method, this.jwt, this.body, this.formatterFunction);
    }
}

module.exports = RequestBuilder;