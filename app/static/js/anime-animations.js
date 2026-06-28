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
  if (mockup) {
    mockup.addEventListener("mousemove", (event) => {
      const rect = mockup.getBoundingClientRect();
      const rotateY = ((event.clientX - rect.left) / rect.width - 0.5) * 14;
      const rotateX = (((event.clientY - rect.top) / rect.height - 0.5) * -14);
      anime({ targets: mockup, rotateX, rotateY, duration: 350, easing: "easeOutQuad" });
    });
    mockup.addEventListener("mouseleave", () => {
      anime({ targets: mockup, rotateX: 0, rotateY: 0, duration: 600, easing: "easeOutElastic(1, .7)" });
    });
  }

  document.querySelectorAll(".connector path").forEach((path) => {
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

