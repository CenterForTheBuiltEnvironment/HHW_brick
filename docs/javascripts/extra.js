// Custom JavaScript for HHW Brick Application Documentation

document.addEventListener('DOMContentLoaded', function() {
  console.log('HHW Brick Application Documentation loaded');

  // Add external link icon to all external links
  document.querySelectorAll('a[href^="http"]').forEach(function(link) {
    if (!link.hostname.includes(window.location.hostname)) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
});
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Buttons */
.md-button {
  border-radius: 0.3rem;
}

/* Tables */
.md-typeset table:not([class]) {
  border-radius: 0.5rem;
  overflow: hidden;
}

/* Custom feature boxes */
.feature-box {
  padding: 1.5rem;
  margin: 1rem 0;
  border-left: 4px solid var(--md-primary-fg-color);
  background: rgba(63, 81, 181, 0.05);
  border-radius: 0.3rem;
}

/* Code annotation */
.md-typeset code {
  border-radius: 0.2rem;
}

/* Mermaid diagrams */
.mermaid {
  text-align: center;
  margin: 1rem 0;
}
