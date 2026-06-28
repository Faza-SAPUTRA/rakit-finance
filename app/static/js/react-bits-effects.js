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
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
    }));
  }

  function draw() {
    if (!running) return;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "rgba(15,92,63,.18)";
    ctx.strokeStyle = "rgba(15,92,63,.08)";
    particles.forEach((p, index) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 1.6, 0, Math.PI * 2);
      ctx.fill();
      for (let j = index + 1; j < particles.length; j += 1) {
        const q = particles[j];
        const distance = Math.hypot(p.x - q.x, p.y - q.y);
        if (distance < 115) {
          ctx.globalAlpha = 1 - distance / 115;
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

