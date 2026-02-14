export class Enemy {
    constructor(game, x, y) {
        this.game = game;
        this.x = x;
        this.y = y;
        this.width = 16;
        this.height = 16;
        this.speed = 40;
        this.color = '#ff0000'; // Red
        this.markedForDeletion = false;
    }

    update(dt) {
        const player = this.game.player;
        const dx = player.x - this.x;
        const dy = player.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > 0) {
            this.x += (dx / dist) * this.speed * dt;
            this.y += (dy / dist) * this.speed * dt;
        }
    }

    render(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(Math.round(this.x), Math.round(this.y), this.width, this.height);

        // Eyes
        ctx.fillStyle = '#fff';
        ctx.fillRect(Math.round(this.x + 3), Math.round(this.y + 4), 2, 2);
        ctx.fillRect(Math.round(this.x + 11), Math.round(this.y + 4), 2, 2);
    }
}
