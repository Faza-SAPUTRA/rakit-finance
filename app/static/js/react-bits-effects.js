// React Bits-inspired visual effects recreated in vanilla JS for this Flask app.
// Includes spotlight cards, magnetic buttons, gradient-border support, and particles.
(function () {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".spotlight-card").forEach((card) => {
    card.addEventListener("mousemove", (event) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--spot-x", `${event.clientX - rect.left}px`);
      card.style.setProperty("--spot-y", `${event.clientY - rect.top}px`);
    });
  });

  if (!reducedMotion && window.gsap) {
    document.querySelectorAll(".magnetic-btn").forEach((button) => {
      const xTo = gsap.quickTo(button, "x", { duration: 0.35, ease: "power3" });
      const yTo = gsap.quickTo(button, "y", { duration: 0.35, ease: "power3" });
      button.addEventListener("mousemove", (event) => {
        const rect = button.getBoundingClientRect();
        xTo((event.clientX - rect.left - rect.width / 2) * 0.18);
        yTo((event.clientY - rect.top - rect.height / 2) * 0.18);
      });
      button.addEventListener("mouseleave", () => {
        xTo(0);
        yTo(0);
      });
    });
  }

  const canvas = document.getElementById("particle-bg");
  if (!canvas || reducedMotion) return;

  const ctx = canvas.getContext("2d");
  let width = 0;
  let height = 0;
  let particles = [];
  let running = true;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    const count = Math.min(58, Math.floor(width / 28));
    particles = Array.from({ length: count }, createDepthParticle);
  }

  function createDepthParticle() {
    const z = Math.random();
    const depthScale = 0.35 + z * 1.65;
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      z,
      size: 0.8 + depthScale * 1.3,
      alpha: 0.05 + z * 0.22,
      vx: (Math.random() - 0.5) * 0.12 * depthScale,
      vy: (Math.random() - 0.5) * 0.12 * depthScale,
    };
  }

  function wrapParticle(particle) {
    if (particle.x < -20) particle.x = width + 20;
    if (particle.x > width + 20) particle.x = -20;
    if (particle.y < -20) particle.y = height + 20;
    if (particle.y > height + 20) particle.y = -20;
  }

  function draw() {
    if (!running) return;
    ctx.clearRect(0, 0, width, height);
    particles.forEach((p, index) => {
      p.x += p.vx;
      p.y += p.vy;
      wrapParticle(p);
      ctx.beginPath();
      ctx.fillStyle = `rgba(15,92,63,${p.alpha})`;
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      for (let j = index + 1; j < particles.length; j += 1) {
        const q = particles[j];
        const distance = Math.hypot(p.x - q.x, p.y - q.y);
        const depthAffinity = 1 - Math.abs(p.z - q.z);
        const maxDistance = 72 + depthAffinity * 82;
        if (distance < maxDistance) {
          ctx.globalAlpha = (1 - distance / maxDistance) * depthAffinity * 0.55;
          ctx.strokeStyle = `rgba(15,92,63,${0.08 + ((p.z + q.z) / 2) * 0.12})`;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(q.x, q.y);
          ctx.stroke();
          ctx.globalAlpha = 1;
        }
      }
    });
    requestAnimationFrame(draw);
  }

  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) draw();
  });
  window.addEventListener("resize", resize);
  resize();
  draw();
})();
