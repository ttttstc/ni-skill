import {AthensRelief} from './runtime/athens-effect.js';
import {DataTexture, RGBAFormat, UnsignedByteType} from './runtime/three.module.js';

const art = document.querySelector('#art');
const canvas = document.querySelector('#relief');
const base = document.querySelector('#base');
const status = document.querySelector('#status');

async function load(url) {
  const image = new Image();
  image.src = url;
  await image.decode();
  return image;
}

try {
  const response = await fetch('./manifest.json');
  if (!response.ok) throw Error('Cannot load manifest.json');
  const maps = await response.json();
  document.documentElement.style.backgroundColor = maps.background;
  art.style.aspectRatio = `${maps.width} / ${maps.height}`;
  base.src = maps.base;
  await base.decode();
  const clip = await load(maps.clip);
  await Promise.all([maps.normal, maps.mask, './runtime/clouds.jpg'].map(load));
  const relief = new AthensRelief(canvas, {
    baseTextureUrl: maps.base, normalMapUrl: maps.normal, maskUrl: maps.mask,
    topperTextureUrl: '', cloudTextureUrl: './runtime/clouds.jpg',
    smudgeBrushSize: maps.brush,
  });
  const context = relief.getCanvas2D();
  relief.getCanvas2D = () => ({
    canvas: context.canvas,
    clearRect: (...args) => context.clearRect(...args),
    drawImage: (...args) => {
      context.drawImage(...args);
      context.globalCompositeOperation = 'destination-in';
      context.drawImage(clip, 0, 0, canvas.width, canvas.height);
      context.globalCompositeOperation = 'destination-over';
      context.fillStyle = maps.background;
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.globalCompositeOperation = 'source-over';
    },
  });
  const fullReveal = new DataTexture(new Uint8Array([255, 255, 255, 255]), 1, 1, RGBAFormat, UnsignedByteType);
  fullReveal.needsUpdate = true;
  let currentMode = 'interactive';
  const renderInteractive = relief.renderFrame.bind(relief);
  relief.renderFrame = (renderer, camera, dt, time) => {
    if (['left', 'center', 'right'].includes(currentMode)) {
      // Keep revealEnabled=1: disabling reveal also disables the original cursor light.
      const uniforms = relief.material.uniforms;
      uniforms.uIntroProgress.value = 1.5;
      uniforms.uSmudgeMask.value = fullReveal;
      uniforms.uCursorPos.value.copy(relief.currentCursor);
      uniforms.uTime.value = time;
      renderer.setRenderTarget(null);
      renderer.render(relief.scene, camera);
    } else {
      renderInteractive(renderer, camera, dt, time);
    }
  };

  const deadline = performance.now() + 15000;
  await new Promise((resolve, reject) => {
    function check() {
      if (['base', 'normal', 'mask', 'cloud'].every(key => relief.textures[key])) resolve();
      else if (performance.now() > deadline) reject(Error('Material texture timeout'));
      else requestAnimationFrame(check);
    }
    check();
  });

  function setMode(mode) {
    const fixed = ['left', 'center', 'right'].includes(mode);
    canvas.hidden = mode === 'stone';
    relief.onMouseLeave();
    relief.updateConfig({revealEnabled: 1, cursorDirFollowsCursor: 1});
    currentMode = mode;
    if (fixed) {
      relief.currentCursor.set({left: 0.18, center: 0.5, right: 0.82}[mode], 0.53);
      relief.targetCursor.copy(relief.currentCursor);
      relief.prevCursor.copy(relief.currentCursor);
      relief.cursorSpeed = 0;
      relief.targetCursorSpeed = 0;
      relief.isHovering = true;
    }
    // Diagnostic modes freeze the light; interaction remains on in the normal mode.
    canvas.style.pointerEvents = fixed || mode === 'stone' ? 'none' : 'auto';
    art.style.pointerEvents = fixed || mode === 'stone' ? 'none' : 'auto';
    document.querySelectorAll('[data-mode]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
    });
    window.picarts.mode = mode;
  }

  window.picarts = {relief, maps, clip, mode: 'interactive', setMode, ready: true};
  document.querySelectorAll('[data-mode]').forEach(button => {
    button.addEventListener('click', () => setMode(button.dataset.mode));
  });
  // Release/cancel outside the figure must not leave the erosion frozen.
  window.addEventListener('mouseup', () => { relief.isMouseDown = false; });
  art.addEventListener('touchcancel', () => relief.onMouseLeave(), {passive: true});
  status.textContent = '图片已载入，可切换光源检查细节。';
} catch (error) {
  status.textContent = `互动未载入：${error.message}`;
  canvas.hidden = true;
  console.error(error);
  window.picarts = {ready: false, error: error.message};
}
