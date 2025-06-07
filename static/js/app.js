// Custom JavaScript for MCP HF Hackathon Interface

// Initialize application when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  console.log("MCP HF Hackathon Application Initialized");

  // Add custom event listeners and functionality
  initializeInterface();
  setupKeyboardShortcuts();
  addStatusIndicators();
  setupEnhancedChatbotObserver();
  
  // Initialize LaTeX rendering if available
  if (window.LatexRenderer) {
    window.LatexRenderer.initializeLatexSupport();
  }
});

// Initialize the interface with custom functionality
function initializeInterface() {
  // Add loading states to buttons
  const submitButtons = document.querySelectorAll(
    'button[type="submit"], .submit-btn'
  );
  submitButtons.forEach((button) => {
    button.addEventListener("click", function () {
      showLoadingState(this);
    });
  });

  // Auto-resize textareas
  const textareas = document.querySelectorAll("textarea");
  textareas.forEach((textarea) => {
    textarea.addEventListener("input", autoResize);
  });
}

// Setup keyboard shortcuts
function setupKeyboardShortcuts() {
  document.addEventListener("keydown", function (e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      const submitBtn = document.querySelector(".submit-btn");
      if (submitBtn) {
        submitBtn.click();
      }
    }

    // Escape to clear input
    if (e.key === "Escape") {
      const activeTextarea = document.activeElement;
      if (activeTextarea && activeTextarea.tagName === "TEXTAREA") {
        activeTextarea.value = "";
        activeTextarea.dispatchEvent(new Event("input"));
      }
    }
  });
}

// Add visual status indicators
function addStatusIndicators() {
  // Monitor for status changes
  const statusElements = document.querySelectorAll('[data-testid="textbox"]');
  statusElements.forEach((element) => {
    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (
          mutation.type === "childList" ||
          mutation.type === "characterData"
        ) {
          updateStatusIndicator(element);
        }
      });
    });

    observer.observe(element, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  });
}

// Show loading state on button
function showLoadingState(button) {
  const originalText = button.textContent;
  button.textContent = "Processing...";
  button.disabled = true;
  button.classList.add("loading-state");

  // Reset after 3 seconds (fallback)
  setTimeout(() => {
    button.textContent = originalText;
    button.disabled = false;
    button.classList.remove("loading-state");
  }, 3000);
}

// Auto-resize textarea based on content
function autoResize() {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
}

// Update status indicator based on content
function updateStatusIndicator(element) {
  const text = element.textContent.toLowerCase();

  // Remove existing status classes
  element.classList.remove(
    "status-success",
    "status-error",
    "status-processing"
  );

  // Add appropriate status class
  if (text.includes("success") || text.includes("completed")) {
    element.classList.add("status-success");
  } else if (text.includes("error") || text.includes("failed")) {
    element.classList.add("status-error");
  } else if (text.includes("processing") || text.includes("loading")) {
    element.classList.add("status-processing");
  }
}

// Utility function to copy text to clipboard
function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(function () {
      showNotification("Copied to clipboard!");
    })
    .catch(function (err) {
      console.error("Could not copy text: ", err);
    });
}

// Show temporary notification
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #3b82f6;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        font-weight: 500;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;

  if (type === "error") {
    notification.style.background = "#dc2626";
  } else if (type === "success") {
    notification.style.background = "#059669";
  }

  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.transform = "translateX(0)";
  }, 100);

  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.transform = "translateX(100%)";
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// Process LaTeX in chatbot messages
function processLatexInChatbot() {
  if (window.LatexRenderer && window.LatexRenderer.processAllLatex) {
    console.log("Processing LaTeX in chatbot messages");
    window.LatexRenderer.processAllLatex();
  }
}

// Enhanced observer for chatbot content changes
function setupEnhancedChatbotObserver() {
  const chatbotContainer = document.querySelector('[data-testid="chatbot"], .main-chatbot, .gradio-chatbot');
  
  if (!chatbotContainer) {
    setTimeout(setupEnhancedChatbotObserver, 1000);
    return;
  }
  
  const observer = new MutationObserver((mutations) => {
    let hasNewContent = false;
    
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        hasNewContent = true;
      }
    });
    
    if (hasNewContent) {
      // Delay to ensure content is fully rendered
      setTimeout(() => {
        processLatexInChatbot();
      }, 200);
    }
  });
  
  observer.observe(chatbotContainer, {
    childList: true,
    subtree: true
  });
}

// Export functions for use in other scripts
window.MCPInterface = {
  copyToClipboard,
  showNotification,
  showLoadingState,
  processLatexInChatbot,
};
