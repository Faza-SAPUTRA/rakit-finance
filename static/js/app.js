(function () {
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  ready(function () {
    var motionOkay = !prefersReducedMotion();
    var gsap = motionOkay ? window.gsap : null;

    initLoadingSkeleton(gsap);

    if (window.lucide) {
      window.lucide.createIcons();
    }

    initPageMotion(gsap);
    initRipple(gsap);
    initClickFeedback(gsap);
    initModals(gsap);
    initSegmented(gsap);
    initCustomSelects(gsap);
    initInvestmentCards(gsap);
    initProgressBars(gsap);
    initPasswordToggles();
    initToasts(gsap);
    initFileInputs();
    initCharts();
  });

  function initLoadingSkeleton(gsap) {
    var body = document.body;
    var shell = document.querySelector(".loading-shell");
    if (!body || !shell) return;

    function hideSkeleton() {
      if (!body.classList.contains("is-loading")) return;
      if (gsap) {
        gsap.to(shell, {
          autoAlpha: 0,
          duration: 0.28,
          ease: "power2.out",
          onComplete: function () {
            body.classList.remove("is-loading");
            shell.removeAttribute("style");
          },
        });
      } else {
        body.classList.remove("is-loading");
      }
    }

    function showSkeleton() {
      body.classList.add("is-loading");
    }

    window.addEventListener("load", function () {
      window.setTimeout(hideSkeleton, prefersReducedMotion() ? 0 : 260);
    });

    window.setTimeout(hideSkeleton, 1400);

    document.addEventListener("click", function (event) {
      var link = event.target.closest("a[href]");
      if (!link) return;
      var href = link.getAttribute("href") || "";
      var target = link.getAttribute("target");
      var download = link.hasAttribute("download");
      var sameOrigin = !link.origin || link.origin === window.location.origin;
      if (download || link.dataset.downloadLink !== undefined) {
        showButtonLoading(link);
        return;
      }
      if (!sameOrigin || target || href.startsWith("#") || href.startsWith("javascript:") || link.dataset.openModal !== undefined) {
        return;
      }
      showSkeleton();
    });

    document.addEventListener("submit", function (event) {
      if (!event.defaultPrevented) showSkeleton();
    });
  }

  function showButtonLoading(button) {
    if (!button || button.classList.contains("is-button-loading")) return;
    var original = button.innerHTML;
    button.dataset.originalHtml = original;
    button.classList.add("is-button-loading");
    button.innerHTML = '<span class="button-spinner"></span><span>Preparing</span>';
    window.setTimeout(function () {
      button.classList.remove("is-button-loading");
      button.innerHTML = button.dataset.originalHtml || original;
      delete button.dataset.originalHtml;
      if (window.lucide) window.lucide.createIcons();
    }, 1200);
  }

  function initPageMotion(gsap) {
    if (!gsap) return;

    var authItems = document.querySelectorAll(
      ".auth-brand .brand, .auth-brand h1, .auth-brand p, .trust-row, .feature-pills, .auth-card > *"
    );
    if (authItems.length) {
      gsap.from(authItems, {
        autoAlpha: 0,
        y: 18,
        duration: 0.68,
        ease: "power3.out",
        stagger: 0.055,
      });
    }

    var appItems = document.querySelectorAll(
      ".topbar, .metric-card, .dashboard-grid > *, .content-two-col > *, .market-card, .news-panel, .analytics-bottom > *, .investment-types > *, .investment-grid > *, .growth-table, .accounts-grid > *"
    );
    if (appItems.length) {
      gsap.from(appItems, {
        autoAlpha: 0,
        y: 18,
        scale: 0.985,
        duration: 0.55,
        ease: "power3.out",
        stagger: 0.045,
      });
    }

    gsap.from(".nav-menu a", {
      autoAlpha: 0,
      x: -12,
      duration: 0.45,
      ease: "power3.out",
      stagger: 0.035,
      delay: 0.05,
    });
  }

  function initRipple(gsap) {
    var targets = document.querySelectorAll(".btn, .icon-btn, .nav-menu a");
    targets.forEach(function (target) {
      target.addEventListener("click", function (event) {
        var rect = target.getBoundingClientRect();
        var ripple = document.createElement("span");
        var size = Math.max(rect.width, rect.height) * 2.3;
        ripple.className = "ripple";
        ripple.style.left = event.clientX - rect.left + "px";
        ripple.style.top = event.clientY - rect.top + "px";
        target.appendChild(ripple);

        if (gsap) {
          gsap.to(ripple, {
            width: size,
            height: size,
            autoAlpha: 0,
            scale: 1,
            duration: 0.58,
            ease: "power2.out",
            onComplete: function () {
              ripple.remove();
            },
          });
        } else {
          ripple.remove();
        }
      });
    });
  }

  function initClickFeedback(gsap) {
    var selectors = [
      ".metric-card",
      ".panel:not(.table-panel)",
      ".market-card",
      ".investment-types article",
      ".wallet-list article",
      ".goal-card",
      ".insight-card",
      ".spending-card",
      ".limit-card",
      ".upload-box",
      ".dropzone",
      ".rakit-table tbody tr",
    ].join(",");

    document.querySelectorAll(selectors).forEach(function (item) {
      item.classList.add("click-pop");
      item.addEventListener("click", function () {
        if (!gsap) return;
        gsap.killTweensOf(item);
        gsap.fromTo(
          item,
          { scale: 0.985 },
          { scale: 1, duration: 0.46, ease: "elastic.out(1, 0.5)" }
        );

        var icon = item.querySelector("svg");
        if (icon) {
          gsap.fromTo(
            icon,
            { rotate: -8, scale: 0.9 },
            { rotate: 0, scale: 1, duration: 0.5, ease: "elastic.out(1, 0.45)" }
          );
        }
      });
    });
  }

  function initModals(gsap) {
    document.querySelectorAll("[data-open-modal]").forEach(function (button) {
      button.addEventListener("click", function () {
        var modal = document.getElementById(button.dataset.openModal);
        if (!modal) return;
        openModal(modal, gsap);
      });
    });

    document.querySelectorAll("[data-close-modal], .modal-backdrop").forEach(function (item) {
      item.addEventListener("click", function (event) {
        if (event.target === item || item.hasAttribute("data-close-modal")) {
          closeModal(item.closest(".modal-backdrop"), gsap);
        }
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      document.querySelectorAll(".modal-backdrop.open").forEach(function (modal) {
        closeModal(modal, gsap);
      });
    });
  }

  function openModal(modal, gsap) {
    if (modal.parentElement !== document.body) {
      document.body.appendChild(modal);
    }
    var card = modal.querySelector(".modal-card");
    modal.classList.add("open");
    document.body.classList.add("modal-open");

    if (!gsap || !card) {
      modal.style.opacity = "1";
      return;
    }

    gsap.killTweensOf([modal, card]);
    gsap.set(modal, { autoAlpha: 0, backdropFilter: "blur(0px)" });
    gsap.set(card, { autoAlpha: 0, y: 26, scale: 0.94, rotateX: -5 });
    gsap
      .timeline()
      .to(modal, {
        autoAlpha: 1,
        backdropFilter: "blur(3px)",
        duration: 0.2,
        ease: "power2.out",
      })
      .to(
        card,
        {
          autoAlpha: 1,
          y: 0,
          scale: 1,
          rotateX: 0,
          duration: 0.48,
          ease: "back.out(1.65)",
        },
        "-=0.05"
      );
  }

  function closeModal(modal, gsap) {
    if (!modal) return;
    var card = modal.querySelector(".modal-card");

    if (!gsap || !card) {
      modal.classList.remove("open");
      if (!document.querySelector(".modal-backdrop.open")) {
        document.body.classList.remove("modal-open");
      }
      modal.style.opacity = "";
      return;
    }

    gsap.killTweensOf([modal, card]);
    gsap
      .timeline({
        onComplete: function () {
          modal.classList.remove("open");
          if (!document.querySelector(".modal-backdrop.open")) {
            document.body.classList.remove("modal-open");
          }
          gsap.set([modal, card], { clearProps: "all" });
        },
      })
      .to(card, {
        autoAlpha: 0,
        y: 16,
        scale: 0.97,
        duration: 0.18,
        ease: "power2.in",
      })
      .to(
        modal,
        {
          autoAlpha: 0,
          backdropFilter: "blur(0px)",
          duration: 0.16,
          ease: "power2.in",
        },
        "-=0.08"
      );
  }

  function initSegmented(gsap) {
    document.querySelectorAll(".segmented").forEach(function (segmented) {
      var hidden = segmented.parentElement.querySelector('input[name="tx_type"]');
      segmented.querySelectorAll("button").forEach(function (button) {
        button.addEventListener("click", function () {
          segmented.querySelectorAll("button").forEach(function (other) {
            other.classList.remove("active");
          });
          button.classList.add("active");
          if (hidden) hidden.value = button.textContent.trim().toLowerCase();

          if (gsap) {
            gsap.fromTo(
              button,
              { scale: 0.94 },
              { scale: 1, duration: 0.38, ease: "elastic.out(1, 0.45)" }
            );
          }
        });
      });
    });
  }

  function initCustomSelects(gsap) {
    document.querySelectorAll("select").forEach(function (select) {
      if (select.dataset.enhancedSelect === "true") return;
      select.dataset.enhancedSelect = "true";

      var wrapper = document.createElement("div");
      wrapper.className = "custom-select";
      select.parentNode.insertBefore(wrapper, select);
      wrapper.appendChild(select);

      var button = document.createElement("button");
      button.type = "button";
      button.className = "custom-select__button";
      button.setAttribute("aria-haspopup", "listbox");
      button.setAttribute("aria-expanded", "false");
      button.innerHTML = '<span></span><i data-lucide="chevron-down"></i>';
      wrapper.appendChild(button);

      var list = document.createElement("div");
      list.className = "custom-select__menu";
      list.setAttribute("role", "listbox");
      wrapper.appendChild(list);

      function selectedOption() {
        return select.options[select.selectedIndex] || select.options[0];
      }

      function syncButton() {
        var current = selectedOption();
        button.querySelector("span").textContent = current ? current.textContent : "";
      }

      function closeMenu() {
        wrapper.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
      }

      function openMenu() {
        document.querySelectorAll(".custom-select.open").forEach(function (item) {
          if (item !== wrapper) item.classList.remove("open");
        });
        wrapper.classList.add("open");
        button.setAttribute("aria-expanded", "true");
        if (gsap) {
          gsap.fromTo(list, { autoAlpha: 0, y: -4 }, { autoAlpha: 1, y: 0, duration: 0.16, ease: "power2.out" });
        }
      }

      function buildOptions() {
        list.innerHTML = "";
        Array.prototype.forEach.call(select.options, function (option) {
          var item = document.createElement("button");
          item.type = "button";
          item.className = "custom-select__option";
          item.setAttribute("role", "option");
          item.dataset.value = option.value;
          item.textContent = option.textContent;
          if (option.selected) {
            item.classList.add("selected");
            item.setAttribute("aria-selected", "true");
          }
          item.addEventListener("click", function () {
            select.value = option.value;
            select.dispatchEvent(new Event("change", { bubbles: true }));
            syncButton();
            buildOptions();
            closeMenu();
          });
          list.appendChild(item);
        });
      }

      button.addEventListener("click", function () {
        if (wrapper.classList.contains("open")) closeMenu();
        else openMenu();
      });

      button.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeMenu();
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          if (wrapper.classList.contains("open")) closeMenu();
          else openMenu();
        }
      });

      select.addEventListener("change", function () {
        syncButton();
        buildOptions();
      });

      syncButton();
      buildOptions();
      if (window.lucide) window.lucide.createIcons();
    });

    document.addEventListener("click", function (event) {
      if (event.target.closest(".custom-select")) return;
      document.querySelectorAll(".custom-select.open").forEach(function (item) {
        item.classList.remove("open");
        var button = item.querySelector(".custom-select__button");
        if (button) button.setAttribute("aria-expanded", "false");
      });
    });
  }

  function initInvestmentCards(gsap) {
    document.querySelectorAll(".investment-types article").forEach(function (card) {
      card.addEventListener("click", function () {
        var group = card.closest(".investment-types");
        if (!group) return;
        group.querySelectorAll("article").forEach(function (item) {
          item.classList.remove("active");
        });
        card.classList.add("active");
        if (gsap) {
          gsap.fromTo(card, { y: 3 }, { y: 0, duration: 0.35, ease: "power3.out" });
        }
      });
    });
  }

  function initProgressBars(gsap) {
    if (!gsap) return;
    document.querySelectorAll(".progress b").forEach(function (bar) {
      var width = bar.style.width || "100%";
      gsap.fromTo(
        bar,
        { scaleX: 0 },
        { scaleX: 1, duration: 0.85, ease: "power3.out", delay: 0.18 }
      );
      bar.style.width = width;
    });
  }

  function initPasswordToggles() {
    document.querySelectorAll(".password-toggle").forEach(function (button) {
      button.addEventListener("click", function () {
        var input = button.parentElement.querySelector("input");
        if (!input) return;
        var hidden = input.type === "password";
        input.type = hidden ? "text" : "password";
        button.setAttribute("aria-label", hidden ? "Hide password" : "Show password");
        if (window.lucide) window.lucide.createIcons();
      });
    });
  }

  function initToasts(gsap) {
    document.querySelectorAll("[data-toast]").forEach(function (item) {
      item.addEventListener("click", function () {
        showToast(item.dataset.toast, gsap);
      });
    });
  }

  function showToast(message, gsap) {
    if (!message) return;
    var toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    if (gsap) {
      gsap.fromTo(
        toast,
        { autoAlpha: 0, y: 16, scale: 0.96 },
        {
          autoAlpha: 1,
          y: 0,
          scale: 1,
          duration: 0.25,
          ease: "power3.out",
          onComplete: function () {
            gsap.to(toast, {
              autoAlpha: 0,
              y: 10,
              duration: 0.25,
              delay: 2.3,
              onComplete: function () {
                toast.remove();
              },
            });
          },
        }
      );
    } else {
      window.setTimeout(function () {
        toast.remove();
      }, 2500);
    }
  }

  function initFileInputs() {
    document.querySelectorAll(".upload-box").forEach(function (form) {
      var input = form.querySelector('input[type="file"]');
      var button = form.querySelector("button[type='submit']");
      var fileName = form.querySelector("[data-file-name]");
      if (!input || !button) return;
      button.addEventListener("click", function (event) {
        if (!input.files.length) {
          event.preventDefault();
          input.click();
        }
      });
      input.addEventListener("change", function () {
        if (!input.files.length) return;
        if (fileName) fileName.textContent = input.files[0].name;
        form.requestSubmit();
      });
    });

    document.querySelectorAll(".dropzone input[type='file']").forEach(function (input) {
      input.addEventListener("change", function () {
        var zone = input.closest(".dropzone");
        var label = zone && zone.querySelector("span");
        if (label && input.files.length) {
          label.textContent = input.files[0].name;
        }
        var scanner = input.closest(".scanner-card");
        if (scanner && input.files.length) {
          var result = scanner.querySelector(".scan-result");
          var button = scanner.querySelector('button[type="submit"]');
          if (result) {
            result.classList.remove("scan-result--empty");
            result.innerHTML = [
              "<strong>SCANNING RESULT</strong>",
              "<p><span>Amount</span><b>$45.00</b></p>",
              "<p><span>Date</span><b>Today</b></p>",
              "<p><span>Merchant</span><b>Whole Foods</b></p>",
              "<small>This demo does not run OCR yet. Confirm only after editing the transaction details if needed.</small>"
            ].join("");
          }
          if (button) button.disabled = false;
        }
      });
    });
  }

  function initCharts() {
    if (!window.Chart) return;

    var cashflow = document.getElementById("cashflowChart");
    if (cashflow) {
      new Chart(cashflow, {
        type: "line",
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          datasets: [
            {
              label: "Income",
              data: [44, 57, 61, 55, 63, 83],
              borderColor: "#07b86f",
              borderWidth: 9,
              tension: 0.45,
              pointRadius: 0,
            },
            {
              label: "Expense",
              data: [37, 44, 43, 37, 42, 55],
              borderColor: "#24479e",
              borderWidth: 8,
              tension: 0.45,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          animation: { duration: prefersReducedMotion() ? 0 : 900, easing: "easeOutQuart" },
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          scales: {
            x: { grid: { display: false }, border: { display: false }, ticks: { color: "#9aa8bb" } },
            y: { display: false, min: 20, max: 90 },
          },
        },
      });
    }

    document.querySelectorAll(".sparkline").forEach(function (canvas) {
      var up = canvas.dataset.direction === "up";
      new Chart(canvas, {
        type: "line",
        data: {
          labels: ["", "", "", "", "", "", "", ""],
          datasets: [
            {
              data: up ? [28, 34, 31, 42, 38, 49, 44, 52, 47] : [50, 46, 40, 43, 35, 40, 37, 34],
              borderColor: up ? "#07b86f" : "#ff4f64",
              backgroundColor: up ? "rgba(7,184,111,.12)" : "rgba(255,79,100,.12)",
              fill: true,
              borderWidth: 5,
              tension: 0.25,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          animation: { duration: prefersReducedMotion() ? 0 : 650, easing: "easeOutQuart" },
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          scales: { x: { display: false }, y: { display: false } },
        },
      });
    });

    var portfolio = document.getElementById("portfolioChart");
    if (portfolio) {
      new Chart(portfolio, {
        type: "doughnut",
        data: {
          labels: ["Crypto", "Bonds", "Stocks", "Cash"],
          datasets: [
            {
              data: [45, 30, 15, 10],
              backgroundColor: ["#07b86f", "#0b4267", "#37d8c8", "#dfe6ef"],
              borderWidth: 10,
              borderColor: "#f8fafc",
            },
          ],
        },
        options: {
          cutout: "65%",
          animation: { duration: prefersReducedMotion() ? 0 : 900, easing: "easeOutQuart" },
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
        },
      });
    }

    var investment = document.getElementById("investmentChart");
    if (investment) {
      new Chart(investment, {
        type: "line",
        data: {
          labels: JSON.parse(investment.dataset.labels),
          datasets: [
            {
              label: "Balance",
              data: JSON.parse(investment.dataset.values),
              borderColor: "#3798c5",
              backgroundColor: "rgba(7,184,111,.42)",
              fill: true,
              borderWidth: 0,
              tension: 0.22,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          animation: { duration: prefersReducedMotion() ? 0 : 850, easing: "easeOutQuart" },
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: "#8ea0b6" } },
            y: { grid: { color: "rgba(226,232,240,.8)" }, border: { display: false }, ticks: { display: false } },
          },
        },
      });
    }
  }
})();
