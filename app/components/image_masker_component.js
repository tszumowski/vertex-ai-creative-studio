import { LitElement, html, css } from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

class ImageMaskerComponent extends LitElement {
  static properties = {
    img_src: { type: String },
    brushType: { type: String },
    brushSize: { type: Number },
    maskChangeEvent: { type: String },
  };

  static styles = css`
    :host {
      display: block;
    }
    .container {
      position: relative;
      overflow: hidden;
    }
    canvas {
      position: absolute;
      top: 0;
      left: 0;
      pointer-events: none;
    }
    img {
      display: block;
      max-width: 100%;
      height: auto;
    }

    /* Styling for the controls (replace with your actual styles) */
    .controls {
        padding: 16px; /* Example padding */
        display: flex;
        flex-direction: column;
        gap: 8px; /* Spacing between elements */
    }
    .button-group {
        display: flex;
        gap: 8px;
    }
    .slider-container {
        display: flex;
        flex-direction: column;
    }

  `;

  constructor() {
    super();
    this.img_src = "";
    this.brushType = "Brush";
    this.brushSize = 5;
    this.maskChangeEvent = "";
    this.drawing = false;
    this.lastX = 0;
    this.lastY = 0;
    this.history = []; // Undo/redo history
    this.historyIndex = -1;
    console.log("Instantiated.")
  }

    firstUpdated() {
        this.img = this.shadowRoot.querySelector('img');
        this.canvas = this.shadowRoot.querySelector('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.container = this.shadowRoot.querySelector('.container');

        this.img.addEventListener('load', () => this.resizeCanvas());
        this.img.addEventListener('error', (error) => console.error("Error loading image:", error));

        this.container.addEventListener('mousedown', this.startDrawing.bind(this));
        this.container.addEventListener('mousemove', this.draw.bind(this));
        this.container.addEventListener('mouseup', this.stopDrawing.bind(this));
        this.container.addEventListener('mouseout', this.stopDrawing.bind(this));

        this.container.addEventListener('touchstart', this.startDrawing.bind(this));
        this.container.addEventListener('touchmove', this.draw.bind(this));
        this.container.addEventListener('touchend', this.stopDrawing.bind(this));

        this.canvas.addEventListener('mouseup', this.handleMaskChange.bind(this));
        this.container.addEventListener('mouseout', this.handleMaskChange.bind(this));
        this.container.addEventListener('touchend', this.handleMaskChange.bind(this));
    }


  render() {
    return html`
      <div class="controls">
        <div class="button-group">
            <button @click=${() => this.setBrushType('Brush')}>
                <i class="material-icons">draw</i> Brush
            </button>
            <button @click=${() => this.setBrushType('Eraser')}>
                <i class="material-icons">drive_file_rename_outline</i> Eraser
            </button>
            <button @click=${this.handleUndoClick}>
                <i class="material-icons">undo</i> Undo
            </button>
            <button @click=${this.handleRedoClick}>
                <i class="material-icons">redo</i> Redo
            </button>
            <button @click=${this.handleClearClick}>
                <i class="material-icons">clear</i> Clear
            </button>
        </div>
        <div class="slider-container">
            <span>${this.brushType} size</span>
            <input type="range" min="1" max="50" value=${this.brushSize} @input=${this.handleBrushSizeChange} />
        </div>
      </div>
      <div class="container">
        <img src="${this.img_src}" alt="" draggable="false">
        <canvas></canvas>
      </div>
    `;
  }

  setBrushType(type) {
    this.brushType = type;
  }

  handleBrushSizeChange(e) {
    this.brushSize = parseInt(e.target.value); // Parse to integer
  }

  resizeCanvas() {
      this.canvas.width = this.img.offsetWidth;
      this.canvas.height = this.img.offsetHeight;
      this.redrawMask(); // Redraw the mask when resized
  }

  startDrawing(e) {
    this.drawing = true;
    const { offsetX, offsetY } = this.getMousePos(e);
    this.lastX = offsetX;
    this.lastY = offsetY;
  }

  draw(e) {
    if (!this.drawing) return;

    const { offsetX, offsetY } = this.getMousePos(e);

    this.ctx.beginPath();
    this.ctx.moveTo(this.lastX, this.lastY);
    this.ctx.lineTo(offsetX, offsetY);
    this.ctx.strokeStyle = this.brushType === 'Brush' ? 'black' : 'transparent'; // Use transparent for eraser
    this.ctx.lineWidth = this.brushSize;
    this.ctx.lineCap = "round";
    this.ctx.stroke();

    this.lastX = offsetX;
    this.lastY = offsetY;

    this.addToHistory(); // Add to history after each stroke
  }

  stopDrawing() {
    this.drawing = false;
  }

  getMousePos(e) {
    const rect = this.container.getBoundingClientRect();
    if (e.type.startsWith('mouse')) {
      return {
        offsetX: e.clientX - rect.left,
        offsetY: e.clientY - rect.top
      };
    } else if (e.type.startsWith('touch')) {
      const touch = e.touches[0];
      return {
        offsetX: touch.clientX - rect.left,
        offsetY: touch.clientY - rect.top
      };
    }
  }

  getMaskData() {
    return this.canvas.toDataURL();
  }

  clearMask() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.history = [];
    this.historyIndex = -1;
    this.handleMaskChange();
  }

  handleMaskChange() {
    const maskData = this.getMaskData();
    this.dispatchEvent(
      new MesopEvent(this.maskChangeEvent, {
        mask: maskData,
      }),
    );
  }

  handleClearClick() {
    this.clearMask();
  }


  handleUndoClick() {
      if (this.historyIndex > 0) {
          this.historyIndex--;
          this.ctx.putImageData(this.history[this.historyIndex], 0, 0);
          this.handleMaskChange();
      }
  }

  handleRedoClick() {
      if (this.historyIndex < this.history.length - 1) {
          this.historyIndex++;
          this.ctx.putImageData(this.history[this.historyIndex], 0, 0);
          this.handleMaskChange();
      }
  }

  addToHistory() {
    const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    this.history = this.history.slice(0, this.historyIndex + 1); // Discard future history on new draw
    this.history.push(imageData);
    this.historyIndex++;
  }

  redrawMask() {
      if (this.historyIndex >= 0) {
          this.ctx.putImageData(this.history[this.historyIndex], 0, 0);
      }
  }

}

customElements.define('image-masker-component', ImageMaskerComponent);