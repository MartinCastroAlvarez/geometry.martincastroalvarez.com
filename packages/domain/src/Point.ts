export interface PointDict {
    x: number;
    y: number;
}

export class Point {
    constructor(public readonly x: number, public readonly y: number) { }

    static fromDict(dict: PointDict): Point {
        return new Point(dict.x, dict.y);
    }

    toDict(): PointDict {
        return { x: this.x, y: this.y };
    }

    equals(other: Point): boolean {
        return Math.abs(this.x - other.x) < Number.EPSILON && Math.abs(this.y - other.y) < Number.EPSILON;
    }

    distanceTo(other: Point): number {
        return Math.sqrt(Math.pow(this.x - other.x, 2) + Math.pow(this.y - other.y, 2));
    }

    toArray(): [number, number] {
        return [this.x, this.y];
    }
}
