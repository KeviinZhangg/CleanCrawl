import { useEffect, useRef } from "react";

/** Subtle animated wireframe mesh — mesh3d.gallery aesthetic without Three.js. */
export function MeshBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let frame = 0;
    let raf = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = () => {
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);

      const cx = width * 0.5;
      const cy = height * 0.35;
      const t = frame * 0.004;
      const rings = 6;
      const spokes = 14;

      for (let r = 0; r < rings; r++) {
        const radius = 80 + r * 55 + Math.sin(t + r * 0.7) * 12;
        ctx.beginPath();
        for (let i = 0; i <= spokes; i++) {
          const angle = (i / spokes) * Math.PI * 2 + t * 0.3 + r * 0.2;
          const x = cx + Math.cos(angle) * radius;
          const y = cy + Math.sin(angle) * radius * 0.55;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        const alpha = 0.04 + (rings - r) * 0.008;
        ctx.strokeStyle = `rgba(168, 180, 255, ${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }

      for (let i = 0; i < spokes; i++) {
        const angle = (i / spokes) * Math.PI * 2 + t * 0.2;
        const innerR = 60;
        const outerR = 80 + (rings - 1) * 55 + 20;
        const x1 = cx + Math.cos(angle) * innerR;
        const y1 = cy + Math.sin(angle) * innerR * 0.55;
        const x2 = cx + Math.cos(angle + Math.sin(t) * 0.1) * outerR;
        const y2 = cy + Math.sin(angle + Math.sin(t) * 0.1) * outerR * 0.55;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = `rgba(168, 180, 255, ${0.03 + (i % 3) * 0.01})`;
        ctx.lineWidth = 0.6;
        ctx.stroke();
      }

      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, width * 0.6);
      grad.addColorStop(0, "rgba(168, 180, 255, 0.04)");
      grad.addColorStop(0.4, "rgba(120, 200, 255, 0.02)");
      grad.addColorStop(1, "transparent");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      frame++;
      raf = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      aria-hidden
    />
  );
}
