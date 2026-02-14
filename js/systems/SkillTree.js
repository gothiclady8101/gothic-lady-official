export class SkillTree {
    constructor(game) {
        this.game = game;
        this.points = 0;
        this.nodes = [
            { id: 'demon_slash', name: 'Demon Slash', type: 'DEMON', learned: true, parent: null, x: 100, y: 150 },
            { id: 'soul_eater', name: 'Soul Eater', type: 'DEMON', learned: false, parent: 'demon_slash', x: 60, y: 100 },
            { id: 'hell_fire', name: 'Hell Fire', type: 'DEMON', learned: false, parent: 'demon_slash', x: 140, y: 100 },

            { id: 'hero_parry', name: 'Hero Parry', type: 'HERO', learned: false, parent: null, x: 220, y: 150 },
            { id: 'holy_light', name: 'Holy Light', type: 'HERO', learned: false, parent: 'hero_parry', x: 260, y: 100 }
        ];
    }

    unlock(nodeId) {
        const node = this.nodes.find(n => n.id === nodeId);
        if (node && !node.learned && this.points > 0) {
            // Check parent
            if (node.parent) {
                const parent = this.nodes.find(n => n.id === node.parent);
                if (!parent.learned) return;
            }
            node.learned = true;
            this.points--;
            console.log(`Learned ${node.name}`);
        }
    }

    render(ctx) {
        ctx.fillStyle = 'rgba(0, 0, 20, 0.9)';
        ctx.fillRect(20, 20, this.game.width - 40, this.game.height - 40);

        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';
        ctx.font = '12px monospace';
        ctx.fillText(`== SKILL TREE (PTS: ${this.points}) ==`, this.game.width / 2, 40);

        // Draw connections
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 2;
        this.nodes.forEach(node => {
            if (node.parent) {
                const parent = this.nodes.find(n => n.id === node.parent);
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.lineTo(parent.x, parent.y);
                ctx.stroke();
            }
        });

        // Draw nodes
        this.nodes.forEach(node => {
            ctx.fillStyle = node.learned ? (node.type === 'DEMON' ? '#f00' : '#0ff') : '#444';
            ctx.fillRect(node.x - 5, node.y - 5, 10, 10);

            ctx.fillStyle = '#aaa';
            ctx.font = '8px monospace';
            ctx.fillText(node.name, node.x, node.y + 15);
        });

        ctx.fillStyle = '#ff0';
        ctx.fillText('Press [K] to Close', this.game.width / 2, this.game.height - 30);
    }
}
