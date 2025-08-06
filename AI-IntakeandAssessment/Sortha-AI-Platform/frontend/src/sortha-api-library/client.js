const RequestBuilder = require('./request/requestBuilder');
const Route = require('./routes/route');

/**
 * Client class for making API requests.
 * @class Client
 * @param {string} baseURL - The base URL for the API.
 * @param {Object} auth - An authentication object that provides a method to get JWT.
 */

class Client {
    constructor(baseURL, auth) {
        if (!baseURL || typeof baseURL !== 'string') {
            throw new Error('Invalid base URL provided.');
        }
        if (!auth || typeof auth.getJWT !== 'function') {
            throw new Error('Invalid authentication object provided.');
        }
        baseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL; // Ensure no trailing slash
        this.baseURL = baseURL;
        this.auth = auth;
    }
    
    /**
     * Creates a request object based on the provided route.
     * @param {Object} route - The route object that defines the API endpoint.
     * @returns {Object} - The constructed request object.
     */
    createRequest(route) {
        if (!route || !(route instanceof Route)) {
            throw new Error('Invalid route provided. It must be an instance of Route.');
        }
        const rb = new RequestBuilder();
        if(route.needsAuth()) {
            rb.setJWT(this.auth.getJWT());
        }
        rb.setURL(`${this.baseURL}${route.getPath()}`)
            .setMethod(route.getMethod())
            .setBody(route.getBody())
            // .setFormatterFunction(route.formatOutput);
        return rb.build();
    }
}

module.exports = Client;