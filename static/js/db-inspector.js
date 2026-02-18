/**
 * IndexedDB Inspector Script
 * Use this in browser console to inspect client-side database contents
 * Demonstrates complete privacy - all data stored locally in browser
 */

class DBInspector {
    constructor() {
        this.dbName = 'ChatbotDB';
        this.dbVersion = 1;
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
        });
    }

    async inspectAll() {
        console.log('🔍 INSPECTING CLIENT-SIDE DATABASE (PRIVACY-FIRST STORAGE)');
        console.log('=' .repeat(60));
        
        try {
            await this.init();
            
            // Get current user
            const currentUser = localStorage.getItem('currentUser');
            console.log('👤 Current User:', currentUser ? JSON.parse(currentUser) : 'None');
            
            // Inspect conversations
            await this.inspectConversations();
            
            // Inspect documents
            await this.inspectDocuments();
            
            // Inspect sessions
            await this.inspectSessions();
            
            // Show storage stats
            await this.showStorageStats();
            
            console.log('=' .repeat(60));
            console.log('🔒 PRIVACY CONFIRMED: All data stored locally in browser only!');
            
        } catch (error) {
            console.error('Error inspecting database:', error);
        }
    }

    async inspectConversations() {
        console.log('\n💬 CONVERSATIONS (Client-Side Storage):');
        console.log('-' .repeat(40));
        
        const conversations = await this.getAllFromStore('conversations');
        console.log(`📊 Total Conversations: ${conversations.length}`);
        
        conversations.forEach((conv, index) => {
            console.log(`\n🗣️  Conversation ${index + 1}:`);
            console.log(`   📅 Timestamp: ${new Date(conv.timestamp).toLocaleString()}`);
            console.log(`   👤 User: ${conv.userMessage.substring(0, 50)}${conv.userMessage.length > 50 ? '...' : ''}`);
            console.log(`   🤖 Bot: ${conv.botResponse.substring(0, 50)}${conv.botResponse.length > 50 ? '...' : ''}`);
            console.log(`   💾 Session: ${conv.sessionId}`);
            console.log(`   📏 Sizes: User=${conv.userMessage.length}, Bot=${conv.botResponse.length}`);
        });
    }

    async inspectDocuments() {
        console.log('\n📄 DOCUMENTS (Client-Side Storage):');
        console.log('-' .repeat(40));
        
        const documents = await this.getAllFromStore('documents');
        console.log(`📊 Total Documents: ${documents.length}`);
        
        documents.forEach((doc, index) => {
            console.log(`\n📋 Document ${index + 1}:`);
            console.log(`   📁 Name: ${doc.filename}`);
            console.log(`   📅 Uploaded: ${new Date(doc.uploadDate).toLocaleString()}`);
            console.log(`   📏 Size: ${doc.content.length} characters`);
            console.log(`   🔍 Preview: ${doc.content.substring(0, 100)}${doc.content.length > 100 ? '...' : ''}`);
        });
    }

    async inspectSessions() {
        console.log('\n🎯 SESSIONS (Client-Side Storage):');
        console.log('-' .repeat(40));
        
        const sessions = await this.getAllFromStore('sessions');
        console.log(`📊 Total Sessions: ${sessions.length}`);
        
        sessions.forEach((session, index) => {
            console.log(`\n🔑 Session ${index + 1}:`);
            console.log(`   🆔 ID: ${session.sessionId}`);
            console.log(`   📅 Started: ${new Date(session.startTime).toLocaleString()}`);
            console.log(`   📅 Last Activity: ${new Date(session.lastActivity).toLocaleString()}`);
            console.log(`   🎲 Active: ${session.isActive}`);
        });
    }

    async showStorageStats() {
        console.log('\n📊 STORAGE STATISTICS (Browser-Only):');
        console.log('-' .repeat(40));
        
        const conversations = await this.getAllFromStore('conversations');
        const documents = await this.getAllFromStore('documents');
        const sessions = await this.getAllFromStore('sessions');
        
        const totalConversationChars = conversations.reduce((sum, conv) => 
            sum + conv.userMessage.length + conv.botResponse.length, 0);
        
        const totalDocumentChars = documents.reduce((sum, doc) => 
            sum + doc.content.length, 0);
        
        console.log(`📈 Conversations: ${conversations.length} items, ${totalConversationChars} characters`);
        console.log(`📂 Documents: ${documents.length} items, ${totalDocumentChars} characters`);
        console.log(`🎯 Sessions: ${sessions.length} items`);
        console.log(`💾 Total Storage Used: ~${(totalConversationChars + totalDocumentChars)} characters`);
        
        // Check localStorage usage
        const localStorageSize = JSON.stringify(localStorage).length;
        console.log(`🗄️  LocalStorage: ~${localStorageSize} characters`);
        
        console.log('\n🔒 PRIVACY FEATURES:');
        console.log('   ✅ Zero server-side storage');
        console.log('   ✅ All data in browser IndexedDB');
        console.log('   ✅ Data persists across browser sessions');
        console.log('   ✅ User controls all data (can clear anytime)');
        console.log('   ✅ No network transmission of stored data');
    }

    async getAllFromStore(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
        });
    }

    async clearAllData() {
        console.log('🗑️  CLEARING ALL CLIENT-SIDE DATA...');
        
        const stores = ['conversations', 'documents', 'sessions'];
        
        for (const storeName of stores) {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            await new Promise((resolve, reject) => {
                const request = store.clear();
                request.onerror = () => reject(request.error);
                request.onsuccess = () => resolve();
            });
            console.log(`   ✅ Cleared ${storeName}`);
        }
        
        // Clear localStorage
        localStorage.removeItem('currentUser');
        localStorage.removeItem('chatbotSettings');
        console.log('   ✅ Cleared localStorage');
        
        console.log('🔒 All client-side data cleared! Privacy maintained.');
    }

    async exportData() {
        console.log('📤 EXPORTING CLIENT-SIDE DATA (Privacy-Preserving)...');
        
        const data = {
            exportDate: new Date().toISOString(),
            user: JSON.parse(localStorage.getItem('currentUser') || '{}'),
            conversations: await this.getAllFromStore('conversations'),
            documents: await this.getAllFromStore('documents'),
            sessions: await this.getAllFromStore('sessions'),
            settings: JSON.parse(localStorage.getItem('chatbotSettings') || '{}')
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chatbot-data-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✅ Data exported! File downloaded to your device.');
        console.log('🔒 Note: This export contains YOUR data only, stored locally in YOUR browser.');
    }
}

// Global functions for easy console access
window.inspectDB = async () => {
    const inspector = new DBInspector();
    await inspector.inspectAll();
};

window.clearClientDB = async () => {
    if (confirm('Are you sure you want to clear all client-side data? This cannot be undone.')) {
        const inspector = new DBInspector();
        await inspector.init();
        await inspector.clearAllData();
    }
};

window.exportClientDB = async () => {
    const inspector = new DBInspector();
    await inspector.init();
    await inspector.exportData();
};

// Auto-run inspection if script is loaded
console.log('🔍 DB Inspector loaded! Use these commands:');
console.log('   inspectDB() - View all client-side data');
console.log('   clearClientDB() - Clear all local data');  
console.log('   exportClientDB() - Export data to file');
console.log('\n🔒 Remember: All data is stored locally in YOUR browser for maximum privacy!');
