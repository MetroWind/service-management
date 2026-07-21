"use strict";

const reduce_motion = window.matchMedia("(prefers-reduced-motion: reduce)");
const canvas = document.querySelector("#matrix-rain");
const context = canvas.getContext("2d");
const glyphs = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const font_size = 16;
let columns = [];
let animation_id = null;

function resizeCanvas()
{
    const scale = window.devicePixelRatio || 1;

    canvas.width = Math.floor(window.innerWidth * scale);
    canvas.height = Math.floor(window.innerHeight * scale);
    canvas.style.width = `${window.innerWidth}px`;
    canvas.style.height = `${window.innerHeight}px`;
    context.setTransform(scale, 0, 0, scale, 0, 0);
    context.font = `${font_size}px monospace`;
    columns = Array.from(
        {length: Math.ceil(window.innerWidth / font_size)},
        () => ({
            position: Math.random() * -window.innerHeight / font_size,
            speed: 0.16 + Math.random() * 0.62,
        }),
    );
}

function drawRain()
{
    context.fillStyle = "rgb(3 8 5 / 12%)";
    context.fillRect(0, 0, window.innerWidth, window.innerHeight);
    context.fillStyle = "rgb(100 255 145 / 42%)";

    for(let index = 0; index < columns.length; index += 1)
    {
        const column = columns[index];
        const glyph = glyphs[Math.floor(Math.random() * glyphs.length)];
        const x = index * font_size;
        const y = column.position * font_size;

        context.fillText(glyph, x, y);
        column.position += column.speed;

        if(y > window.innerHeight && Math.random() > 0.98)
        {
            column.position = Math.random() * -24;
            column.speed = 0.16 + Math.random() * 0.62;
        }
    }

    animation_id = window.requestAnimationFrame(drawRain);
}

function stopRain()
{
    if(animation_id !== null)
    {
        window.cancelAnimationFrame(animation_id);
        animation_id = null;
    }
}

function startRain()
{
    if(!reduce_motion.matches && !document.hidden && animation_id === null)
    {
        drawRain();
    }
}

window.addEventListener("resize", resizeCanvas);
document.addEventListener("visibilitychange", () =>
{
    stopRain();
    startRain();
});
reduce_motion.addEventListener("change", () =>
{
    stopRain();
    startRain();
});

resizeCanvas();
startRain();
