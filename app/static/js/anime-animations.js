(function () {
  if (!window.anime) return;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion) return;

  const title = document.querySelector(".hero-title");
  if (title) {
    title.innerHTML = title.textContent
      .split(" ")
      .map((word) => `<span class="inline-block overflow-hidden"><span class="inline-block">${word}</span></span>`)
      .join(" ");
    anime({
      targets: ".hero-title span span",
      translateY: ["110%", "0%"],
      opacity: [0, 1],
      delay: anime.stagger(55),
      duration: 880,
      easing: "easeOutExpo",
    });
  }

  const mockup = document.querySelector(".hero-mockup");
  const stage = mockup?.querySelector(".hero-depth-stage");
  const layers = stage ? Array.from(stage.querySelectorAll(".hero-depth-layer")) : [];
  const shadow = stage?.querySelector(".hero-depth-shadow");
  if (mockup && stage && layers.length) {
    layers.forEach((layer) => {
      const depth = Number(layer.dataset.depth || 0);
      if (window.gsap) {
        gsap.set(layer, { z: depth });
      } else {
        layer.style.transform = `translateZ(${depth}px)`;
      }
    });

    anime({
      targets: stage,
      opacity: [0, 1],
      rotateY: [-25, 0],
      rotateX: [10, 0],
      scale: [0.85, 1],
      translateZ: [-200, 0],
      duration: 1200,
      delay: 260,
      easing: "easeOutExpo",
    });

    anime({
      targets: layers,
      opacity: [0, 1],
      translateY: [34, 0],
      translateZ: (element) => [Number(element.dataset.depth || 0) - 120, Number(element.dataset.depth || 0)],
      delay: anime.stagger(90, { start: 420 }),
      duration: 950,
      easing: "easeOutExpo",
    });

    if (window.gsap) {
      const rotateXTo = gsap.quickTo(stage, "rotationX", { duration: 0.45, ease: "power3.out" });
      const rotateYTo = gsap.quickTo(stage, "rotationY", { duration: 0.45, ease: "power3.out" });
      const shadowXTo = shadow ? gsap.quickTo(shadow, "x", { duration: 0.45, ease: "power3.out" }) : null;
      const shadowYTo = shadow ? gsap.quickTo(shadow, "y", { duration: 0.45, ease: "power3.out" }) : null;
      const layerTweens = layers.map((layer) => ({
        xTo: gsap.quickTo(layer, "x", { duration: 0.45, ease: "power3.out" }),
        yTo: gsap.quickTo(layer, "y", { duration: 0.45, ease: "power3.out" }),
        parallax: Number(layer.dataset.parallax || 1),
      }));

      mockup.addEventListener("mousemove", (event) => {
        const rect = mockup.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        rotateYTo(x * 16);
        rotateXTo(y * -14);
        shadowXTo?.(x * -28);
        shadowYTo?.(Math.abs(x) * 8 + y * -10);
        layerTweens.forEach(({ xTo, yTo, parallax }) => {
          xTo(x * 18 * parallax);
          yTo(y * 14 * parallax);
        });
      });

      mockup.addEventListener("mouseleave", () => {
        rotateXTo(0);
        rotateYTo(0);
        shadowXTo?.(0);
        shadowYTo?.(0);
        layerTweens.forEach(({ xTo, yTo }) => {
          xTo(0);
          yTo(0);
        });
      });
    } else {
      mockup.addEventListener("mousemove", (event) => {
        const rect = mockup.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        anime({ targets: stage, rotateX: y * -14, rotateY: x * 16, duration: 350, easing: "easeOutQuad" });
      });
      mockup.addEventListener("mouseleave", () => {
        anime({ targets: stage, rotateX: 0, rotateY: 0, duration: 600, easing: "easeOutElastic(1, .7)" });
      });
    }
  }

  document.querySelectorAll(".connector path:not([data-scroll-path])").forEach((path) => {
    const length = path.getTotalLength();
    path.style.strokeDasharray = length;
    path.style.strokeDashoffset = length;
    anime({
      targets: path,
      strokeDashoffset: [length, 0],
      duration: 1600,
      easing: "easeInOutSine",
      autoplay: true,
    });
  });
})();
