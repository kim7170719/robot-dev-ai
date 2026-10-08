const gsap = window.gsap;
const landing = document.querySelector("#landing");

if (gsap && landing) {
  const motion = gsap.matchMedia();
  motion.add("(prefers-reduced-motion: no-preference)", () => {
    const intro = gsap.timeline({
      defaults: { duration: .72, ease: "power3.out", overwrite: "auto" },
    });
    intro
      .from(".landing-topline", { autoAlpha: 0, y: -12 })
      .from(".landing-copy > p:first-child", { autoAlpha: 0, y: 14 }, "<.12")
      .from(".landing-copy h1", { autoAlpha: 0, y: 26, filter: "blur(8px)", clearProps: "filter" }, "<.08")
      .from(".landing-summary", { autoAlpha: 0, y: 18 }, "<.18")
      .from(".landing-actions > *", { autoAlpha: 0, y: 12, stagger: .1 }, "<.1")
      .from(".humanoid-stage", { autoAlpha: 0, x: 28, scale: .97, duration: 1.1 }, "intro+=.04")
      .from(".landing-status", { autoAlpha: 0, y: 10 }, "<.18");
    return () => intro.kill();
  });
}
