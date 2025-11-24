/**
 * AI Kitchen Assistant - Frontend JavaScript
 * 
 * This file contains all the client-side functionality for the AI Kitchen Assistant,
 * including image upload, preview, and interaction with the backend API.
 * 
 * Key Features:
 * - Drag and drop image upload
 * - Camera capture support
 * - Image preview with removal option
 * - Form validation
 * - API communication with loading states
 * - Error handling and user feedback
 * 
 * Dependencies:
 * - Bootstrap 5 (for modal and UI components)
 * - Bootstrap Icons (for UI icons)
 */

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const uploadForm = document.querySelector('form');
const loadingSpinner = document.getElementById('loading-spinner');
const recipeContainer = document.getElementById('recipe-container');
const ingredientsContainer = document.getElementById('ingredients-container');
const cameraButton = document.getElementById('camera-button');
const cameraModal = new bootstrap.Modal(document.getElementById('cameraModal'));
const cameraPreview = document.getElementById('camera-preview');
const captureButton = document.getElementById('capture-button');
const cameraCanvas = document.getElementById('camera-canvas');

/**
 * Application state
 * @type {Object}
 * @property {File|null} currentFile - The currently selected image file
 * @property {boolean} isLoading - Whether an operation is in progress
 */
const appState = {
    currentFile: null,
    isLoading: false,
    currentStream: null // To hold the camera stream
};

// Initialize event listeners for the application
function initializeEventListeners() {
    // File selection handling
    fileInput.addEventListener('change', handleFileSelect);
    
    // Button event listeners
    cameraButton.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' },
                audio: false
            });
            cameraPreview.srcObject = stream;
            cameraModal.show();
        } catch (err) {
            console.error('Error accessing camera:', err);
            showNotification('No se pudo acceder a la cámara. Por favor, verifica los permisos.');
        }
    });

    // Drag and drop event listeners
    const dragEvents = ['dragenter', 'dragover', 'dragleave', 'drop'];
    dragEvents.forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    // Remove highlight when leaving or dropping
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle file drop
    dropZone.addEventListener('drop', handleDrop, false);
}

// Initialize the application
initializeEventListeners();

// Prevent default behavior for drag and drop events
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight the drop zone
function highlight(e) {
    dropZone.classList.add('border-primary');
}

// Unhighlight the drop zone
function unhighlight(e) {
    dropZone.classList.remove('border-primary');
}

// Handle file selection from file input
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.match('image.*')) {
            showError('Please upload a valid image file (JPEG, PNG)');
            return;
        }
        
        // Update application state
        appState.currentFile = file;
        
        // Display image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewImage = document.createElement('img');
            previewImage.src = e.target.result;
            previewContainer.innerHTML = '';
            previewContainer.appendChild(previewImage);
        };
        reader.readAsDataURL(file);
    }
}

// Handle files dropped onto the upload area
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
        fileInput.files = files;
        handleFileSelect({ target: fileInput });
    }
}

// Handle camera capture
captureButton.addEventListener('click', () => {
    const context = cameraCanvas.getContext('2d');
    cameraCanvas.width = cameraPreview.videoWidth;
    cameraCanvas.height = cameraPreview.videoHeight;
    
    context.scale(-1, 1); // Espejo de la imagen
    context.drawImage(cameraPreview, -cameraCanvas.width, 0, cameraCanvas.width, cameraCanvas.height);
    
    cameraCanvas.toBlob((blob) => {
        const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
        handleFileSelect({ target: { files: [file] } });
        cameraModal.hide();
    }, 'image/jpeg');
});

// Detener la cámara al cerrar el modal
document.getElementById('cameraModal').addEventListener('hidden.bs.modal', () => {
    if (cameraPreview.srcObject) {
        cameraPreview.srcObject.getTracks().forEach(track => track.stop());
        cameraPreview.srcObject = null;
    }
});

// Handle form submission
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    recipeContainer.innerHTML = '';
    ingredientsContainer.innerHTML = '';

    const submitButton = this.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
    }

    loadingSpinner.style.display = 'block';
    
    // Secuencia de mensajes de carga
    const messages = [
        "Escaneando los ingredientes de la nevera...",
        "Viendo qué receta deliciosa preparar...",
        "Preparando la receta...",
        "Preparando la lista de ingredientes..."
    ];
    for (let i = 0; i < messages.length; i++) {
        document.getElementById('current-status').textContent = messages[i];
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
                    ingredientsContainer.innerHTML = ingredientsHtml;

                    // Mostrar recetas generadas
                    const recipesHtml = data.recipes.map((recipe) => `
                        <div class="recipe-card">
                            ${recipe}
                        </div>
                    `).join('');
                    recipeContainer.innerHTML = recipesHtml;
                } else {
                    showNotification('Error al generar la receta. Por favor, intenta de nuevo.');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Error de conexión. Por favor, verifica tu conexión a internet.');
            } finally {
                loadingMessages.style.display = 'none';
                if (submitButton) {
                    submitButton.disabled = false;
                }
            }
        });
    } else {
        console.error('No se encontró el formulario en el DOM');
    }

    /**
     * Manejo de eventos de copiado
     * @param {Event} e - Evento del click
     */
    function handleCopy(e) {
        const target = e.target.closest('.copy-button, .copy-shopping-list');
        if (!target) return;

        let textToCopy = '';
        let button = target;

        if (target.classList.contains('copy-button')) {
            // Copiar receta completa
            const recipeCard = target.closest('.recipe-card');
            const title = recipeCard.querySelector('.recipe-title')?.textContent || '';
            const content = recipeCard.querySelector('.recipe-content')?.textContent || '';
            const shoppingList = recipeCard.querySelector('.shopping-list')?.textContent || '';
            textToCopy = `${title}\n\n${content}\n\n${shoppingList}`;
        } else if (target.classList.contains('copy-shopping-list')) {
            // Copiar solo lista de compras
            const shoppingList = target.closest('.shopping-list');
            const items = Array.from(shoppingList.querySelectorAll('.shopping-list-item span'))
                .map(span => span.textContent.trim())
                .join('\n');
            textToCopy = `Lista de Compra Sugerida:\n\n${items}`;
        }

        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                const originalHTML = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i>';
                showNotification('¡Copiado al portapapeles!');
                setTimeout(() => {
                    button.innerHTML = originalHTML;
                }, 2000);
            })
            .catch(err => {
                console.error('Error al copiar:', err);
                showNotification('Error al copiar. Por favor, inténtalo manualmente.');
            });
    }

    // Delegación de eventos para el copiado
    document.addEventListener('click', handleCopy);
});
