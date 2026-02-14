export class Player {
    constructor(game) {
        this.game = game;
        this.x = game.width / 2;
        this.y = game.height / 2;
        this.width = 16;
        this.height = 16;
        this.speed = 100;
        // this.color = '#00ff00'; // Removed color for sprite

        // Sprite settings
        this.image = new Image();
        this.image.src = 'assets/player.png';
        this.spriteWidth = 48; // Assumed frame size (adjust based on actual image)
        this.spriteHeight = 48;
        this.frameX = 0;
        this.frameY = 0;
        this.maxFrame = 2; // 3 frames per row (0, 1, 2)
        this.fps = 10;
        this.frameTimer = 0;
        this.frameInterval = 1000 / this.fps;

        this.attackCooldown = 0.5;
        this.attackTimer = 0;
        this.isAttacking = false;

        // Visual offset to center sprite on hit box
        this.drawOffsetX = -16;
        this.drawOffsetY = -16;
    }

    update(dt) {
        const input = this.game.input;
        let dx = 0;
        let dy = 0;
        let isMoving = false;

        if (input.isDown('ArrowUp') || input.isDown('KeyW')) { dy = -1; }
        if (input.isDown('ArrowDown') || input.isDown('KeyS')) { dy = 1; }
        if (input.isDown('ArrowLeft') || input.isDown('KeyA')) { dx = -1; }
        if (input.isDown('ArrowRight') || input.isDown('KeyD')) { dx = 1; }

        if (dx !== 0 || dy !== 0) {
            isMoving = true;
            const length = Math.sqrt(dx * dx + dy * dy);
            dx /= length;
            dy /= length;
        }

        this.x += dx * this.speed * dt;
        this.y += dy * this.speed * dt;

        // Boundary checks
        this.x = Math.max(0, Math.min(this.game.width - this.width, this.x));
        this.y = Math.max(0, Math.min(this.game.height - this.height, this.y));

        // Attack Logic
        if (this.attackTimer > 0) this.attackTimer -= dt;

        if (input.isDown('Space') && this.attackTimer <= 0) {
            this.attack();
        }

        // Animation Logic
        if (this.isAttacking) {
            this.frameY = 2; // Attack Row (Assumed bottom)
            this.maxFrame = 2;
        } else if (isMoving) {
            this.frameY = 0; // Run Row (Assumed top)
            // Flip? Standard sheets might have L/R or just one direction.
            // For now, assume one direction or row 1 is run.
        } else {
            this.frameY = 1; // Idle Row (Assumed middle)
        }

        // Frame Cycling
        if (this.frameTimer > this.frameInterval) {
            if (this.frameX < this.maxFrame) this.frameX++;
            else this.frameX = 0;
            this.frameTimer = 0;
        } else {
            this.frameTimer += dt * 1000;
        }
    }

    attack() {
        this.attackTimer = this.attackCooldown;
        const attackRange = 40;
        const cx = this.x + this.width / 2;
        const cy = this.y + this.height / 2;

        this.isAttacking = true;
        this.frameX = 0; // Reset animation to start of attack
        setTimeout(() => this.isAttacking = false, 300); // Match animation duration roughly

        this.game.enemies.forEach(enemy => {
            const ex = enemy.x + enemy.width / 2;
            const ey = enemy.y + enemy.height / 2;
            const dist = Math.sqrt((ex - cx) ** 2 + (ey - cy) ** 2);
            if (dist < attackRange) {
                enemy.markedForDeletion = true;
            }
        });
    }

    render(ctx) {
        // Shadow
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.beginPath();
        ctx.ellipse(this.x + this.width / 2, this.y + this.height - 2, 8, 4, 0, 0, Math.PI * 2);
        ctx.fill();

        // Sprite
        if (this.image.complete) {
            ctx.drawImage(
                this.image,
                this.frameX * this.spriteWidth,
                this.frameY * this.spriteHeight,
                this.spriteWidth,
                this.spriteHeight,
                this.x + this.drawOffsetX,
                this.y + this.drawOffsetY,
                this.spriteWidth,
                this.spriteHeight
            );
        } else {
            // Fallback
            ctx.fillStyle = '#0f0';
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }

        // Attack Range Debug (only when attacking?)
        /*
        if (this.isAttacking) {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.strokeRect(this.x, this.y, this.width, this.height);
        }
        */
    }
}
