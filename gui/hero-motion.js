const gsap = window.gsap;
const landing = document.querySelector("#landing");

if (gsap && landing) {
  const motion = gsap.matchMedia();
  motion.add("(prefers-reduced-motion: no-preference)", () => {
    const intro = gsap.timeline({
      defaults: { duration: .74, ease: "power3.out", overwrite: "auto" },
    });
    intro
      .from(".landing-topline", { autoAlpha: 0, y: -10 })
      .from(".landing-copy h1", { autoAlpha: 0, y: 34, clipPath: "inset(0 0 100% 0)", clearProps: "clipPath" }, "<.16")
      .from(".landing-summary", { autoAlpha: 0, y: 18 }, "<.24")
      .from(".landing-actions > *", { autoAlpha: 0, y: 12, stagger: .1 }, "<.1")
      .from(".humanoid-stage", { autoAlpha: 0, x: 48, scale: .96, rotationY: -4, transformOrigin: "center center", duration: 1.1 }, "intro+=.04")
      .from(".landing-status", { autoAlpha: 0, y: 10 }, "<.2");
    return () => intro.kill();
  });
}
