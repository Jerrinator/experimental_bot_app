class ChatApp {
    constructor() {
        this.socket = io();
        this.currentUser = null;
        this.sessionId = null;
        this.lastBotResponse = '';
        this.isRecording = false;
        this.mediaRecorder = null;
        
        this.loadConfig().then(() => {
            this.initializeElements();
            this.bindEvents();
            this.updateUI();
        });
    }

    async loadConfig() {
        try {
            const response = await fetch('/get_config');
            if (response.ok) {
                const config = await response.json();
                this.currentUser = config.user;
                this.authSystemUrl = config.authSystemUrl;
                console.log('User authenticated:', this.currentUser);
            } else {
                console.error('Failed to load config, redirecting to auth');
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Failed to load config:', error);
            window.location.href = '/';
        }
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-message');
        this.fileInput = document.getElementById('file-input');
        this.fileDropZone = document.getElementById('file-drop-zone');
        this.uploadedFiles = document.getElementById('uploaded-files');
        this.urlInput = document.getElementById('url-input');
        this.addUrlButton = document.getElementById('add-url-btn');
        this.addedUrls = document.getElementById('added-urls');
        this.voiceSelector = document.getElementById('voice-selector');
        this.playButton = document.getElementById('play-last-response');
        this.recordButton = document.getElementById('hold-to-record');
        this.exportPdfButton = document.getElementById('export-pdf');
        this.printButton = document.getElementById('print-chat');
        this.loading = document.getElementById('loading');
        this.usernameSpan = document.getElementById('username');
        this.logoutButton = document.getElementById('logout-btn');
        this.audioModeCheckbox = document.getElementById('audio-mode');

        // Clear UI state on page refresh to avoid retaining stale selections
        this.uploadedFiles.innerHTML = "";
        this.urlInput.value = "";
        this.addedUrls.innerHTML = "";
        this.fileInput.value = "";
        this.messageInput.value = "";
    }

    bindEvents() {
        // Socket events
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.createChatSession();
        });

        this.socket.on('connected', (data) => {
            console.log('Server confirmation:', data.status);
        });

        this.socket.on(
            "bot-response",
            (data) => {
                this.socket.emit("bot-response", data);
                this.addMessage(data.text, "bot", data.timestamp);
                this.lastBotResponse = data.text;
                this.playButton.disabled = false;
                this.hideLoading();
                this.autoPlayTTSIfEnabled(data.text);
            }
        );


        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.addMessage('Sorry, something went wrong. Please try again.', 'bot');
            this.hideLoading();
        });

        this.socket.on('pdf-ready', (data) => {
            console.log('PDF ready for download:', data);
            // Add notification message to chat
            this.addMessage(`📄 PDF export completed successfully!`, 'bot');
            // Add download button to chat
            this.addMessage(`<a href="${data.url}" class="btn btn-success btn-sm" download="${data.filename || 'chat-history.pdf'}"><i class="fas fa-download me-1"></i>Download PDF</a>`, 'bot');
            // Also trigger automatic download
            const link = document.createElement('a');
            link.href = data.url;
            link.download = data.filename || 'chat-history.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });

        // UI events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // File upload events
        this.fileDropZone.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));
        
        this.fileDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.fileDropZone.classList.add('dragover');
        });
        
        this.fileDropZone.addEventListener('dragleave', () => {
            this.fileDropZone.classList.remove('dragover');
        });
        
        this.fileDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.fileDropZone.classList.remove('dragover');
            this.handleFileUpload(e.dataTransfer.files);
        });

        // URL input events
        this.addUrlButton.addEventListener('click', () => this.handleUrlAdd());
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleUrlAdd();
            }
        });

        // Voice controls
        this.playButton.addEventListener('click', () => this.playLastResponse());
        
        // Recording events
        this.recordButton.addEventListener('mousedown', () => this.startRecording());
        this.recordButton.addEventListener('mouseup', () => this.stopRecording());
        this.recordButton.addEventListener('mouseleave', () => this.stopRecording());
        this.recordButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.recordButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        this.recordButton.addEventListener('touchcancel', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // Export events
        this.exportPdfButton.addEventListener('click', () => this.exportToPDF());
        this.printButton.addEventListener('click', () => this.printChat());
        
        // Auth events
        this.logoutButton.addEventListener('click', () => this.logout());
    }

    async createChatSession() {
        if (!this.currentUser) {
            console.error('No user data available');
            return;
        }

        // Ensure we listen for session-created before requesting session to avoid race conditions
        this.socket.on('session-created', (data) => {
            console.log('Session created:', data);
            this.sessionId = data.sessionId;
            // Enable export button only after session is established
            try { if (this.exportPdfButton) this.exportPdfButton.disabled = false; } catch (e) {}
            this.loadUserDocuments(); // Load existing documents after session is created
        });

        // Disable export until session is established to make the button responsive
        try { if (this.exportPdfButton) this.exportPdfButton.disabled = true; } catch (e) {}

        // Request a new session from the server
        this.socket.emit('create-session', { 
            userId: this.currentUser.id,
            username: this.currentUser.username 
        });
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        const timestamp = new Date();
        this.addMessage(message, 'user', timestamp);
        this.messageInput.value = '';
        this.showLoading();

        // Get user's timezone information
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const timeZoneOffset = timestamp.getTimezoneOffset(); // in minutes

        this.socket.emit(
            "user-message",
            {
                sessionId: this.sessionId,
                message: message,
                userId: this.currentUser.id,
                username: this.currentUser.username,
                timestamp: timestamp.toISOString(),
                currentTime: timestamp.toISOString(), // Add current time for LLM awareness
                timeZone: timeZone, // User's IANA timezone (e.g., 'America/New_York')
                timeZoneOffset: timeZoneOffset, // Offset in minutes from UTC
                localTimeString: timestamp.toLocaleString() // Formatted local time string
            }
        );

    }

    addMessage(content, type, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Only render markdown for bot responses, keep user messages as plain text
        if (type === 'bot') {
            // Configure marked with custom renderer for code blocks
            const renderer = new marked.Renderer();
            renderer.code = (code, language) => {
                const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
                const highlightedCode = hljs.highlight(code, { language: validLanguage }).value;
                return `<div class="code-block-container">
                    <div class="code-block-header">
                        <span class="code-language">${validLanguage}</span>
                        <button class="copy-code-btn" onclick="copyToClipboard(this)" data-code="${encodeURIComponent(code)}">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                    <pre><code class="hljs language-${validLanguage}">${highlightedCode}</code></pre>
                </div>`;
            };
            
            marked.setOptions({
                renderer: renderer,
                gfm: true,
                breaks: true,
                sanitize: false
            });
            
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        
        // Use provided timestamp or create new one
        const messageTime = timestamp ? new Date(timestamp) : new Date();
        
        // Format timestamp to show local date and time
        const options = {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        };
        
        timestampDiv.textContent = messageTime.toLocaleString(undefined, options);
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async handleFileUpload(files) {
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('userId', this.currentUser.id);

            try {
                this.showLoading();
                this.addMessage(`Starting upload of "${file.name}"...`, 'system');
                
                const response = await fetch('/api/files/upload', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.success && result.task_id) {
                        // Start polling for progress updates instead of showing immediate success
                        this.startProgressPolling(result.task_id, file.name);
                        this.addMessage(result.message, 'system');
                    } else {
                        this.hideLoading();
                        this.addMessage(`Failed to upload file "${file.name}": ${result.error || 'Unknown error'}`, 'bot');
                    }
                } else {
                    this.hideLoading();
                    this.addMessage(`Failed to upload file "${file.name}".`, 'bot');
                }
            } catch (error) {
                console.error('File upload error:', error);
                this.hideLoading();
                this.addMessage(`Error uploading file "${file.name}".`, 'bot');
            }
        }
    }

    startProgressPolling(taskId, filename) {
        console.log('Starting progress monitoring for task:', taskId, 'file:', filename);
        
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/progress/${taskId}`);
                const data = await response.json();
                
                if (response.ok) {
                    console.log('Progress data received:', data);
                    
                    // Update progress display
                    this.updateProgressMessage(data.message, data.progress);
                    
                    // Check if processing is complete
                    console.log('Checking completion: progress =', data.progress, 'completed =', data.completed);
                    if (data.progress === 100 && data.completed) {
                        console.log('Processing complete detected, showing notification');
                        clearInterval(pollInterval);
                        this.hideLoading();
                        
                        // Use the filename from the progress data (secure_filename version)
                        const processedFilename = data.filename || filename;
                        
                        // Refresh the document list from server to ensure UI is in sync
                        await this.loadUserDocuments();
                        
                        // Now show success message
                        this.addMessage(`✅ File "${processedFilename}" processed successfully and loaded into chatbot context! You can now ask questions about this document.`, 'bot');
                        
                        // Add download button in chat if download info is available
                        if (data.download_id && data.download_filename) {
                            const downloadUrl = `/download/${data.download_id}`;
                            this.addMessage(`<a href="${downloadUrl}" class="btn btn-success btn-sm" download="${data.download_filename}"><i class="fas fa-download"></i> Download Scraped PDF</a>`, 'bot');
                        }
                        
                        // Show notification similar to OCR PDF app
                        this.showProcessingCompleteNotification(processedFilename, data.download_id, data.download_filename);
                        
                    } else if (data.progress === -1) {
                        // Error occurred
                        clearInterval(pollInterval);
                        this.hideLoading();
                        this.addMessage(`❌ Processing failed for "${filename}": ${data.message || 'Unknown error'}`, 'bot');
                    }
                } else {
                    console.error('Progress endpoint error:', data);
                }
            } catch (error) {
                console.error('Error in polling:', error);
                clearInterval(pollInterval);
                this.hideLoading();
                this.addMessage(`Connection lost while processing "${filename}". Please refresh and try again.`, 'bot');
            }
        }, 2000); // Poll every 2 seconds for responsive updates
        
        // Clean up polling if user navigates away
        window.addEventListener('beforeunload', () => clearInterval(pollInterval));
    }

    updateProgressMessage(message, progress) {
        // Update the last system message with progress info
        const messages = this.chatMessages.querySelectorAll('.message.system');
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            const contentDiv = lastMessage.querySelector('.message-content');
            if (contentDiv && progress >= 0) {
                contentDiv.textContent = `${message} (${progress}%)`;
            }
        }
    }

    showProcessingCompleteNotification(filename, downloadId, downloadFilename) {
        // Create a temporary notification similar to OCR PDF app
        const notification = document.createElement('div');
        notification.className = 'processing-complete-notification';
        
        // Only show download link if we have download info
        let downloadButton = '';
        if (downloadId && downloadFilename) {
            const downloadUrl = `/download/${downloadId}`;
            downloadButton = `
                <a href="${downloadUrl}" class="btn btn-success btn-sm" download="${downloadFilename}">
                    <i class="fas fa-download"></i> Download Scraped PDF
                </a>
            `;
        }
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <i class="fas fa-check-circle" style="color: #28a745;"></i>
                    <strong>Document Processing Complete!</strong>
                </div>
                <div class="notification-body">
                    "${filename}" has been successfully processed and added to the chatbot context.
                </div>
                <div class="notification-actions">
                    ${downloadButton}
                    <button class="btn btn-secondary btn-sm" onclick="this.closest('.processing-complete-notification').remove()">
                        <i class="fas fa-times"></i> Dismiss
                    </button>
                </div>
            </div>
        `;
        
        // Add to DOM and auto-remove after 10 seconds
        document.body.appendChild(notification);
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    displayUploadedFile(filename) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.dataset.filename = filename;
        
        const fileName = document.createElement('span');
        fileName.className = 'file-item-name';
        fileName.textContent = filename;
        fileName.title = filename; // Show full name on hover
        
        const removeButton = document.createElement('button');
        removeButton.className = 'file-item-remove';
        removeButton.innerHTML = '<i class="fas fa-times"></i>';
        removeButton.title = 'Remove document';
        removeButton.onclick = (e) => {
            e.stopPropagation();
            this.removeUploadedFile(filename, fileItem);
        };
        
        fileItem.appendChild(fileName);
        fileItem.appendChild(removeButton);
        
        // Add click handler for selection
        fileItem.onclick = (e) => {
            e.stopPropagation(); // Prevent triggering file drop zone click
            this.toggleFileSelection(fileItem);
        };
        
        this.uploadedFiles.appendChild(fileItem);
    }

    toggleFileSelection(fileItem) {
        // Remove selection from all other files
        const allFileItems = this.uploadedFiles.querySelectorAll('.file-item');
        allFileItems.forEach(item => {
            if (item !== fileItem) {
                item.classList.remove('selected');
            }
        });
        
        // Toggle selection on clicked file
        fileItem.classList.toggle('selected');
    }

    async removeUploadedFile(filename, fileItem) {
        try {
            console.log('Removing document:', filename);
            const response = await fetch('/api/remove-document', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: filename })
            });

            if (response.ok) {
                // Remove from UI
                fileItem.remove();
                console.log(`Document ${filename} removed successfully`);
            } else {
                const error = await response.json();
                console.error('Failed to remove document:', error.error);
                alert('Failed to remove document: ' + (error.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error removing document:', error);
            alert('Error removing document. Please try again.');
        }
    }

    removeSelectedDocument() {
        const selectedFile = this.uploadedFiles.querySelector('.file-item.selected');
        if (!selectedFile) {
            alert('Please select a document to remove.');
            return;
        }
        
        const filename = selectedFile.dataset.filename;
        console.log('Attempting to remove selected document:', filename);
        if (confirm(`Are you sure you want to remove "${filename}"?`)) {
            this.removeUploadedFile(filename, selectedFile);
        }
    }

    async handleUrlAdd() {
        const url = this.urlInput.value.trim();
        if (!url) {
            alert('Please enter a valid URL');
            return;
        }

        // Basic URL validation
        try {
            new URL(url);
        } catch (error) {
            alert('Please enter a valid URL (e.g., https://example.com)');
            return;
        }

        // Send URL to web scraper
        try {
            this.showLoading();
            this.addMessage(`Starting web scraping of "${url}"...`, 'system');
            
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    userId: this.currentUser.id 
                })
            });

            if (response.ok) {
                const result = await response.json();
                if (result.success && result.task_id) {
                    // Start polling for progress updates similar to file upload
                    this.startProgressPolling(result.task_id, url);
                    this.addMessage(result.message, 'system');
                } else {
                    this.hideLoading();
                    this.addMessage(`Failed to scrape URL "${url}": ${result.error || 'Unknown error'}`, 'bot');
                }
            } else {
                this.hideLoading();
                this.addMessage(`Failed to scrape URL "${url}".`, 'bot');
            }
        } catch (error) {
            console.error('URL scraping error:', error);
            this.hideLoading();
            this.addMessage(`Error scraping URL "${url}".`, 'bot');
        }

        this.urlInput.value = ''; // Clear the input
    }

    displayAddedUrl(url) {
        const urlItem = document.createElement('div');
        urlItem.className = 'file-item';
        urlItem.dataset.url = url;
        
        const urlName = document.createElement('span');
        urlName.className = 'file-item-name';
        urlName.textContent = url;
        urlName.title = url; // Show full URL on hover
        
        const removeButton = document.createElement('button');
        removeButton.className = 'file-item-remove';
        removeButton.innerHTML = '<i class="fas fa-times"></i>';
        removeButton.title = 'Remove URL';
        removeButton.onclick = (e) => {
            e.stopPropagation();
            this.removeAddedUrl(url, urlItem);
        };
        
        urlItem.appendChild(urlName);
        urlItem.appendChild(removeButton);
        
        // Add click handler for selection
        urlItem.onclick = (e) => {
            e.stopPropagation();
            this.toggleUrlSelection(urlItem);
        };
        
        this.addedUrls.appendChild(urlItem);
    }

    toggleUrlSelection(urlItem) {
        // Remove selection from all other URLs
        const allUrlItems = this.addedUrls.querySelectorAll('.file-item');
        allUrlItems.forEach(item => {
            if (item !== urlItem) {
                item.classList.remove('selected');
            }
        });
        
        // Toggle selection on clicked URL
        urlItem.classList.toggle('selected');
    }

    removeAddedUrl(url, urlItem) {
        urlItem.remove();
        console.log(`URL ${url} removed from list`);
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            // Choose a supported MIME type for MediaRecorder to maximize compatibility
            let selectedMime = '';
            const candidates = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/webm', 'audio/ogg'];
            for (const c of candidates) {
                if (MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(c)) {
                    selectedMime = c;
                    break;
                }
            }

            try {
                this.mediaRecorder = selectedMime ? new MediaRecorder(stream, { mimeType: selectedMime }) : new MediaRecorder(stream);
            } catch (mrErr) {
                console.warn('Failed to create MediaRecorder with selected mimeType, falling back to default:', mrErr);
                this.mediaRecorder = new MediaRecorder(stream);
            }
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordButton.classList.add('recording');
            this.recordButton.textContent = '🎤 Recording...';
        } catch (error) {
            console.error('Recording failed:', error);
            this.addMessage('Microphone access denied or not available.', 'bot');
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            try {
                this.mediaRecorder.stop();
            } catch (err) {
                console.warn('Error stopping mediaRecorder:', err);
            }
        } else {
            console.warn('mediaRecorder is not available or already stopped');
        }
        this.isRecording = false;
        this.recordButton.classList.remove('recording');
        this.recordButton.textContent = '🎤 Hold to Record';
        
        // Stop all tracks
        try {
            if (this.mediaRecorder && this.mediaRecorder.stream) {
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        } catch (err) {
            console.warn('Error stopping media tracks:', err);
        }
    }

    async processRecording() {
        // Use the same mimeType as the MediaRecorder when creating the Blob
        const blobType = (this.mediaRecorder && this.mediaRecorder.mimeType) ? this.mediaRecorder.mimeType : 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: blobType });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('userId', this.currentUser.id);

        let dispatchedToLLM = false;

        try {
            this.showLoading();
            const response = await fetch('/api/audio/transcribe', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                const transcribedText = (result && result.text) ? String(result.text).trim() : '';
                
                if (transcribedText) {
                    // Reuse the existing send flow so voice input matches manual submissions
                    this.messageInput.value = transcribedText;
                    dispatchedToLLM = true;
                    this.sendMessage();
                } else {
                    this.addMessage('No speech detected in the recording.', 'bot');
                }
            } else {
                // Log response body for debugging transcription failures
                let bodyText = '';
                try { bodyText = await response.text(); } catch (e) { bodyText = '<unreadable>'; }
                console.error('Transcription endpoint returned error:', response.status, bodyText);
                this.addMessage('Failed to transcribe audio.', 'bot');
            }
        } catch (error) {
            console.error('Transcription error:', error);
            this.addMessage('Error processing voice input.', 'bot');
        } finally {
            // Only hide the loading indicator when nothing was forwarded to the LLM
            if (!dispatchedToLLM) {
                this.hideLoading();
            }
        }
    }

    async playLastResponse() {
        if (!this.lastBotResponse || !this.voiceSelector.value) {
            this.addMessage('Please select a voice and have a bot response to play.', 'bot');
            return;
        }

        try {
            this.showLoading();
            
            // Create FormData for TTS request (matching knowledgeninja format)
            const formData = new FormData();
            formData.append('text', this.lastBotResponse);
            formData.append('voice', this.voiceSelector.value);
            
            const response = await fetch('/api/tts', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play();
            } else {
                this.addMessage('Failed to generate speech.', 'bot');
            }
        } catch (error) {
            console.error('TTS error:', error);
            this.addMessage('Error generating speech.', 'bot');
        } finally {
            this.hideLoading();
        }
    }

    async autoPlayTTSIfEnabled(message) {
        // Check if audioMode is enabled and voice is selected
        if (!this.audioModeCheckbox.checked || !this.voiceSelector.value) {
            console.log('Auto TTS skipped: audioMode disabled or no voice selected');
            return;
        }

        try {
            console.log('Auto-playing TTS for message:', message);
            
            // Create FormData for TTS request
            const formData = new FormData();
            formData.append('text', message);
            formData.append('voice', this.voiceSelector.value);
            
            const response = await fetch('/api/tts', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play();
                console.log('Auto TTS playback started');
            } else {
                console.error('Auto TTS failed:', response.status);
            }
        } catch (error) {
            console.error('Auto TTS error:', error);
        }
    }

    exportToPDF() {
        console.log('Exporting PDF for session:', this.sessionId);
        if (!this.sessionId) {
            console.error('No session ID available for PDF export');
            alert('Cannot export PDF: No active session');
            return;
        }
        this.socket.emit('export-pdf', { sessionId: this.sessionId });
    }

    printChat() {
        const printWindow = window.open('', '_blank');
        const chatContent = this.chatMessages.innerHTML;
        
        printWindow.document.write(`
            <html>
                <head>
                    <title>Chat History</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                        .message.user { background-color: #e3f2fd; margin-left: 20%; }
                        .message.bot { background-color: #f5f5f5; margin-right: 20%; }
                        .message-timestamp { font-size: 0.8em; opacity: 0.7; }
                    </style>
                </head>
                <body>
                    <h1>Chat History</h1>
                    <div>${chatContent}</div>
                </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.print();
    }

    showLoading() {
        this.loading.style.display = 'flex';
    }

    hideLoading() {
        this.loading.style.display = 'none';
    }

    async loadUserDocuments() {
        try {
            const response = await fetch('/api/user-documents', {
                method: 'GET',
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.documents) {
                    // Clear existing documents in UI first
                    this.uploadedFiles.innerHTML = '';
                    
                    // Display each document
                    data.documents.forEach(filename => {
                        this.displayUploadedFile(filename);
                    });
                    
                    console.log(`Loaded ${data.count} existing documents`);
                }
            } else {
                console.log('No existing documents found or failed to load');
            }
        } catch (error) {
            console.error('Error loading user documents:', error);
        }
    }

    updateUI() {
        if (this.currentUser && this.usernameSpan) {
            this.usernameSpan.textContent = this.currentUser.username || this.currentUser.email || 'User';
        }
        this.populateVoices();
    }

    populateVoices() {
        // OpenAI TTS voices
        const voices = [
            { id: 'alloy', name: 'Alloy' },
            { id: 'echo', name: 'Echo' },
            { id: 'fable', name: 'Fable' },
            { id: 'onyx', name: 'Onyx' },
            { id: 'nova', name: 'Nova' },
            { id: 'shimmer', name: 'Shimmer' }
        ];

        // Clear existing options
        while (this.voiceSelector.children.length > 0) {
            this.voiceSelector.removeChild(this.voiceSelector.lastChild);
        }

        // Add voice options
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            this.voiceSelector.appendChild(option);
        });

        // Set alloy as default
        this.voiceSelector.value = 'alloy';
    }

    logout() {
        localStorage.removeItem('authToken');
        window.close();
    }

    redirectToLogin() {
        const currentUrl = encodeURIComponent(window.location.href);
        window.location.href = `${this.authSystemUrl}/login?redirect=${currentUrl}`;
    }
}

// Global function for copying code to clipboard
function copyToClipboard(button) {
    const code = decodeURIComponent(button.getAttribute('data-code'));
    navigator.clipboard.writeText(code).then(() => {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        button.classList.add('copied');
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code: ', err);
        button.innerHTML = '<i class="fas fa-exclamation"></i> Failed';
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-copy"></i> Copy';
        }, 2000);
    });
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
