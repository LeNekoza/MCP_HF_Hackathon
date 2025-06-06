/**
 * LaTeX Renderer for MCP HF Hackathon Chatbot
 * Provides LaTeX/MathJax rendering capabilities for medical formulas and calculations
 */

// MathJax configuration
window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true,
    packages: ['base', 'ams', 'noerrors', 'noundefined', 'autoload', 'configmacros']
  },
  options: {
    ignoreHtmlClass: 'tex2jax_ignore',
    processHtmlClass: 'tex2jax_process'
  },
  startup: {
    ready() {
      console.log('MathJax is loaded and ready');
      MathJax.startup.defaultReady();
      
      // Process any existing content
      processExistingLatex();
    }
  }
};

// Load MathJax library
function loadMathJax() {
  if (window.MathJax && window.MathJax.typesetPromise) {
    return Promise.resolve();
  }
  
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js';
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// Process LaTeX content in a specific element
function processLatexInElement(element) {
  if (!window.MathJax || !window.MathJax.typesetPromise) {
    console.warn('MathJax not loaded, queueing for later processing');
    return;
  }
  
  try {
    // Add processing class to prevent double processing
    element.classList.add('tex2jax_process');
    
    // Use MathJax to render the content
    MathJax.typesetPromise([element]).then(() => {
      console.log('LaTeX processed successfully in element');
    }).catch((err) => {
      console.error('LaTeX processing error:', err);
    });
  } catch (error) {
    console.error('Error processing LaTeX:', error);
  }
}

// Process all LaTeX content on the page
function processAllLatex() {
  if (!window.MathJax || !window.MathJax.typesetPromise) {
    console.warn('MathJax not loaded, cannot process LaTeX');
    return;
  }
  
  try {
    MathJax.typesetPromise().then(() => {
      console.log('All LaTeX content processed');
    }).catch((err) => {
      console.error('Error processing all LaTeX:', err);
    });
  } catch (error) {
    console.error('Error in processAllLatex:', error);
  }
}

// Process existing LaTeX content when MathJax loads
function processExistingLatex() {
  // Look for chatbot messages that might contain LaTeX
  const chatbotElements = document.querySelectorAll('[data-testid="chatbot"] .message, .chatbot .message, .gradio-chatbot .message');
  
  chatbotElements.forEach(element => {
    if (containsLatex(element.textContent || element.innerHTML)) {
      processLatexInElement(element);
    }
  });
}

// Check if text contains LaTeX syntax
function containsLatex(text) {
  const latexPatterns = [
    /\\\(.*?\\\)/g,  // Inline math \( ... \)
    /\\\[.*?\\\]/g,  // Display math \[ ... \]
    /\$\$.*?\$\$/g,  // Display math $$ ... $$
    /\$[^$]+\$/g,    // Inline math $ ... $
    /\\frac\{/g,     // Fractions
    /\\sqrt\{/g,     // Square roots
    /\\sum\b/g,      // Summation
    /\\int\b/g,      // Integrals
    /\\alpha\b/g,    // Greek letters
    /\\beta\b/g,
    /\\gamma\b/g,
    /\\times\b/g,    // Multiplication
    /\\cdot\b/g,     // Dot product
    /\\pm\b/g,       // Plus-minus
    /\\geq\b/g,      // Greater than or equal
    /\\leq\b/g,      // Less than or equal
    /\\neq\b/g,      // Not equal
    /\\approx\b/g,   // Approximately equal
  ];
  
  return latexPatterns.some(pattern => pattern.test(text));
}

// Observer to detect new chatbot messages
function setupChatbotObserver() {
  const chatbotContainer = document.querySelector('[data-testid="chatbot"], .chatbot, .gradio-chatbot');
  
  if (!chatbotContainer) {
    console.log('Chatbot container not found, will retry later');
    setTimeout(setupChatbotObserver, 1000);
    return;
  }
  
  console.log('Setting up chatbot observer for LaTeX rendering');
  
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if the new node or its children contain LaTeX
            const textContent = node.textContent || node.innerHTML || '';
            if (containsLatex(textContent)) {
              console.log('New LaTeX content detected, processing...');
              setTimeout(() => processLatexInElement(node), 100);
            }
            
            // Also check child elements
            const childElements = node.querySelectorAll ? node.querySelectorAll('*') : [];
            childElements.forEach(child => {
              const childText = child.textContent || child.innerHTML || '';
              if (containsLatex(childText)) {
                console.log('Child LaTeX content detected, processing...');
                setTimeout(() => processLatexInElement(child), 100);
              }
            });
          }
        });
      } else if (mutation.type === 'characterData') {
        // Text content changed
        const textContent = mutation.target.textContent || '';
        if (containsLatex(textContent)) {
          console.log('LaTeX content in text change detected, processing...');
          const parentElement = mutation.target.parentElement;
          if (parentElement) {
            setTimeout(() => processLatexInElement(parentElement), 100);
          }
        }
      }
    });
  });
  
  observer.observe(chatbotContainer, {
    childList: true,
    subtree: true,
    characterData: true
  });
}

// Initialize LaTeX support
function initializeLatexSupport() {
  console.log('Initializing LaTeX support...');
  
  loadMathJax().then(() => {
    console.log('MathJax loaded successfully');
    setupChatbotObserver();
    
    // Process any existing content
    setTimeout(processExistingLatex, 500);
  }).catch((error) => {
    console.error('Failed to load MathJax:', error);
  });
}

// Export functions for use in other scripts
window.LatexRenderer = {
  processLatexInElement,
  processAllLatex,
  containsLatex,
  initializeLatexSupport
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeLatexSupport);
} else {
  initializeLatexSupport();
} 