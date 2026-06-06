/*
 * TRIZEL Monitor - Minimal JavaScript
 * Zero interpretation, facts-only UI interactions
 */

// Load build metadata and display version
async function loadBuildMetadata() {
  const buildPaths = ['build.json', '../build.json'];
  try {
    let build = null;
    for (const path of buildPaths) {
      const response = await fetch(path);
      if (response.ok) {
        build = await response.json();
        break;
      }
    }
    if (!build) {
      throw new Error('build.json not found');
    }
    
    // Update version displays
    const versionElements = document.querySelectorAll('[data-version]');
    versionElements.forEach(el => {
      el.textContent = build.build_metadata.version;
    });
    
    // Update status displays
    const statusElements = document.querySelectorAll('[data-status]');
    statusElements.forEach(el => {
      const key = el.dataset.status;
      const keys = key.split('.');
      let value = build;
      for (const k of keys) {
        value = value[k];
      }
      el.textContent = value !== undefined ? value : 'N/A';
    });
  } catch (error) {
    console.error('Failed to load build metadata:', error);
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadBuildMetadata);
} else {
  loadBuildMetadata();
}
