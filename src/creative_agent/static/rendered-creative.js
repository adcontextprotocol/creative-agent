/**
 * Web Component for embedding ADCP creative previews
 *
 * Usage:
 *   <rendered-creative src="https://preview-url.com/..."></rendered-creative>
 *
 * Attributes:
 *   - src: URL to fetch the creative HTML fragment
 *   - width: Optional width (default: from content)
 *   - height: Optional height (default: from content)
 *   - lazy: Enable lazy loading (default: true)
 *
 * Features:
 *   - Shadow DOM for CSS isolation
 *   - Lazy loading with Intersection Observer
 *   - Automatic dimensions from content
 */
class RenderedCreative extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.loaded = false;
    }

    static get observedAttributes() {
        return ['src', 'width', 'height', 'lazy'];
    }

    connectedCallback() {
        const lazy = this.getAttribute('lazy') !== 'false';

        if (lazy) {
            this.setupLazyLoading();
        } else {
            this.loadContent();
        }
    }

    setupLazyLoading() {
        // Show placeholder while not loaded
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    position: relative;
                }
                .placeholder {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #f5f5f5;
                    color: #999;
                    font-family: system-ui, -apple-system, sans-serif;
                    font-size: 14px;
                    min-height: 200px;
                }
            </style>
            <div class="placeholder">Loading preview...</div>
        `;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.loaded) {
                    this.loadContent();
                    observer.unobserve(this);
                }
            });
        }, { rootMargin: '50px' });

        observer.observe(this);
    }

    async loadContent() {
        const src = this.getAttribute('src');
        if (!src) {
            this.showError('No src attribute provided');
            return;
        }

        try {
            const response = await fetch(src);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const html = await response.text();
            this.renderContent(html);
            this.loaded = true;
        } catch (error) {
            this.showError(`Failed to load preview: ${error.message}`);
        }
    }

    renderContent(html) {
        // Parse the HTML to extract just the content we need
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Extract styles from the document
        const styles = Array.from(doc.querySelectorAll('style'))
            .map(style => style.textContent)
            .join('\n');

        // Extract body content
        const bodyContent = doc.body.innerHTML;

        // Apply dimensions if specified
        const width = this.getAttribute('width');
        const height = this.getAttribute('height');
        const hostStyles = [];
        if (width) hostStyles.push(`width: ${width}px`);
        if (height) hostStyles.push(`height: ${height}px`);

        // Render in shadow DOM
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    ${hostStyles.join('; ')};
                }
                ${styles}
            </style>
            ${bodyContent}
        `;
    }

    showError(message) {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                }
                .error {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #fee;
                    color: #c33;
                    padding: 20px;
                    border: 1px solid #fcc;
                    border-radius: 4px;
                    font-family: system-ui, -apple-system, sans-serif;
                    font-size: 14px;
                    min-height: 100px;
                }
            </style>
            <div class="error">${message}</div>
        `;
    }
}

// Register the custom element
if (!customElements.get('rendered-creative')) {
    customElements.define('rendered-creative', RenderedCreative);
}
