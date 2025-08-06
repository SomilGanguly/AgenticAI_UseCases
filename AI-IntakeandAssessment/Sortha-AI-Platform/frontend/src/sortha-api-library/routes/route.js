/**
 * Abstract class representing a route in the API.
 * @class Route
 */
class Route {
    
    /**
     * Returns the HTTP method for the route.
     * @returns {string} - The HTTP method (e.g., 'GET', 'POST', etc.).
     */
    getMethod() {
        throw new Error('Method not implemented.');
    }

    /**
     * Returns the path for the route.
     * @returns {string} - The path for the route.
     */
    getPath() {
        throw new Error('Method not implemented.');
    }

    /**
     * Determines if the route requires authentication.
     * @returns {boolean} - True if authentication is required, false otherwise.
     */
    needsAuth() {
        throw new Error('Method not implemented.');
    }

    /**
     * Returns the body for the route.
     * @returns {Object} - The body for the route, if applicable.
     */
    getBody() {
        throw new Error('Method not implemented.');
    }

    /**
     * Returns the formated output.
     * @returns {Object} - The headers for the route, if applicable.
     */
    formatOutput() {
        throw new Error('Method not implemented.');
    }
}

module.exports = Route;