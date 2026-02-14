export class Village {
    constructor(game) {
        this.game = game;
        this.rank = 1;
        this.resources = 0;
        this.facilities = {
            'Blacksmith': { level: 1, cost: 100, desc: 'Increases Attack Damage' },
            'Shrine': { level: 1, cost: 150, desc: 'Increases Max HP' }
        };
    }

    upgrade(facilityName) {
        const facility = this.facilities[facilityName];
        if (facility && this.resources >= facility.cost) {
            this.resources -= facility.cost;
            facility.level++;
            facility.cost = Math.floor(facility.cost * 1.5);
            console.log(`Upgraded ${facilityName} to level ${facility.level}`);

            // Apply effects (Placeholder)
            if (facilityName === 'Blacksmith') this.game.player.damage = (this.game.player.damage || 1) + 1;
        }
    }

    render(ctx) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(50, 50, this.game.width - 100, this.game.height - 100);

        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`== VILLAGE (Rank ${this.rank}) ==`, this.game.width / 2, 70);
        ctx.fillText(`Resources: ${this.resources} Souls`, this.game.width / 2, 90);

        let y = 120;
        ctx.textAlign = 'left';
        for (const [name, data] of Object.entries(this.facilities)) {
            const color = this.resources >= data.cost ? '#fff' : '#888';
            ctx.fillStyle = color;
            ctx.fillText(`[${name} Lv.${data.level}] Cost: ${data.cost}`, 60, y);
            ctx.font = '8px monospace';
            ctx.fillStyle = '#aaa';
            ctx.fillText(`  ${data.desc}`, 60, y + 10);
            ctx.font = '12px monospace';
            y += 30;
        }

        ctx.textAlign = 'center';
        ctx.fillStyle = '#ff0';
        ctx.fillText('Press [1] or [2] to Upgrade', this.game.width / 2, this.game.height - 70);
        ctx.fillText('Press [V] to Exit', this.game.width / 2, this.game.height - 55);
    }

    update(dt) {
        // Simple input for prototype
        if (this.game.input.isDown('Digit1')) this.upgrade('Blacksmith'); // Needs logic to prevent spam
        if (this.game.input.isDown('Digit2')) this.upgrade('Shrine');
    }
}
