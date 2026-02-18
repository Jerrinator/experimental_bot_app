/**
 * Client-Side Database Manager using IndexedDB
 * Replaces server-side SQLite for maximum privacy
 */

class ClientDatabase {
    constructor() {
        this.dbName = 'HEROChatbotDB';
        this.dbVersion = 1;
        this.db = null;
        this.username = null;
    }

    /**
     * Initialize the database for a specific user
     */
    async init(username) {
        this.username = username;
        
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => {
                console.error('Failed to open IndexedDB:', request.error);
                reject(request.error);
            };
            
            request.onsuccess = () => {
                this.db = request.result;
                console.log('IndexedDB initialized successfully for user:', username);
                resolve(this.db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create conversations table
                if (!db.objectStoreNames.contains('conversations')) {
                    const conversationsStore = db.createObjectStore('conversations', { 
                        keyPath: 'id', 
                        autoIncrement: true 
                    });
                    conversationsStore.createIndex('username', 'username', { unique: false });
                    conversationsStore.createIndex('session_id', 'session_id', { unique: false });
                    conversationsStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
                
                // Create documents table
                if (!db.objectStoreNames.contains('documents')) {
                    const documentsStore = db.createObjectStore('documents', { 
                        keyPath: 'id', 
                        autoIncrement: true 
                    });
                    documentsStore.createIndex('username', 'username', { unique: false });
                    documentsStore.createIndex('filename', 'filename', { unique: false });
                    documentsStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
                
                // Create sessions table
                if (!db.objectStoreNames.contains('sessions')) {
                    const sessionsStore = db.createObjectStore('sessions', { 
                        keyPath: 'session_id' 
                    });
                    sessionsStore.createIndex('username', 'username', { unique: false });
                    sessionsStore.createIndex('created_at', 'created_at', { unique: false });
                }
                
                console.log('IndexedDB schema created');
            };
        });
    }

    /**
     * Start a new session
     */
    async startSession(sessionId) {
        const transaction = this.db.transaction(['sessions'], 'readwrite');
        const store = transaction.objectStore('sessions');
        
        const sessionData = {
            session_id: sessionId,
            username: this.username,
            created_at: new Date().toISOString(),
            is_active: true
        };
        
        return new Promise((resolve, reject) => {
            const request = store.add(sessionData);
            
            request.onsuccess = () => {
                console.log('Session started:', sessionId);
                resolve(sessionData);
            };
            
            request.onerror = () => {
                console.error('Failed to start session:', request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Add a conversation to the database
     */
    async addConversation(userMessage, botResponse, sessionId, contextData = {}) {
        const transaction = this.db.transaction(['conversations'], 'readwrite');
        const store = transaction.objectStore('conversations');
        
        const conversationData = {
            username: this.username,
            session_id: sessionId,
            user_message: userMessage,
            bot_response: botResponse,
            timestamp: new Date().toISOString(),
            context_data: contextData
        };
        
        return new Promise((resolve, reject) => {
            const request = store.add(conversationData);
            
            request.onsuccess = () => {
                console.log('Conversation stored locally');
                resolve(conversationData);
            };
            
            request.onerror = () => {
                console.error('Failed to store conversation:', request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Get recent conversations for context injection
     */
    async getRecentConversations(limit = 10) {
        const transaction = this.db.transaction(['conversations'], 'readonly');
        const store = transaction.objectStore('conversations');
        const index = store.index('timestamp');
        
        return new Promise((resolve, reject) => {
            const conversations = [];
            const request = index.openCursor(null, 'prev'); // Reverse order (newest first)
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor && conversations.length < limit) {
                    const record = cursor.value;
                    if (record.username === this.username) {
                        conversations.push(record);
                    }
                    cursor.continue();
                } else {
                    console.log(`Retrieved ${conversations.length} recent conversations`);
                    resolve(conversations.reverse()); // Return in chronological order
                }
            };
            
            request.onerror = () => {
                console.error('Failed to retrieve conversations:', request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Store a document in the database
     */
    async storeDocument(filename, content, fileType) {
        const transaction = this.db.transaction(['documents'], 'readwrite');
        const store = transaction.objectStore('documents');
        
        const documentData = {
            username: this.username,
            filename: filename,
            content: content,
            file_type: fileType,
            timestamp: new Date().toISOString(),
            content_length: content.length
        };
        
        return new Promise((resolve, reject) => {
            const request = store.add(documentData);
            
            request.onsuccess = () => {
                console.log('Document stored locally:', filename);
                resolve(documentData);
            };
            
            request.onerror = () => {
                console.error('Failed to store document:', request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Get all documents for context injection
     */
    async getDocuments() {
        const transaction = this.db.transaction(['documents'], 'readonly');
        const store = transaction.objectStore('documents');
        const index = store.index('username');
        
        return new Promise((resolve, reject) => {
            const documents = [];
            const request = index.openCursor(IDBKeyRange.only(this.username));
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    documents.push(cursor.value);
                    cursor.continue();
                } else {
                    console.log(`Retrieved ${documents.length} documents`);
                    resolve(documents);
                }
            };
            
            request.onerror = () => {
                console.error('Failed to retrieve documents:', request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Search documents by content (simple text search)
     */
    async searchDocuments(query) {
        const documents = await this.getDocuments();
        const results = documents.filter(doc => 
            doc.content.toLowerCase().includes(query.toLowerCase()) ||
            doc.filename.toLowerCase().includes(query.toLowerCase())
        );
        
        console.log(`Document search for "${query}" found ${results.length} results`);
        return results;
    }

    /**
     * Build enhanced context for AI requests
     */
    async buildEnhancedContext(userMessage, basePrompt) {
        try {
            // Get recent conversations
            const conversations = await this.getRecentConversations(10);
            
            // Get all documents
            const documents = await this.getDocuments();
            
            // Build conversation context
            let conversationContext = '';
            if (conversations.length > 0) {
                conversationContext = '\n\n=== Recent Conversation History ===\n';
                conversations.forEach(conv => {
                    conversationContext += `User: ${conv.user_message}\nAssistant: ${conv.bot_response}\n\n`;
                });
            }
            
            // Build document context
            let documentContext = '';
            if (documents.length > 0) {
                documentContext = '\n\n=== Available Documents ===\n';
                documents.forEach(doc => {
                    documentContext += `Document: ${doc.filename}\nContent Preview: ${doc.content.substring(0, 200)}...\n\n`;
                });
            }
            
            // Combine all context
            const enhancedPrompt = basePrompt + conversationContext + documentContext;
            
            console.log(`Enhanced context built: ${enhancedPrompt.length} chars, ${conversations.length} conversations, ${documents.length} documents`);
            
            return {
                enhancedPrompt,
                conversationCount: conversations.length,
                documentCount: documents.length,
                totalLength: enhancedPrompt.length
            };
            
        } catch (error) {
            console.error('Failed to build enhanced context:', error);
            return {
                enhancedPrompt: basePrompt,
                conversationCount: 0,
                documentCount: 0,
                totalLength: basePrompt.length
            };
        }
    }

    /**
     * Get database statistics
     */
    async getStats() {
        try {
            const conversations = await this.getRecentConversations(1000); // Get more for stats
            const documents = await this.getDocuments();
            
            return {
                totalConversations: conversations.length,
                totalDocuments: documents.length,
                totalStorageUsed: conversations.reduce((sum, conv) => 
                    sum + conv.user_message.length + conv.bot_response.length, 0) +
                    documents.reduce((sum, doc) => sum + doc.content.length, 0),
                username: this.username
            };
        } catch (error) {
            console.error('Failed to get database stats:', error);
            return {
                totalConversations: 0,
                totalDocuments: 0,
                totalStorageUsed: 0,
                username: this.username
            };
        }
    }

    /**
     * Clear all data for the current user (privacy/reset)
     */
    async clearAllData() {
        try {
            const transaction = this.db.transaction(['conversations', 'documents', 'sessions'], 'readwrite');
            
            // Clear conversations
            const conversationsStore = transaction.objectStore('conversations');
            const conversationsIndex = conversationsStore.index('username');
            await this._clearStoreByUsername(conversationsIndex, conversationsStore);
            
            // Clear documents
            const documentsStore = transaction.objectStore('documents');
            const documentsIndex = documentsStore.index('username');
            await this._clearStoreByUsername(documentsIndex, documentsStore);
            
            // Clear sessions
            const sessionsStore = transaction.objectStore('sessions');
            const sessionsIndex = sessionsStore.index('username');
            await this._clearStoreByUsername(sessionsIndex, sessionsStore);
            
            console.log('All user data cleared from local database');
            return true;
        } catch (error) {
            console.error('Failed to clear user data:', error);
            return false;
        }
    }

    /**
     * Helper method to clear store by username
     */
    _clearStoreByUsername(index, store) {
        return new Promise((resolve, reject) => {
            const request = index.openCursor(IDBKeyRange.only(this.username));
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    cursor.delete();
                    cursor.continue();
                } else {
                    resolve();
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
}

// Export for use in other scripts
window.ClientDatabase = ClientDatabase;
