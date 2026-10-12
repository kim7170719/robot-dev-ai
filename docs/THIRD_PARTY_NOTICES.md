# Third-party notices

## Three.js

The local landing-page WebGL runtime, including the GLTFLoader and Meshopt
decoder addons, is derived from the
[Three.js repository](https://github.com/mrdoob/three.js), which is released
under the MIT License.

Copyright © 2010–2026 Three.js authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## GSAP

The landing-page entry choreography locally vendors GSAP 3.12.5 as
`gui/vendor/gsap.min.js`. It is distributed by GreenSock under the
[GSAP Standard License](https://gsap.com/standard-license/). The original
copyright and license header remains in the vendored file. GSAP only
orchestrates DOM entry motion; it has no ROS, API, or simulator access.

## User-supplied humanoid GLB

`gui/assets/humanoid-reference.glb` and `gui/assets/humanoid-rigged.glb` are
Web-optimised derivatives of GLBs the project user supplied on 2026-10-12. The
source metadata names `Tripo` as generator. The rigged asset includes a 78-joint
skeleton and five animation clips; both assets are used only for landing-page
visuals and do not represent robot capabilities, an Isaac Sim scene, or
physical hardware. The user must retain the source models' applicable licence
and usage rights before any public deployment.
