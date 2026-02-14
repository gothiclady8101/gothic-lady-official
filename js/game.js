import { Input } from './systems/Input.js';
import { Player } from './entities/Player.js';
import { Enemy } from './entities/Enemy.js';
import { Village } from './systems/Village.js';
import { SkillTree } from './systems/SkillTree.js';

const STATE = {
    PLAYING: 0,
    VILLAGE: 1,
    SKILL_TREE: 2
};

class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Logical resolution (e.g., SNES style)
        this.width = 320;
        this.height = 240;

        // Scale to fit window
        this.scale = 1;

        this.lastTime = 0;
        this.input = new Input();

        this.state = STATE.PLAYING;
        this.village = new Village(this);
        this.skillTree = new SkillTree(this);

        this.player = new Player(this);
        this.enemies = [];
        this.enemySpawnTimer = 0;

        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.loop = this.loop.bind(this);
        requestAnimationFrame(this.loop);
    }

    resize() {
        // Maintain aspect ratio or fill screen?
        // For now, let's just maximize while keeping aspect ratio, or integer scaling
        const aspect = this.width / this.height;
        const windowAspect = window.innerWidth / window.innerHeight;

        if (windowAspect < aspect) {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerWidth / aspect;
        } else {
            this.canvas.width = window.innerHeight * aspect;
            this.canvas.height = window.innerHeight;
        }

        // We want to render to a small offscreen buffer or verify context scaling
        // For simplicity in this prototype, we'll just scale the context
        this.scale = this.canvas.width / this.width;
        this.ctx.scale(this.scale, this.scale);
        this.ctx.imageSmoothingEnabled = false;
    }

    update(dt) {
        // State switching debugging
        if (this.input.isDown('KeyV') && !this.input.lockV) {
            this.state = this.state === STATE.VILLAGE ? STATE.PLAYING : STATE.VILLAGE;
            this.input.lockV = true;
            setTimeout(() => this.input.lockV = false, 300);
        }
        if (this.input.isDown('KeyK') && !this.input.lockK) {
            this.state = this.state === STATE.SKILL_TREE ? STATE.PLAYING : STATE.SKILL_TREE;
            this.input.lockK = true;
            setTimeout(() => this.input.lockK = false, 300);
        }

        if (this.state === STATE.VILLAGE) {
            this.village.update(dt);
            return;
        }
        if (this.state === STATE.SKILL_TREE) {
            return;
        }

        this.player.update(dt);

        // Spawn Enemies
        this.enemySpawnTimer -= dt;
        if (this.enemySpawnTimer <= 0) {
            this.enemies.push(new Enemy(this, Math.random() * this.width, Math.random() * this.height));
            this.enemySpawnTimer = 2.0; // Spawn every 2 seconds
        }

        // Update Enemies
        this.enemies.forEach(enemy => enemy.update(dt));

        // Collision Detection for Enemies vs Player (Game Over?) for now just push

        // Remove dead enemies
        const initialCount = this.enemies.length;
        this.enemies = this.enemies.filter(enemy => !enemy.markedForDeletion);

        // Grant resources on kill
        const killedCount = initialCount - this.enemies.length;
        if (killedCount > 0) {
            this.village.resources += killedCount * 10;
            this.skillTree.points += killedCount; // Generous for testing
        }
    }

    render() {
        // Clear screen
        this.ctx.fillStyle = '#222';
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Sort by Y for simple depth
        const entities = [...this.enemies, this.player];
        entities.sort((a, b) => a.y - b.y);

        entities.forEach(entity => entity.render(this.ctx));

        // Overlays
        if (this.state === STATE.VILLAGE) {
            this.village.render(this.ctx);
        } else if (this.state === STATE.SKILL_TREE) {
            this.skillTree.render(this.ctx);
        }

        // UI / Debug
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '10px monospace';
        this.ctx.textAlign = 'left';
        this.ctx.fillText(`FPS: ${(1 / this.dt).toFixed(1)}`, 5, 12);
    }

    loop(timestamp) {
        this.dt = (timestamp - this.lastTime) / 1000;
        this.lastTime = timestamp;

        this.update(this.dt);
        this.render();

        requestAnimationFrame(this.loop);
    }
}

window.onload = () => {
    const game = new Game();
};
