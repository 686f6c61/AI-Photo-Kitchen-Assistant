/**
 * Inicialización y configuración principal de la aplicación
 * Maneja la interacción con la interfaz de usuario, cámara y procesamiento de imágenes
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const uploadForm = document.querySelector('form');
    const loadingSpinner = document.getElementById('loading-spinner');
    const recipeContainer = document.getElementById('recipe-container');
    const ingredientsContainer = document.getElementById('ingredients-container');
    
    // Elementos de la cámara
    const cameraButton = document.getElementById('camera-button');
    const cameraModal = new bootstrap.Modal(document.getElementById('cameraModal'));
    const cameraPreview = document.getElementById('camera-preview');
    const captureButton = document.getElementById('capture-button');
    const cameraCanvas = document.getElementById('camera-canvas');
    
    let stream = null;

    // Configuración del contenedor de mensajes de carga
    const loadingMessages = document.createElement('div');
    loadingMessages.className = 'loading-container';
    loadingMessages.style.display = 'none';
    loadingMessages.innerHTML = `
        <div class="spinner"></div>
        <p id="current-status">Escaneando los ingredientes de la nevera...</p>
    `;
    document.body.appendChild(loadingMessages);

    // Mensajes de estado durante el procesamiento
    const messages = [
        "Escaneando los ingredientes de la nevera...",
        "Viendo qué receta deliciosa preparar...",
        "Preparando la receta...",
        "Preparando la lista de ingredientes..."
    ];

    // Inicialización de Bootstrap Tags Input para alergias e ingredientes principales
    $('#allergies, #main-ingredients').tagsinput({
        trimValue: true,
        confirmKeys: [13, 44] // Enter y coma
    });

    /**
     * Prevención de comportamientos por defecto para drag & drop
     */
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Gestión de efectos visuales para la zona de drop
     */
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight);
    });

    function highlight(e) {
        dropZone.classList.add('border-primary');
    }

    function unhighlight(e) {
        dropZone.classList.remove('border-primary');
    }

    /**
     * Sistema de notificaciones
     * @param {string} message - Mensaje a mostrar
     */
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }

    /**
     * Funcionalidad de la cámara
     */
    cameraButton.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
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

    // Detener la cámara al cerrar el modal
    document.getElementById('cameraModal').addEventListener('hidden.bs.modal', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    });

    /**
     * Captura de foto desde la cámara
     */
    captureButton.addEventListener('click', () => {
        const context = cameraCanvas.getContext('2d');
        cameraCanvas.width = cameraPreview.videoWidth;
        cameraCanvas.height = cameraPreview.videoHeight;
        
        context.scale(-1, 1); // Espejo de la imagen
        context.drawImage(cameraPreview, -cameraCanvas.width, 0, cameraCanvas.width, cameraCanvas.height);
        
        cameraCanvas.toBlob((blob) => {
            const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
            handleFiles([file]);
            cameraModal.hide();
        }, 'image/jpeg');
    });

    /**
     * Gestión de archivos y previsualización
     */
    dropZone.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        handleFiles(dt.files);
    }

    function handleFileSelect(e) {
        handleFiles(e.target.files);
    }

    function handleFiles(files) {
        previewContainer.innerHTML = '';
        Array.from(files).forEach(previewFile);
    }

    /**
     * Previsualización de imagen
     * @param {File} file - Archivo de imagen a previsualizar
     */
    function previewFile(file) {
        if (!file.type.startsWith('image/')) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'preview-wrapper';

        const img = document.createElement('img');
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => {
            img.src = reader.result;
            img.classList.add('preview-image');
        }

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-danger delete-preview';
        deleteBtn.innerHTML = '×';
        deleteBtn.onclick = () => wrapper.remove();

        wrapper.appendChild(img);
        wrapper.appendChild(deleteBtn);
        previewContainer.appendChild(wrapper);
    }

    /**
     * Sistema de copiado al portapapeles
     */
    document.addEventListener('click', function(e) {
        const copyButton = e.target.closest('.copy-button');
        const copyShoppingList = e.target.closest('.copy-shopping-list');
        
        if (!copyButton && !copyShoppingList) return;
        
        let textToCopy = '';
        let button = copyButton || copyShoppingList;
        
        if (copyButton) {
            const recipeCard = copyButton.closest('.recipe-card');
            const title = recipeCard.querySelector('.recipe-title').textContent;
            const content = recipeCard.querySelector('.recipe-content').textContent;
            const shoppingList = recipeCard.querySelector('.shopping-list')?.textContent || '';
            textToCopy = `${title}\n\n${content}\n\n${shoppingList}`;
        } else {
            const shoppingList = copyShoppingList.closest('.shopping-list');
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
    });

    /**
     * Manejo del formulario y envío de datos
     */
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            recipeContainer.innerHTML = '';
            ingredientsContainer.innerHTML = '';

            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
            }

            loadingMessages.style.display = 'block';
            
            // Secuencia de mensajes de carga
            for (let i = 0; i < messages.length; i++) {
                document.getElementById('current-status').textContent = messages[i];
                await new Promise(resolve => setTimeout(resolve, 2000));
            }

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (data.success) {
                    // Mostrar ingredientes detectados
                    const ingredientsHtml = `
                        <div class="ingredients-list">
                            <h3>Ingredientes Detectados</h3>
                            <ul>
                                ${data.ingredients.map(ingredient => 
                                    `<li>${ingredient}</li>`
                                ).join('')}
                            </ul>
                        </div>
                    `;
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
