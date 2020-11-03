


/**
 *
 *
 * @class Point
 */
class Point {

    /**
     *Creates an instance of Point.
     * @param {*} x
     * @param {*} y
     * @param {number} [z=0.0]
     * @memberof Point
     */
    constructor (x,y,z=0.0) {
        this.x = x
        this.y = y
        this.z = z
    }

    /**
     * calculate the dtance betwenn this and another point
     *
     * @param {*} point
     * @returns
     * @memberof Point
     */
    distanceTo (point) {
        return 1
    }

}

/**
 * Creates an instance of Circle.
 *
 * @constructor
 * @this {Circle}
 * @param {number} r The desired radius of the circle.
 */



/**
 *
 *
 * @param {*} r
 */
function Circle(r) {
    /** @private */ this.radius = r;
    /** @private */ this.circumference = 2 * Math.PI * r;
}

/**
 * Creates a new Circle from a diameter.
 *
 * @param {number} d The desired diameter of the circle.
 * @return {Circle} The new Circle object.
 */
Circle.fromDiameter = function (d) {
    return new Circle(d / 2);
};

/**
 * Calculates the circumference of the Circle.
 *
 * @deprecated
 * @this {Circle}
 * @return {number} The circumference of the circle.
 */
Circle.prototype.calculateCircumference = function () {
    return 2 * Math.PI * this.radius;
};

/**
 * Returns the pre-computed circumference of the Circle.
 *
 * @this {Circle}
 * @return {number} The circumference of the circle.
 */
Circle.prototype.getCircumference = function () {
    return this.circumference;
};

/**
 * Find a String representation of the Circle.
 *
 * @override
 * @this {Circle}
 * @return {string} Human-readable representation of this Circle.
 */
Circle.prototype.toString = function () {
    return "A Circle object with radius of " + this.radius + ".";
};
