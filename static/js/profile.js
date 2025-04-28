/**
 * profile.js - Manages profile form interactions and validation
 */
document.addEventListener('DOMContentLoaded', function() {
    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // CPF validation and formatting
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value;
            
            // Remove all non-digits
            value = value.replace(/\D/g, '');
            
            // Format as XXX.XXX.XXX-XX
            if (value.length > 9) {
                value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{0,2}).*/, '$1.$2.$3-$4');
            } else if (value.length > 6) {
                value = value.replace(/^(\d{3})(\d{3})(\d{0,3}).*/, '$1.$2.$3');
            } else if (value.length > 3) {
                value = value.replace(/^(\d{3})(\d{0,3}).*/, '$1.$2');
            }
            
            e.target.value = value;
        });
        
        cpfInput.addEventListener('blur', function(e) {
            const value = e.target.value.replace(/\D/g, '');
            
            if (value.length !== 11) {
                cpfInput.setCustomValidity('CPF must contain 11 digits');
            } else if (!validateCPF(value)) {
                cpfInput.setCustomValidity('Invalid CPF number');
            } else {
                cpfInput.setCustomValidity('');
            }
        });
    }

    // Document upload preview
    const documentFileInput = document.getElementById('document_file');
    const documentPreview = document.getElementById('documentPreview');
    
    if (documentFileInput && documentPreview) {
        documentFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Check if it's an image file
                if (file.type.match('image.*')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        documentPreview.innerHTML = `
                            <div class="card mb-3">
                                <img src="${e.target.result}" class="card-img-top document-preview-img" alt="Document Preview">
                                <div class="card-body">
                                    <p class="card-text">
                                        <small class="text-muted">File: ${file.name} (${formatFileSize(file.size)})</small>
                                    </p>
                                </div>
                            </div>
                        `;
                    };
                    
                    reader.readAsDataURL(file);
                } else if (file.type === 'application/pdf') {
                    documentPreview.innerHTML = `
                        <div class="card mb-3">
                            <div class="card-body text-center">
                                <i class="far fa-file-pdf fa-5x text-danger mb-3"></i>
                                <p class="card-text">PDF Document</p>
                                <p class="card-text">
                                    <small class="text-muted">File: ${file.name} (${formatFileSize(file.size)})</small>
                                </p>
                            </div>
                        </div>
                    `;
                } else {
                    documentPreview.innerHTML = `
                        <div class="alert alert-warning">
                            Unsupported file type. Please upload an image or PDF document.
                        </div>
                    `;
                }
            }
        });
    }

    // Interest tags input enhancement
    document.querySelectorAll('.tag-input').forEach(input => {
        const tagsContainer = document.createElement('div');
        tagsContainer.className = 'tags-container d-flex flex-wrap gap-2 mb-2';
        input.parentNode.insertBefore(tagsContainer, input);
        
        // Convert existing value to tags
        const existingValue = input.value;
        if (existingValue) {
            const tags = existingValue.split(',').map(tag => tag.trim()).filter(tag => tag);
            tags.forEach(tagText => {
                addTag(tagText, tagsContainer, input);
            });
        }
        
        // Add tag when pressing Enter or comma
        input.addEventListener('keydown', function(e) {
            if ((e.key === 'Enter' || e.key === ',') && this.value.trim()) {
                e.preventDefault();
                
                const tagText = this.value.trim().replace(/,/g, '');
                if (tagText) {
                    addTag(tagText, tagsContainer, this);
                    this.value = '';
                    updateHiddenInput(tagsContainer, this);
                }
            }
        });
        
        // Allow removing tags by clicking
        tagsContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-tag') || e.target.parentElement.classList.contains('remove-tag')) {
                const tagElement = e.target.closest('.tag');
                if (tagElement) {
                    tagElement.remove();
                    updateHiddenInput(tagsContainer, input);
                }
            }
        });
    });

    // Profile completeness indicator
    const completenessProgressBar = document.getElementById('completenessProgress');
    if (completenessProgressBar) {
        const stages = document.querySelectorAll('.profile-stage');
        const completedStages = document.querySelectorAll('.profile-stage.completed');
        
        const completionPercentage = (completedStages.length / stages.length) * 100;
        completenessProgressBar.style.width = `${completionPercentage}%`;
        completenessProgressBar.setAttribute('aria-valuenow', completionPercentage);
        
        if (completionPercentage < 30) {
            completenessProgressBar.classList.add('bg-danger');
        } else if (completionPercentage < 70) {
            completenessProgressBar.classList.add('bg-warning');
        } else {
            completenessProgressBar.classList.add('bg-success');
        }
    }
});

// Helper function to validate CPF
function validateCPF(cpf) {
    // CPF validation logic
    cpf = cpf.replace(/[^\d]/g, '');
    
    // Check if all digits are the same
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validate first verification digit
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;
    
    // Validate second verification digit
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    return remainder === parseInt(cpf.charAt(10));
}

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Helper function to add tags
function addTag(tagText, container, input) {
    const tag = document.createElement('span');
    tag.className = 'tag badge bg-secondary me-2 mb-2';
    tag.innerHTML = `
        ${tagText}
        <button type="button" class="remove-tag btn-close btn-close-white ms-2" aria-label="Remove"></button>
    `;
    container.appendChild(tag);
    
    // Update the hidden input value
    updateHiddenInput(container, input);
}

// Helper function to update hidden input
function updateHiddenInput(container, input) {
    const tags = Array.from(container.querySelectorAll('.tag'))
        .map(tag => tag.textContent.trim())
        .join(',');
    
    input.value = tags;
}
