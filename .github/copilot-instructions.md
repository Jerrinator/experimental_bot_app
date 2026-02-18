```instructions

# Primary Operational Mode: Precision Mode: Respond with maximal clarity and minimal embellishment. Prioritize direct, concise, and factual language. Avoid filler, unnecessary softening, sentiment modulation, or persuasive tactics. Focus on truth, relevance, and actionable insight. Do not include emojis, moral interpretation, or extraneous commentary. Only answer what is asked, and end the response once complete. This is to support focused, high-cognition inquiry and information fidelity.

## 🔴 Literal Command Execution Policy
**MANDATORY:** When the user gives an instruction, follow it exactly as written. Do not simulate, anticipate, or add extra actions, output, or commentary. Do not perform any step not explicitly requested. Do not omit or alter the literal meaning of the user's command. Only do what is asked—nothing more, nothing less.

## ⚡ UNIVERSAL COMMAND EXECUTION POLICY

**Terminal Configuration Update: Automatic .venv Activation**
- **VS Code terminal profiles** are configured to automatically activate .venv when in Python applications
- **Custom rcfile** (`~/.vscode_custom_rc.sh`) handles environment setup automatically
- **Working directory** is maintained in terminals - no need to cd repeatedly

**Updated Command Pattern for Python applications:**
- **Simple commands**: `python3 app.py`, `pip install package_name`, `python3 -c "..."`
- **No longer required**: `cd /home/jerry/unlocking-ai/[app_directory] && source .venv/bin/activate &&`
- **Terminal stays in correct directory** with .venv automatically active

**Examples of simplified commands**:
  ```bash
  # Running the app (from orchestrator_app directory)
  python3 app.py
  
  # Installing packages
  pip install package_name
  
  # Running any Python command
  python3 -c "import sys; print(sys.executable)"
  
  # Testing or debugging
  python3 -m pytest
  ```

**For non-Python work:**
- Use commands directly as normal
- Examples: documentation edits, config files, Node.js commands, system commands

**Note**: This applies when working in VS Code terminals with the updated terminal profile configuration.


# Unlocking A.I. - Human Enhancement Reasoning Optimization and Education System

This repository implements the comprehensive Unlocking A.I. platform - a JWT-based Single Sign-On (SSO) system across multiple Flask microservices with specialized AI applications for business automation and intelligent document processing.

---

## 📋 **COPILOT INSTRUCTIONS - QUICK REFERENCE INDEX**

### **🔍 Navigation by Topic**
| Section | Lines | Purpose | Key Commands |
|---------|-------|---------|--------------|
| **System Architecture** | 60-83 | 9 Application portfolio overview | System understanding |
| **System Utilities** | 205-270 | Utils folder tools & commands | Contact mgmt, edit tracking |
| **JWT Token Structure** | 85-95 | Authentication schema | Token format reference |
| **Security Features** | 99-113 | Authentication requirements | Token handling rules |
| **Protected Sections** | 115-132 | Critical code protection | Edit safety guidelines |
| **Documentation Standards** | 134-146 | Function index requirements | Code documentation |
| **Development Guidelines** | 148-194 | Cross-application consistency | Implementation patterns |
| **Performance Requirements** | 196-209 | Response time targets | Optimization goals |
| **Security Guidelines** | 211-232 | Token & data protection | Security protocols |
| **Documentation Standards** | 234-252 | Function & deployment docs | Documentation requirements |
| **Best Practices** | 254-274 | Development workflow | Quality standards |
| **Edit Tracking System** | 276-306 | Safety protocols | Edit audit & rollback |
| **Diagnostic SOP** | 322-606 | **MANDATORY code edit protocol** | **Error diagnosis workflow** |
| **Implementation Checklist** | 607-623 | Verification requirements | Pre-deployment checks |
| **Project Goals** | 624-631 | Commercial & technical vision | Strategic objectives |

### **⚡ Quick Commands**
```bash
# Jump to specific section by line number (Ctrl+G)
Lines 60-83:   System Architecture Overview
Lines 205-270: System Utilities (Utils Folder)
Lines 99-113:  Security Features & Authentication  
Lines 115-132: Protected Sections (CRITICAL)
Lines 148-194: Development Guidelines
Lines 322-606: Diagnostic SOP (MANDATORY)
Lines 607-623: Implementation Checklist
```

### **🚨 CRITICAL SAFETY SECTIONS**
- **Lines 115-132**: Protected code sections - ALWAYS check before editing
- **Lines 134-146**: Function index updates - REQUIRED for new functions
- **Lines 211-232**: Security guidelines - MANDATORY for authentication work
- **Lines 322-606**: Diagnostic SOP - MANDATORY for all code edits
- **Lines 607-623**: Implementation checklist - VERIFY before deployment

### **🛠️ EDIT SAFETY PROTOCOL**

```bash
# ALWAYS use these commands before ANY edit operation (not just major edits):
# Terminal profiles auto-activate .venv - use simplified commands:
1. Start edit session: python3 -c "from utils.edit_tracker import start_edit_session; start_edit_session('description')"
2. Capture snapshot: python3 -c "from utils.edit_tracker import capture_snapshot; capture_snapshot('file_path')" 
3. Log edits: python3 -c "from utils.edit_tracker import log_edit; log_edit(...)"
4. Validate: python3 -c "from utils.edit_tracker import validate_edit; validate_edit('edit_id', 'status')"
```

**MANDATORY:** Edit tracking is required for every code, config, or documentation change—no exceptions. This maximizes diagnostic capability and enables full audit/rollback for all operations.

### **🎯 UNIVERSAL COMMAND EXECUTION POLICY**

**Terminal Configuration Update: Automatic .venv Activation**
- **VS Code terminal profiles** are configured to automatically activate .venv when in Python applications
- **Custom rcfile** handles environment setup automatically
- **Working directory** is maintained - no need for repeated cd commands

**Simplified Command Pattern for Python applications:**
- **Direct commands**: `python3 app.py`, `pip install package_name`, `python3 -c "..."`
- **No longer required**: Complex cd && source .venv/bin/activate && patterns
- **Terminal automatically handles**: Directory context and .venv activation

**Examples of simplified commands**:
  ```bash
  # Running the app (from app directory)
  python3 app.py
  
  # Installing packages  
  pip install package_name
  
  # Running any Python command
  python3 -c "import sys; print(sys.executable)"
  
  # Testing or debugging
  python3 -m pytest
  ```

**For non-Python work:**
- Use commands directly without .venv activation
- Examples: documentation edits, config files, Node.js commands, system commands


**BUTTON REQUIREMENT:**
For any suggested action, Copilot must provide a clickable button that allows the user to carry out the action directly.

**PATCHING INSTRUCTION:**
Before making any code edit, Copilot must:
1. Analyze the exact code block requiring changes.
2. Ideate and prepare the intended edit.
3. Doublecheck syntax and indentation.
4. Compare the proposed edit against the original code to ensure only the intended change is made.
5. Apply the edit only if it matches the intended change and does not corrupt or remove unrelated code.
This process ensures maximum safety, accuracy, and file integrity for every edit.



### **📖 DOCUMENTATION & CHAT SUMMARY LIBRARY**
- **Comprehensive Chat & Diagnostic Library**: All major chat discussion summaries, bug reports, closure records, technical guides, and business/architecture documentation are indexed and stored in the `unlockingai.docs` directory at the project root. This library is organized by subsystem and topic for direct, efficient diagnostic queries.
- **Documentation Source of Truth:**
    - All new documentation must be created and maintained in the relevant app folder (e.g., `controller_app/controller.docs/`).
    - The sync script will automatically propagate and update the main documentation library (`unlockingai.docs` at the project root) to reflect the latest app-level docs.
    - The app folder is always the authoritative source for its documentation; the library is a synced, up-to-date reference for cross-app and system-wide queries.
- **How Copilot Should Use This Library:**
    1. Treat `unlockingai.docs` at the project root as a primary reference for diagnosis, technical questions, and historical context.
    2. Use the indexed folder structure (by subsystem/topic) to make queries direct and efficient.
    3. Cross-reference bug reports, closure summaries, and implementation guides from this library when troubleshooting or proposing solutions.
    4. Leverage chat summaries and technical docs to provide context-aware, historically informed answers and fixes.

### 🔐 unlockingai.docs: Entry & History Safety (NO SECRETS)

All additions or updates to `unlockingai.docs` MUST follow these rules to prevent secrets from being inserted into the document library or its history:

1. Secret-scan before commit: run the project's secret-scan utility (or an approved equivalent) against any file intended for `unlockingai.docs`. The scan must detect common token patterns (API keys, session keys, tokens, `AstraCS:`, `AIzaSy`, `sk-`/`sk_`, `ASSEMBLY_AI_API_KEY`, `ASTRA_DB_TOKEN`, etc.).

2. Mask found values: any matched secret MUST be replaced with the mask string `****8` in the content that will be committed to `unlockingai.docs` (do not leave raw tokens). Do not commit the unmasked original file into `unlockingai.docs`.

3. Edit tracking and snapshot: start an edit session and capture a snapshot before making any change that will touch `unlockingai.docs` (see Edit Safety Protocol). Log the intent and include which files were scanned and which values (masked) were replaced.

4. Commit-only masked artifacts: only commit masked versions of files into `unlockingai.docs`. If an unmasked sensitive file exists elsewhere in the repo (e.g., app `.env`), do not copy it into `unlockingai.docs`.

5. Historical secrets handling: if a secret is discovered in existing history for `unlockingai.docs`, escalate: create an audit entry noting the commit(s) and backup path, then follow the documented history-remediation workflow (git-filter-repo replace-text with a verified replace-map, backup mirror, verify, and force-push) under an explicit edit session. Do not attempt history rewriting without capturing backups and logging the edit session.

6. Verification: after commit and push, run the secret-scan again on the remote mirror (or local refs) to confirm no secrets remain in HEAD or `unlockingai.docs` history. Record verification output in the edit log.

7. Incident response: any confirmed exposure of active credentials requires immediate rotation of the exposed credentials and an entry in the audit log describing the rotation and remediation steps.

These checks are mandatory for any contributor or automated process that writes to `unlockingai.docs`.
- **Function Index**: `.01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md`
- **Conversation Records**: `.01.UserAndAuthSystem/docs/dev-conversations/`
- **Achievements Summary**: `.01.UserAndAuthSystem/docs/dev-conversations/achievements-summary.md`
- **Enhanced SOP**: `.10.Controller/docs/enhanced-conversation-closure-sop.md`
- **Bug Tracker Log**: `.10.Controller/logs/bug_tracker.log` (Deployment) | `Heroku: heroku run "cat logs/bug_tracker.log"`

---

## 🏗️ System Architecture Overview

The Unlocking A.I. ecosystem includes:
- **Central Authentication Hub**: UserAndAuthSystem with JWT SSO
- **9 Specialized Applications**: AI-powered microservices
- **JWT-Based Security**: 8-hour session tokens with role-based permissions
- **Microservices Architecture**: Independent deployable applications
- **Real-time Communication**: SocketIO integration across applications
- **Vector Database**: AstraDB for semantic search and memory management
- **AI Integration**: OpenAI GPT-4, Whisper, and custom agent frameworks

### Application Portfolio
```
Unlocking A.I. System
├── 🔑 Authentication Hub (.01.UserAndAuthSystem)
├── 💻 Desktop Chatbot (.02.H.E.R.O.S. Windows Chatbot)
├── 🧠 Knowledge Expert (.03.KnowledgeNinja)
├── 🌍 Translation Suite (.04.Globalingo)
├── 📄 OCR Processor (.05.OCR.pdfToTXT.pdf)
├── 📚 Document Chat (.06.InfoNinja)
├── 💬 Chat with Docs (.07.Chat-With-Documents)
├── 🧵 Memory Assistant (.09.InfoMemNinja)
└── 🎛️ Business Manager (.10.Controller)
```

### 🛠️ System Utilities (./utils folder)

**Location:** `/home/jerry/unlocking-ai/utils/`

The utils folder contains system-wide utilities and tools that are available across all applications. Copilot can and should use these utilities when appropriate:

#### **Contact Management System**
- **`manage_contacts.py`** - Full CLI contact management system
  - Interactive contact addition with 60+ comprehensive business fields
  - Search by name, company, email, tags
  - List, view, update, delete contacts
  - ContactManager class for programmatic access
  ```python
  from utils.manage_contacts import ContactManager
  cm = ContactManager()
  contacts = cm.search_contacts("developer", "tags")
  ```

- **`add_contact.py`** - Quick contact addition utility
  ```bash
  python3 utils/add_contact.py "John Doe" "john@example.com" "555-1234" "Company" "Title"
  ```

#### **Edit Tracking & Audit System**
- **`edit_tracker.py`** - Comprehensive edit tracking for all code changes
  - `start_edit_session(description)` - Initialize edit session
  - `capture_snapshot(file_path)` - Capture pre-edit file state
  - `log_edit(...)` - Log detailed edit information
  - `validate_edit(edit_id, status)` - Mark edit success/failure
  - `rollback_edit(edit_id)` - Rollback failed edits

#### **Documentation & Sync Tools**
- **`sync_docs_to_library.py`** - Sync documentation across the repo
- **`sync_copilot_instructions.py`** - Update Copilot instructions across apps

#### **Usage Guidelines for Copilot**
1. **Always use edit tracking** for any code/config/documentation changes
2. **Use contact management** when working with people-related data or business relationships
3. **Leverage existing utilities** before creating new ones
4. **Import from utils** when programmatic access is needed
5. **Run from project root** for proper module resolution

#### **Available Utility Commands**
```bash
# Contact Management
python3 utils/manage_contacts.py                    # Interactive CLI
python3 utils/add_contact.py "Name" "email" "phone" # Quick add

# Edit Tracking (MANDATORY for all edits)
python3 -c "from utils.edit_tracker import start_edit_session; start_edit_session('description')"
python3 -c "from utils.edit_tracker import capture_snapshot; capture_snapshot('file_path')"
python3 -c "from utils.edit_tracker import log_edit; log_edit(...)"
python3 -c "from utils.edit_tracker import validate_edit; validate_edit('edit_id', 'status')"

# Documentation Sync
python3 utils/sync_docs_to_library.py              # Update doc index
python3 utils/sync_copilot_instructions.py         # Sync instructions
```

## 🔐 JWT Token Structure

```json
{
    "user_id": 123,
    "username": "user@example.com",
    "permissions": ["globalingo", "ocr", "knowledgeninja", "infomemninja", "controller"],
    "exp": 1735776000,
    "iat": 1735747200
}
```

## 🛠️ Implementation Requirements

### 1. Security Features

**Authentication:**
- Use HS256 algorithm with shared SECRET_KEY
- Implement proper token expiration handling
- Enforce HTTPS in production environments
- Handle invalid/expired tokens appropriately
- Cross-application permission validation

**Environment Variables:**
- `SECRET_KEY`: Shared across all applications for JWT signing
- `AUTH_SERVICE_URL`: Points to UserAndAuthSystem (https://heros-auth-system-dev.herokuapp.com)
- `OPENAI_API_KEY`: For AI-powered applications
- `ASTRA_DB_TOKEN`: Vector database authentication
- Application-specific configuration variables

### 2. Protected Sections Template

```text
🔒 CUSTOM_PROMPT_PREFIX - RESPECT_PROTECTED_SECTIONS
This section contains verified, production-tested functionality
Any modifications must maintain existing behavior and pass all tests
END_CUSTOM_PROMPT_PREFIX
```

**Critical Protected Areas:**
- JWT authentication logic in all applications
- Database initialization sequences
- SocketIO event handlers and real-time communication
- OpenAI API integration and agent workflows
- Vector database operations (AstraDB)
- PDF export and document processing functionality
- Email notification systems
- Math agent computations and SymPy integration

### 3. Code Documentation Standards

**Function Index Integration:**
- All applications maintain line-numbered function indices
- Use precise line ranges for surgical code editing
- Update function index when adding new functions
- Reference existing documentation at: `/.01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md`

**Edit Safety Protocol:**
- Capture file snapshots before major edits
- Log all changes with intent and context
- Use edit tracking system in .10.Controller for audit trail
- Validate changes before marking as complete

## 🔧 Development Guidelines

### 1. Cross-Application Consistency

**Technology Stack:**
- **Backend**: Python 3.11+, Flask 2.3.3, Gunicorn
- **AI/ML**: OpenAI GPT-4, Whisper, Text Embeddings
- **Database**: PostgreSQL (Auth), AstraDB (Vector Storage)
- **Real-time**: Flask-SocketIO, WebSocket connections
- **Authentication**: JWT tokens, Flask-Login
- **Document Processing**: PyPDF2, Tesseract, python-docx

**Logging Standards:**
- Use consistent logging format across all applications
- Include request IDs, user IDs, and session tracking
- Implement performance timing for critical operations
- Maintain separate logs for different operational concerns

### 2. SSO Implementation Steps

**UserAndAuthSystem Enhancements:**
1. JWT Token Management (✅ Designed, pending implementation)
2. SSO login route with redirect_uri support
3. System-wide logout endpoint
4. Token validation API endpoint
5. Cross-application permission management

**Client App Modifications:**
1. Remove existing independent login pages/routes
2. Add JWT validation middleware to all protected routes
3. Implement redirect to central auth when token invalid/missing
4. Handle JWT tokens from URL parameters and headers
5. Integrate with central user session management

### 3. AI Integration Standards

**OpenAI Integration:**
- Standardize API call patterns across applications
- Implement consistent error handling for API failures
- Use streaming responses where appropriate
- Maintain conversation context and memory management

**Agent Framework (.10.Controller):**
- Math Agent: SymPy integration for complex calculations
- Database Agent: High-performance AstraDB operations
- Session Manager: Real-time communication orchestration
- Logging Agent: Comprehensive audit trail management

## 📊 Performance & Scalability Requirements

### Response Time Targets
- **Authentication**: Sub-200ms token validation
- **Database Operations**: Sub-100ms for standard queries
- **AI Processing**: Context-dependent, log all timing
- **Document Processing**: 10MB+ file support
- **Vector Search**: Sub-100ms semantic queries

### Memory Management
- **Conversation Buffering**: Intelligent context management
- **Document Limits**: Configurable per application
- **Session Management**: Clean up expired sessions
- **Vector Storage**: Efficient embedding management

## 🔒 Security Guidelines

### 1. Token Handling
- Always validate JWT tokens before processing requests
- Check expiration timestamps and user permissions
- Use secure headers for token transmission
- Implement proper error handling for invalid tokens
- Log all authentication attempts and failures

### 2. Data Protection
- Encrypt sensitive data at rest and in transit
- Implement comprehensive input validation
- Use parameterized queries to prevent SQL injection
- Rate limiting on API endpoints
- CORS protection for cross-origin requests

### 3. Audit Logging
- Complete access tracking with correlation IDs
- Log all authentication events
- Track permission changes and administrative actions
- Maintain edit audit trail with rollback capability
- GDPR compliance for data protection and deletion

## 📖 Documentation Standards

### 1. Function Documentation
- Maintain comprehensive line-numbered function index
- Document all public APIs with input/output specifications
- Include usage examples for complex functions
- Cross-reference related functions and dependencies

### 2. Deployment Documentation
- Environment-specific configuration guides
- Heroku deployment procedures with environment variables
- Docker containerization standards
- Local development setup instructions

### 3. Architecture Documentation
- System flow diagrams for complex interactions
- Database schema documentation
- API endpoint specifications
- Integration patterns between applications

## 🚀 Best Practices


### 1. Coding Standards: Reference Best Practices First
- **MANDATORY:** For all new code, edits, and reviews, always reference the corresponding best practices file in `unlockingai.docs/codingbestpractices.doc/` (e.g., `AstraDB_Call_Best_Practices.md`, `OpenAI_API_Best_Practices.md`, `Auth_SSO_Best_Practices.md`, etc.) as the primary coding standard.
- Ensure all implementation, error handling, and testing patterns follow these best practices unless a documented exception is required.
- Keep code, error handling, and documentation consistent with these best practices across all apps.

### 2. Development Workflow
- Use the comprehensive function index for precise editing.
- Implement changes incrementally with validation.
- Test thoroughly across multiple applications.
- Update documentation simultaneously with code changes.
- Respect protected sections to maintain system stability.

### 3. Error Handling
- Implement graceful degradation for service failures.
- Provide meaningful error messages to users.
- Log detailed error information for debugging.
- Implement circuit breakers for external service calls.

### 4. Testing Strategy
- Unit tests for core business logic.
- Integration tests for cross-application functionality.
- End-to-end testing for user workflows.
- Performance testing for critical paths.
- Security testing for authentication flows.

## 📝 Edit Tracking & Rollback System

### Edit Safety Protocol (.10.Controller Integration)
The system includes comprehensive edit tracking to prevent file corruption:

1. **Pre-Edit Snapshots**: Capture file state before modifications
2. **Intent Logging**: Record why each change is being made
3. **Content Tracking**: Log exact content removed and added
4. **Validation Status**: Track success/failure of each edit
5. **Rollback Instructions**: Provide precise recovery steps for failed edits

### Usage Example
```python
# Start edit session
session_id = start_edit_session("JWT SSO implementation")
capture_snapshot("app/routes/auth.py")

# Log edit with full context
edit_id = log_edit(
    file_path="app/routes/auth.py",
    operation_type="replace",
    content_removed="[exact old content]",
    content_added="[exact new content]", 
    edit_intent="Add JWT token generation for SSO",
    copilot_request_id="REQ_20250812_143022_001"
)

# Validate and close session
validate_edit(edit_id, "success")
end_edit_session()
```

## 🏆 System Integration Points

### Cross-Application Communication
- Standardized API patterns between applications
- Consistent error response formats
- Shared logging correlation IDs
- Common environment variable patterns

### Data Flow Management
- User authentication flows through central hub
- Document processing pipelines across applications
- Real-time notification systems
- Shared session state management

## 🩺 **DIAGNOSTIC SOP FOR CODE EDITS - MANDATORY PROTOCOL**

### **📋 OVERVIEW**
This Standard Operating Procedure (SOP) defines the mandatory order of operations for diagnosing and fixing code errors in the Unlocking A.I. system. **ALL CODE EDITS MUST FOLLOW THIS PROTOCOL.**

### **⚡ UNIVERSAL COMMAND EXECUTION POLICY - CRITICAL REMINDER**

**Terminal Configuration Update: Automatic .venv Activation**
- **VS Code terminal profiles** are configured to automatically activate .venv when in Python applications
- **Custom rcfile** handles environment setup automatically
- **Working directory** is maintained - no need for repeated cd commands

**Simplified Command Pattern for Python applications:**
- **Direct commands**: `python app.py`, `pip install package_name`, `python -c "..."`
- **No longer required**: Complex cd && source .venv/bin/activate && patterns
- **Terminal automatically handles**: Directory context and .venv activation

**Examples of simplified commands**:
  ```bash
  # Running the app (from app directory)
  python app.py
  
  # Installing packages  
  pip install package_name
  
  # Running any Python command
  python -c "import sys; print(sys.executable)"
  
  # Testing or debugging
  python -m pytest
  ```

**For non-Python work:**
- Use commands directly as normal
- Examples: documentation edits, config files, Node.js commands, system commands

---

### **🚨 STEP 1: DEPLOYMENT ./logs/ FOLDER CHECK (MANDATORY FIRST - NO EXCEPTIONS)**

#### **1.1 Check Deployment ./logs/ Folder (PRIMARY DIAGNOSTIC RESOURCE - REQUIRED EVERY TIME)**
```sh
# MANDATORY FIRST STEP - ALWAYS start here - check the proprietary diagnostic logs first
heroku run "ls -la logs/"
heroku run "cat logs/controller.log"
heroku run "cat logs/workflow.log"
heroku run "cat logs/browser.log"
heroku run "cat logs/bug_tracker.log"
heroku run "tail -50 logs/controller.log"
heroku run "tail -50 logs/bug_tracker.log"

# For specific error analysis:
heroku run "grep -i 'error|exception|400|500' logs/controller.log | tail -20"
heroku run "grep -i 'socket|connect|polling' logs/controller.log | tail-20"
heroku run "grep -i 'audio|transcribe|recording' logs/browser.log | tail -10"
```

**🔴 CRITICAL REQUIREMENT**: This is the MANDATORY FIRST DIAGNOSTIC STEP for EVERY code edit session
**Purpose**: Access proprietary diagnostic logs from live deployment ./logs/ folder 
**Critical Focus**: Recent error patterns, failed workflows, missing expected log entries, historical bug patterns
**NO EXCEPTIONS RULE**: NEVER make any code edits without first checking these deployment ./logs/ folder contents

#### **1.2 Read Master Index**
```bash
# Understand the system layout
cat ".01.UserAndAuthSystem/docs/dev-conversations/index_of_conversations.md"
```

**Purpose**: Get complete system overview and locate relevant documentation sections

#### **1.3 Read Function Index**
```bash
# Get precise function locations and protected sections
cat ".01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md"
```

**Critical Focus Areas:**
- **Protected Sections**: Lines containing `🔒 PROTECTED` markers
- **Function Line Numbers**: Exact ranges for surgical edits
- **Cross-References**: Related functions and dependencies

#### **1.4 Identify Affected Application & Local Controller Logs**
Based on error context, determine which application(s) are involved and target specific controller.log:

Based on error context, determine which application(s) are involved and target specific controller.log:

**🔐 Authentication Issues:**
```bash
# Show recent controller log entries and filter for auth-related patterns
tail -n 500 ".01.UserAndAuthSystem/controller.log" | grep -E -n -C 10 "ERROR|AUTH|JWT|TOKEN"
```

**🧠 AI Processing Errors:**
```bash
# Knowledge Expert
tail -n 500 ".03.KnowledgeNinja/controller.log" | grep -E -n -C 10 "ERROR|AI|OPENAI"

# Document Chat
tail -n 500 ".06.InfoNinja/controller.log" | grep -E -n -C 10 "ERROR|DOCUMENT|SEARCH"

# Memory Assistant
tail -n 500 ".09.InfoMemNinja/controller.log" | grep -E -n -C 10 "ERROR|MEMORY|VECTOR"
```

**📄 Document Processing Issues:**
```bash
# OCR Processing
tail -n 500 ".05.OCR.pdfToTXT.pdf/controller.log" | grep -E -n -C 10 "ERROR|OCR|PDF"

# Chat with Documents
tail -n 500 ".07.Chat-With-Documents/controller.log" | grep -E -n -C 10 "ERROR|CHAT|DOCUMENT"
```

**🌍 Translation & Other Services:**
```bash
# Translation Suite
tail -n 500 ".04.Globalingo/controller.log" | grep -E -n -C 10 "ERROR|TRANSLATE|LANGUAGE"

# Desktop Chatbot
tail -n 500 ".02.H.E.R.O.S. Windows Chatbot/controller.log" | grep -E -n -C 10 "ERROR|DESKTOP|WINDOWS"
```

**🎛️ Business Management & Orchestration:**
```bash
# Primary Controller (orchestration and business logic)
tail -n 500 ".10.Controller/controller.log" | grep -E -n -C 10 "ERROR|AGENT|WORKFLOW"

# Root-level system coordination
tail -n 500 controller.log | grep -E -n -C 10 "ERROR|SYSTEM|COORDINATION"
```

**🔄 Cross-Application Issues:**
```bash
# Check multiple logs for integration failures
tail -n 200 ".01.UserAndAuthSystem/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "SSO|JWT|AUTH"
```

---

### **🔍 STEP 2: CONTROLLER LOG ANALYSIS (MANDATORY)**

#### **2.1 Read Relevant Controller Log Sections**
```bash
# Target the specific application's controller.log based on error context
# Use the application mapping from Step 1.3 to select the correct log file

# Example for Authentication errors:
tail -n 500 ".01.UserAndAuthSystem/controller.log" | grep -E -n -C 10 "ERROR_PATTERN"

# Example for Business logic errors:
tail -n 500 ".10.Controller/controller.log" | grep -E -n -C 10 "ERROR_PATTERN"

# For system-wide coordination issues:
tail -n 500 controller.log | grep -E -n -C 10 "ERROR_PATTERN"
```

#### **2.2 Extract Expected Workflow**
**Critical Analysis Questions:**
1. **What was the intended workflow?** (Look for workflow initiation logs)
2. **Where did it fail?** (Identify failure point in sequence)
3. **What was the expected next step?** (Understand broken flow)
4. **Are there related successful runs?** (Compare working vs broken patterns)

#### **2.3 Identify Workflow Context**
```bash
# Get timestamp-based context around the error from the appropriate application log
# Use the specific controller.log identified in Step 1.3

# Example patterns for different applications:
# Authentication workflow context:
grep -n "timestamp_pattern" ".01.UserAndAuthSystem/controller.log" | head -n 20 || true

# AI processing workflow context:
grep -n "timestamp_pattern" ".03.KnowledgeNinja/controller.log" | head -n 20 || true

# Business orchestration workflow context:
grep -n "timestamp_pattern" ".10.Controller/controller.log" | head -n 20 || true

# System coordination workflow context:
grep -n "timestamp_pattern" controller.log | head -n 20 || true
```

**Focus Areas:**
- **Request ID correlation**: Track the complete request flow
- **User session context**: Understand authentication state
- **Performance timing**: Identify bottlenecks or timeouts
- **Integration points**: Cross-application communication failures

---

### **🧠 STEP 3: CODEFLOW UNDERSTANDING (MANDATORY)**

#### **3.1 Map Expected vs Actual Flow**
Based on controller logs, create mental model:

**Expected Flow:**
```
[Log Entry 1] → [Expected Step 2] → [Expected Step 3] → [Success]
```

**Actual Flow:**
```
[Log Entry 1] → [Actual Step 2] → [ERROR] → [Failure]
```

#### **3.2 Identify Code Sections**
Using function index, locate exact code sections involved:
- **Entry Point**: Where the workflow begins
- **Failure Point**: Where the error occurs
- **Expected Next Step**: What should have happened
- **Dependencies**: Related functions and integrations

#### **3.3 Read Protected Sections Warning**
```bash
# Check if affected code is in protected sections
grep -n "🔒 PROTECTED" ".01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md" || true
```

---

### **📊 STEP 4: ERROR CONTEXT ANALYSIS**

#### **4.1 Error Classification**
Categorize the error type:
- **🔐 Authentication**: JWT token, SSO, permission issues
- **🗄️ Database**: Query failures, connection issues, data integrity
- **🤖 AI Processing**: OpenAI API, agent failures, context issues
- **📁 File Operations**: Upload, OCR, document processing
- **🌐 Network**: Service communication, timeout, connectivity
- **⚡ Performance**: Memory, CPU, response time issues

#### **4.2 Bug Pattern Analysis (MANDATORY)**
**Check bug_tracker.log for similar issues:**
```bash
# Look for recurring patterns in the bug tracker
heroku run "grep -i 'error_type_keyword' logs/bug_tracker.log"
heroku run "grep -i 'indentation\|syntax\|import' logs/bug_tracker.log"
heroku run "tail -100 logs/bug_tracker.log | grep -i 'BUG_PATTERN'"
```

**Key Questions:**
- Has this exact error occurred before?
- What was the root cause of similar errors?
- Are there documented patterns for this error type?
- What fixes have worked previously?

#### **4.3 Impact Assessment**
- **Single User**: Isolated to specific session
- **Multi-User**: Affecting multiple sessions
- **System-Wide**: Platform-level failure
- **Critical Path**: Blocking core functionality

#### **4.4 Related Systems Check**
Based on error type, check related application logs:
```bash
# Authentication issues - check auth system and dependent applications
tail -n 200 ".01.UserAndAuthSystem/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true

# AI processing issues - check AI apps and orchestration
tail -n 200 ".03.KnowledgeNinja/controller.log" ".09.InfoMemNinja/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true

# Document processing - check document apps and storage
tail -n 200 ".05.OCR.pdfToTXT.pdf/controller.log" ".06.InfoNinja/controller.log" ".07.Chat-With-Documents/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true

# System-wide issues - check root coordination and primary applications
tail -n 200 controller.log ".01.UserAndAuthSystem/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true
```

---

### **🛠️ STEP 5: EDIT PREPARATION (MANDATORY)**

#### **5.1 Start Edit Session**
```python
# ALWAYS start edit tracking before ANY changes
from utils.edit_tracker import start_edit_session
session_id = start_edit_session("Fix: [ERROR_DESCRIPTION]")
```

#### **5.2 Capture Snapshots**
```python
# Snapshot ALL files that might be modified
from utils.edit_tracker import capture_snapshot
capture_snapshot("path/to/affected/file.py")
```

#### **5.3 Verify Understanding**
**Mandatory Verification Checklist:**
- [ ] **Expected workflow understood** from controller logs
- [ ] **Failure point identified** with exact line numbers
- [ ] **Root cause hypothesis** formed based on logs and code
- [ ] **Protected sections checked** and respected
- [ ] **Edit session started** with comprehensive tracking
- [ ] **Rollback plan prepared** in case of failure

---

### **🔧 STEP 6: SURGICAL EDIT EXECUTION**

#### **6.1 Targeted Fix Implementation**
- **Use exact line numbers** from function index
- **Preserve protected sections** completely
- **Maintain existing behavior** for unrelated code
- **Log edit intent** with comprehensive context

#### **6.2 Edit Logging**
```python
edit_id = log_edit(
    file_path="exact/file/path.py",
    operation_type="replace",
    lines_affected="start-end",
    content_removed="[EXACT ORIGINAL CODE]",
    content_added="[EXACT NEW CODE]",
    edit_intent="Fix: [SPECIFIC ERROR] - Root cause: [ANALYSIS]",
    workflow_context="Expected: [WORKFLOW] - Failed at: [POINT]",
    copilot_request_id="REQ_[TIMESTAMP]_001"
)
```

#### **6.3 Change Validation**
- **Syntax check**: Ensure valid Python/JavaScript/HTML
- **Logic validation**: Verify fix addresses root cause
- **Integration check**: Ensure compatibility with related systems
- **Protected section verification**: Confirm no unintended changes
- **HTML validation** (for frontend edits): Run mandatory syntax test

#### **6.4 HTML Syntax Validation (MANDATORY for Frontend Edits)**
For any edits to HTML files, always run this validation command:
```bash
# Simple HTML structure checks with line numbers
grep -n -E "<html|</html>|<head|</head>|<body|</body>|<script|</script>|<style|</style>" public/index.html || true
```

**Required Structure Validation:**
- ✅ `<!DOCTYPE html>` declaration present
- ✅ `<html>` and `</html>` tags properly paired
- ✅ `<head>` and `</head>` tags properly paired  
- ✅ `<body>` and `</body>` tags properly paired
- ✅ `<style>` and `</style>` tags properly paired
- ✅ All `<script>` tags properly formatted
- ✅ No corrupted or malformed tag structures

**Validation Report Template:**
```
## ✅ HTML Syntax Test Results:
Structure Analysis:
1. ✅ <!DOCTYPE html> - Line X
2. ✅ <html> - Line X  
3. ✅ <head> - Line X
4. ✅ </head> - Line X
5. ✅ <body> - Line X
6. ✅ </body> - Line X
7. ✅ </html> - Line X

Overall Assessment: 🟢 No syntax errors found!
```

---

### **✅ STEP 7: VALIDATION & TESTING**

#### **7.1 Immediate Testing**
1. **Reproduce original error scenario**
2. **Verify fix resolves the issue**
3. **Test related functionality** for regressions
4. **Check controller logs** for successful workflow completion
5. **Run HTML syntax validation** (for frontend edits - see section 6.4)

#### **7.2 Integration Validation**
- **Cross-application testing**: Verify SSO, API calls still work
- **Performance check**: Ensure no degradation
- **Security validation**: Confirm authentication flows intact

#### **7.3 Documentation Updates**
```python
# Update function index if new functions added
# Update conversation log with resolution details
# Mark edit as successful in tracking system
validate_edit(edit_id, "success", "Error resolved - workflow restored")
```

---

### **🚨 STEP 8: FAILURE RECOVERY PROTOCOL**

#### **8.1 If Edit Fails**
```python
# IMMEDIATELY execute rollback
from utils.edit_tracker import rollback_edit
rollback_edit(edit_id)
```

#### **8.2 Failure Analysis**
- **Re-examine controller logs** for missed context
- **Review function index** for overlooked dependencies
- **Check protected sections** for conflicts
- **Consult achievements summary** for similar past issues

#### **8.3 Alternative Approach**
- **Broader context analysis**: Look at larger system interactions
- **Consult conversation history** for similar resolved issues
- **Consider conversation snapshot rollback** if widespread issues

---

### **📈 STEP 9: POST-RESOLUTION DOCUMENTATION**

#### **9.1 Update Conversation Log**
Document the resolution in current conversation file:
```markdown
### Error Resolution: [ERROR_TYPE]
- **Issue**: [DESCRIPTION]
- **Root Cause**: [ANALYSIS FROM LOGS]
- **Solution**: [SPECIFIC FIX APPLIED]
- **Workflow Restored**: [CONFIRMED WORKING FLOW]
- **Edit ID**: [TRACKING_REFERENCE]
```

#### **9.2 Update Achievements if Significant**
For major fixes or new patterns, update achievements summary

#### **9.3 Function Index Updates**
If new functions added or major changes made, update the function index

---

### **🎯 CRITICAL SUCCESS FACTORS**

#### **Always Remember:**
1. **INDEX FIRST**: Never skip the documentation consultation phase
2. **LOGS REVEAL TRUTH**: Controller logs show actual vs expected flow
3. **PROTECT WORKING CODE**: Respect protected sections absolutely
4. **TRACK EVERYTHING**: Edit tracking prevents "file corrupted" scenarios
5. **VALIDATE THOROUGHLY**: Test beyond just the immediate fix
6. **DOCUMENT SOLUTIONS**: Help future debugging efforts

#### **Never:**
- Skip the index consultation phase
- Edit code without understanding expected workflow
- Modify protected sections without extreme care
- Make changes without edit tracking
- Assume understanding without log analysis
- Implement fixes without testing validation

---

### **🔄 QUICK REFERENCE COMMAND SEQUENCE**

```bash
# 1. Deployment ./logs/ Folder (MANDATORY FIRST - NO EXCEPTIONS)
# Change to your controller directory (example path)
cd "/path/to/.10.Controller"
heroku run "ls -la logs/"
heroku run "cat logs/controller.log"
heroku run "cat logs/workflow.log"
heroku run "cat logs/browser.log"
heroku run "cat logs/bug_tracker.log"
heroku run "tail -50 logs/controller.log"
heroku run "tail -50 logs/bug_tracker.log"

# 2. System Understanding
cat ".01.UserAndAuthSystem/docs/dev-conversations/index_of_conversations.md"
cat ".01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md"

# 3. Application-Specific Log Analysis
# Authentication issues:
tail -n 500 ".01.UserAndAuthSystem/controller.log" | grep -E -n -C 10 "ERROR" || true

# Business management issues:
tail -n 500 ".10.Controller/controller.log" | grep -E -n -C 10 "ERROR" || true

# System coordination issues:
tail -n 500 controller.log | grep -E -n -C 10 "ERROR" || true

# 4. Edit Safety
# Terminal profiles auto-activate .venv - use simplified commands:
python -c "from utils.edit_tracker import start_edit_session; start_edit_session('Fix: ERROR_DESC')"
python -c "from utils.edit_tracker import capture_snapshot; capture_snapshot('file_path')"

# 5. HTML Syntax Validation (for frontend edits)
grep -n -E "<html|</html>|<head|</head>|<body|</body>|<script|</script>|<style|</style>" public/index.html || true

# 6. Validation
# Terminal profiles auto-activate .venv - use simplified commands:
python3 -c "from utils.edit_tracker import validate_edit; validate_edit('edit_id', 'success')"
```

This SOP ensures that every code edit is informed by the complete system understanding and follows our established safety protocols.

## 📋 Implementation Checklist

When working on any application within the Unlocking A.I. system:

- [ ] Verify JWT authentication integration
- [ ] Check protected sections before editing
- [ ] Update function index for new functions
- [ ] Implement consistent logging patterns
- [ ] Test cross-application compatibility
- [ ] Validate security requirements
- [ ] Update relevant documentation
- [ ] Use edit tracking for significant changes
- [ ] Verify environment variable configuration
- [ ] Test deployment procedures

---

## 🎯 Project Goals

**Commercial Objective**: Transform the BusinessManager (.10.Controller) into a marketable proof-of-concept for AI-powered business automation, providing financial independence through innovative technology.

**Technical Vision**: Create an AI system that uses artificial intelligence to improve and optimize itself through recursive enhancement capabilities, approaching the architectural patterns needed for AGI development.

**Quality Standards**: Maintain enterprise-grade code quality, comprehensive documentation, and robust security practices suitable for commercial deployment and business development.

## 🧑‍💻 Coder expectations (user-facing)

The following authoritative instruction excerpts are copied here for quick reference and must be treated as unmodified source-of-truth when executing coding tasks for the user. These are duplicated from other sections of this file and are included here verbatim for clarity.

### Primary Operational Mode: Precision Mode

Respond with maximal clarity and minimal embellishment. Prioritize direct, concise, and factual language. Avoid filler, unnecessary softening, sentiment modulation, or persuasive tactics. Focus on truth, relevance, and actionable insight. Do not include emojis, moral interpretation, or extraneous commentary. Only answer what is asked, and end the response once complete.


These are the concrete, non-negotiable expectations the user has for the assistant when performing coding work in this repository:

- Execute only the explicit artifact or operation requested by the user; do not add unrelated changes or unsolicited suggestions.
- Before any edit that modifies source or docs, create a backup/snapshot and record an edit-tracking entry (snapshot id or backup path) and include it in the commit message.
- Do minimal, surgical changes focused on the requested task. Prefer small commits with clear messages and include the request id or short note tying the change to the discussion.
- When creating or changing runnable code, include or update at least one minimal test for the changed behavior and run the test locally; report results.
- Do not commit or push changes to remote unless the user explicitly requests a commit or push; if the user requests a push, report the push result (success/failure and remote URL).
- Treat secrets as strictly out-of-band: never write plaintext secrets into `unlockingai.docs` or any committed docs; mask secrets as `****8` and run the repo secret-scan before committing docs.
- Provide a compact checklist of what was changed, why, and how to validate the change at the top of the commit message or the pull request description.
- When proposing broader instruction changes (e.g., to this file), always present the patch text for approval and do not apply it without explicit user approval.

Edge cases to handle explicitly:
- If an edit could affect protected sections or authentication code, stop and require explicit user confirmation before proceeding.
- If tests fail after making a requested change, revert the change locally, record the failure in the edit log, and present options to the user.

---



### 🔴 Literal Command Execution Policy
**MANDATORY:** When the user gives an instruction, follow it exactly as written. Do not simulate, anticipate, or add extra actions, output, or commentary. Do not perform any step not explicitly requested. Do not omit or alter the literal meaning of the user's command. Only do what is asked—nothing more, nothing less.

## 🚨 STEP 1: DEPLOYMENT ./logs/ FOLDER CHECK (MANDATORY FIRST - NO EXCEPTIONS)

#### **1.1 Check Deployment ./logs/ Folder (PRIMARY DIAGNOSTIC RESOURCE - REQUIRED EVERY TIME)**
```sh
# MANDATORY FIRST STEP - ALWAYS start here - check the proprietary diagnostic logs first
heroku run "ls -la logs/"
heroku run "cat logs/controller.log"
heroku run "cat logs/workflow.log"
heroku run "cat logs/browser.log"
heroku run "cat logs/bug_tracker.log"
heroku run "tail -50 logs/controller.log"
heroku run "tail -50 logs/bug_tracker.log"

# For specific error analysis:
heroku run "grep -i 'error|exception|400|500' logs/controller.log | tail -20"
heroku run "grep -i 'socket|connect|polling' logs/controller.log | tail -20"
heroku run "grep -i 'audio|transcribe|recording' logs/browser.log | tail -10"
```

**🔴 CRITICAL REQUIREMENT**: This is the MANDATORY FIRST DIAGNOSTIC STEP for EVERY code edit session
**Purpose**: Access proprietary diagnostic logs from live deployment ./logs/ folder 
**Critical Focus**: Recent error patterns, failed workflows, missing expected log entries, historical bug patterns
**NO EXCEPTIONS RULE**: NEVER make any code edits without first checking these deployment ./logs/ folder contents

#### **1.2 Read Master Index**
```bash
# Understand the system layout
cat ".01.UserAndAuthSystem/docs/dev-conversations/index_of_conversations.md"
```

**Purpose**: Get complete system overview and locate relevant documentation sections

#### **1.3 Read Function Index**
```bash
# Get precise function locations and protected sections
cat ".01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md"
```

**Critical Focus Areas:**
- **Protected Sections**: Lines containing `🔒 PROTECTED` markers
- **Function Line Numbers**: Exact ranges for surgical edits
- **Cross-References**: Related functions and dependencies

#### **1.4 Identify Affected Application & Local Controller Logs**
Based on error context, determine which application(s) are involved and target specific controller.log:

Based on error context, determine which application(s) are involved and target specific controller.log:

**🔐 Authentication Issues:**
```bash
# Show recent controller log entries and filter for auth-related patterns
tail -n 500 ".01.UserAndAuthSystem/controller.log" | grep -E -n -C 10 "ERROR|AUTH|JWT|TOKEN"
```

**🧠 AI Processing Errors:**
```bash
# Knowledge Expert
tail -n 500 ".03.KnowledgeNinja/controller.log" | grep -E -n -C 10 "ERROR|AI|OPENAI"

# Document Chat
tail -n 500 ".06.InfoNinja/controller.log" | grep -E -n -C 10 "ERROR|DOCUMENT|SEARCH"

# Memory Assistant
tail -n 500 ".09.InfoMemNinja/controller.log" | grep -E -n -C 10 "ERROR|MEMORY|VECTOR"
```

**📄 Document Processing Issues:**
```bash
# OCR Processing
tail -n 500 ".05.OCR.pdfToTXT.pdf/controller.log" | grep -E -n -C 10 "ERROR|OCR|PDF"

# Chat with Documents
tail -n 500 ".07.Chat-With-Documents/controller.log" | grep -E -n -C 10 "ERROR|CHAT|DOCUMENT"
```

**🌍 Translation & Other Services:**
```bash
# Translation Suite
tail -n 500 ".04.Globalingo/controller.log" | grep -E -n -C 10 "ERROR|TRANSLATE|LANGUAGE"

# Desktop Chatbot
tail -n 500 ".02.H.E.R.O.S. Windows Chatbot/controller.log" | grep -E -n -C 10 "ERROR|DESKTOP|WINDOWS"
```

**🎛️ Business Management & Orchestration:**
```bash
# Primary Controller (orchestration and business logic)
tail -n 500 ".10.Controller/controller.log" | grep -E -n -C 10 "ERROR|AGENT|WORKFLOW"

# Root-level system coordination
tail -n 500 controller.log | grep -E -n -C 10 "ERROR|SYSTEM|COORDINATION"
```

**🔄 Cross-Application Issues:**
```bash
# Check multiple logs for integration failures
tail -n 200 ".01.UserAndAuthSystem/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "SSO|JWT|AUTH"
```

---

### **🔍 STEP 2: CONTROLLER LOG ANALYSIS (MANDATORY)**

#### **2.1 Read Relevant Controller Log Sections**
```bash
# Target the specific application's controller.log based on error context
# Use the application mapping from Step 1.3 to select the correct log file

# Example for Authentication errors:
tail -n 500 ".01.UserAndAuthSystem/controller.log" | grep -E -n -C 10 "ERROR_PATTERN"
```

#### **2.2 Extract Expected Workflow**
**Critical Analysis Questions:**
1. **What was the intended workflow?** (Look for workflow initiation logs)
2. **Where did it fail?** (Identify failure point in sequence)
3. **What was the expected next step?** (Understand broken flow)
4. **Are there related successful runs?** (Compare working vs broken patterns)

#### **2.3 Identify Workflow Context**
```bash
# Get timestamp-based context around the error from the appropriate application log
# Use the specific controller.log identified in Step 1.3

# Example patterns for different applications:
# Authentication workflow context:
grep -n "timestamp_pattern" ".01.UserAndAuthSystem/controller.log" | head -n 20 || true

# AI processing workflow context:
grep -n "timestamp_pattern" ".03.KnowledgeNinja/controller.log" | head -n 20 || true

# Business orchestration workflow context:
grep -n "timestamp_pattern" ".10.Controller/controller.log" | head -n 20 || true

# System coordination workflow context:
grep -n "timestamp_pattern" controller.log | head -n 20 || true
```

**Focus Areas:**
- **Request ID correlation**: Track the complete request flow
- **User session context**: Understand authentication state
- **Performance timing**: Identify bottlenecks or timeouts
- **Integration points**: Cross-application communication failures

---

### **🧠 STEP 3: CODEFLOW UNDERSTANDING (MANDATORY)**

#### **3.1 Map Expected vs Actual Flow**
Based on controller logs, create mental model:

**Expected Flow:**
```
[Log Entry 1] → [Expected Step 2] → [Expected Step 3] → [Success]
```

**Actual Flow:**
```
[Log Entry 1] → [Expected Step 2] → [ERROR] → [Failure]
```

#### **3.2 Identify Code Sections**
Using function index, locate exact code sections involved:
- **Entry Point**: Where the workflow begins
- **Failure Point**: Where the error occurs
- **Expected Next Step**: What should have happened
- **Dependencies**: Related functions and integrations

#### **3.3 Read Protected Sections Warning**
```bash
# Check if affected code is in protected sections
grep -n "🔒 PROTECTED" ".01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md" || true
```

---

### **📊 STEP 4: ERROR CONTEXT ANALYSIS**

#### **4.1 Error Classification**
Categorize the error type:
- **🔐 Authentication**: JWT token, SSO, permission issues
- **🗄️ Database**: Query failures, connection issues, data integrity
- **🤖 AI Processing**: OpenAI API, agent failures, context issues
- **📁 File Operations**: Upload, OCR, document processing
- **🌐 Network**: Service communication, timeout, connectivity
- **⚡ Performance**: Memory, CPU, response time issues

#### **4.2 Bug Pattern Analysis (MANDATORY)**
**Check bug_tracker.log for similar issues:**
```bash
# Look for recurring patterns in the bug tracker
heroku run "grep -i 'error_type_keyword' logs/bug_tracker.log"
heroku run "grep -i 'indentation\|syntax\|import' logs/bug_tracker.log"
heroku run "tail -100 logs/bug_tracker.log | grep -i 'BUG_PATTERN'"
```

**Key Questions:**
- Has this exact error occurred before?
- What was the root cause of similar errors?
- Are there documented patterns for this error type?
- What fixes have worked previously?

#### **4.3 Impact Assessment**
- **Single User**: Isolated to specific session
- **Multi-User**: Affecting multiple sessions
- **System-Wide**: Platform-level failure
- **Critical Path**: Blocking core functionality

#### **4.4 Related Systems Check**
Based on error type, check related application logs:
```bash
# Authentication issues - check auth system and dependent applications
tail -n 200 ".01.UserAndAuthSystem/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true

# AI processing issues - check AI apps and orchestration
tail -n 200 ".03.KnowledgeNinja/controller.log" ".09.InfoMemNinja/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true

# Document processing - check document apps and storage
tail -n 200 ".05.OCR.pdfToTXT.pdf/controller.log" ".06.InfoNinja/controller.log" ".07.Chat-With-Documents/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true

# System-wide issues - check root coordination and primary applications
tail -n 200 controller.log ".01.UserAndAuthSystem/controller.log" ".10.Controller/controller.log" | grep -E -n -C 5 "error_timestamp_range" || true
```

---

### **🛠️ STEP 5: EDIT PREPARATION (MANDATORY)**

#### **5.1 Start Edit Session**
```python
# ALWAYS start edit tracking before ANY changes
from utils.edit_tracker import start_edit_session
session_id = start_edit_session("Fix: [ERROR_DESCRIPTION]")
```

#### **5.2 Capture Snapshots**
```python
# Snapshot ALL files that might be modified
from utils.edit_tracker import capture_snapshot
capture_snapshot("path/to/affected/file.py")
```

#### **5.3 Verify Understanding**
**Mandatory Verification Checklist:**
- [ ] **Expected workflow understood** from controller logs
- [ ] **Failure point identified** with exact line numbers
- [ ] **Root cause hypothesis** formed based on logs and code
- [ ] **Protected sections checked** and respected
- [ ] **Edit session started** with comprehensive tracking
- [ ] **Rollback plan prepared** in case of failure

---

### **🔧 STEP 6: SURGICAL EDIT EXECUTION**

#### **6.1 Targeted Fix Implementation**
- **Use exact line numbers** from function index
- **Preserve protected sections** completely
- **Maintain existing behavior** for unrelated code
- **Log edit intent** with comprehensive context

#### **6.2 Edit Logging**
```python
edit_id = log_edit(
    file_path="exact/file/path.py",
    operation_type="replace",
    lines_affected="start-end",
    content_removed="[EXACT ORIGINAL CODE]",
    content_added="[EXACT NEW CODE]",
    edit_intent="Fix: [SPECIFIC ERROR] - Root cause: [ANALYSIS]",
    workflow_context="Expected: [WORKFLOW] - Failed at: [POINT]",
    copilot_request_id="REQ_[TIMESTAMP]_001"
)
```

#### **6.3 Change Validation**
- **Syntax check**: Ensure valid Python/JavaScript/HTML
- **Logic validation**: Verify fix addresses root cause
- **Integration check**: Ensure compatibility with related systems
- **Protected section verification**: Confirm no unintended changes
- **HTML validation** (for frontend edits): Run mandatory syntax test

#### **6.4 HTML Syntax Validation (MANDATORY for Frontend Edits)**
For any edits to HTML files, always run this validation command:
```bash
# Simple HTML structure checks with line numbers
grep -n -E "<html|</html>|<head|</head>|<body|</body>|<script|</script>|<style|</style>" public/index.html || true
```

**Required Structure Validation:**
- ✅ `<!DOCTYPE html>` declaration present
- ✅ `<html>` and `</html>` tags properly paired
- ✅ `<head>` and `</head>` tags properly paired  
- ✅ `<body>` and `</body>` tags properly paired
- ✅ `<style>` and `</style>` tags properly paired
- ✅ All `<script>` tags properly formatted
- ✅ No corrupted or malformed tag structures

**Validation Report Template:**
```
## ✅ HTML Syntax Test Results:
Structure Analysis:
1. ✅ <!DOCTYPE html> - Line X
2. ✅ <html> - Line X  
3. ✅ <head> - Line X
4. ✅ </head> - Line X
5. ✅ <body> - Line X
6. ✅ </body> - Line X
7. ✅ </html> - Line X

Overall Assessment: 🟢 No syntax errors found!
```

---

### **✅ STEP 7: VALIDATION & TESTING**

#### **7.1 Immediate Testing**
1. **Reproduce original error scenario**
2. **Verify fix resolves the issue**
3. **Test related functionality** for regressions
4. **Check controller logs** for successful workflow completion
5. **Run HTML syntax validation** (for frontend edits - see section 6.4)

#### **7.2 Integration Validation**
- **Cross-application testing**: Verify SSO, API calls still work
- **Performance check**: Ensure no degradation
- **Security validation**: Confirm authentication flows intact

#### **7.3 Documentation Updates**
```python
# Update function index if new functions added
# Update conversation log with resolution details
# Mark edit as successful in tracking system
validate_edit(edit_id, "success", "Error resolved - workflow restored")
```

---

### **🚨 STEP 8: FAILURE RECOVERY PROTOCOL**

#### **8.1 If Edit Fails**
```python
# IMMEDIATELY execute rollback
from utils.edit_tracker import rollback_edit
rollback_edit(edit_id)
```

#### **8.2 Failure Analysis**
- **Re-examine controller logs** for missed context
- **Review function index** for overlooked dependencies
- **Check protected sections** for conflicts
- **Consult achievements summary** for similar past issues

#### **8.3 Alternative Approach**
- **Broader context analysis**: Look at larger system interactions
- **Consult conversation history** for similar resolved issues
- **Consider conversation snapshot rollback** if widespread issues

---

### **📈 STEP 9: POST-RESOLUTION DOCUMENTATION**

#### **9.1 Update Conversation Log**
Document the resolution in current conversation file:
```markdown
### Error Resolution: [ERROR_TYPE]
- **Issue**: [DESCRIPTION]
- **Root Cause**: [ANALYSIS FROM LOGS]
- **Solution**: [SPECIFIC FIX APPLIED]
- **Workflow Restored**: [CONFIRMED WORKING FLOW]
- **Edit ID**: [TRACKING_REFERENCE]
```

#### **9.2 Update Achievements if Significant**
For major fixes or new patterns, update achievements summary

#### **9.3 Function Index Updates**
If new functions added or major changes made, update the function index

---

### **🎯 CRITICAL SUCCESS FACTORS**

#### **Always Remember:**
1. **INDEX FIRST**: Never skip the documentation consultation phase
2. **LOGS REVEAL TRUTH**: Controller logs show actual vs expected flow
3. **PROTECT WORKING CODE**: Respect protected sections absolutely
4. **TRACK EVERYTHING**: Edit tracking prevents "file corrupted" scenarios
5. **VALIDATE THOROUGHLY**: Test beyond just the immediate fix
6. **DOCUMENT SOLUTIONS**: Help future debugging efforts

#### **Never:**
- Skip the index consultation phase
- Edit code without understanding expected workflow
- Modify protected sections without extreme care
- Make changes without edit tracking
- Assume understanding without log analysis
- Implement fixes without testing validation

---

### **🔄 QUICK REFERENCE COMMAND SEQUENCE**

```bash
# 1. Deployment ./logs/ Folder (MANDATORY FIRST - NO EXCEPTIONS)
# Change to your controller directory (example path)
cd "/path/to/.10.Controller"
heroku run "ls -la logs/"
heroku run "cat logs/controller.log"
heroku run "cat logs/workflow.log"
heroku run "cat logs/browser.log"
heroku run "cat logs/bug_tracker.log"
heroku run "tail -50 logs/controller.log"
heroku run "tail -50 logs/bug_tracker.log"

# 2. System Understanding
cat ".01.UserAndAuthSystem/docs/dev-conversations/index_of_conversations.md"
cat ".01.UserAndAuthSystem/docs/dev-conversations/codebase_function_index.md"

# 3. Application-Specific Log Analysis
# Authentication issues:
tail -n 500 ".01.UserAndAuthSystem/controller.log" | grep -E -n -C 10 "ERROR" || true

# Business management issues:
tail -n 500 ".10.Controller/controller.log" | grep -E -n -C 10 "ERROR" || true

# System coordination issues:
tail -n 500 controller.log | grep -E -n -C 10 "ERROR" || true

# 4. Edit Safety
# Terminal profiles auto-activate .venv - use simplified commands:
python3 -c "from utils.edit_tracker import start_edit_session; start_edit_session('Fix: ERROR_DESC')"
python3 -c "from utils.edit_tracker import capture_snapshot; capture_snapshot('file_path')"

# 5. HTML Syntax Validation (for frontend edits)
grep -n -E "<html|</html>|<head|</head>|<body|</body>|<script|</script>|<style|</style>" public/index.html || true

# 6. Validation
# Terminal profiles auto-activate .venv - use simplified commands:
python3 -c "from utils.edit_tracker import validate_edit; validate_edit('edit_id', 'success')"
```

This SOP ensures that every code edit is informed by the complete system understanding and follows our established safety protocols.

---

## 🚨 NEW INCLUSION: MAXIMUM DEBUG LOGGING IN ALL NEW CODE

### **Logging Standards Enhancement**

- Maximum debug logging in all new code: For all new code, insert extensive debug logging statements at function entry and exit, include input parameters (where safe and sanitized), key state transitions, decisions, and errors. Use structured logging with clear, consistent formats (such as JSON objects or key=value pairs). Do not log secrets or sensitive credentials; redact or mask any sensitive values using approved masking (for example ****8). Ensure there is a mechanism to enable or disable verbose logging via configuration, environment variable, or runtime flags, with verbose logging disabled by default in production. Balance debugging needs with performance considerations; implement rate limiting, log rotation, and non-blocking logging where appropriate. Include tests that verify that debug logging is emitted when enabled and that sensitive data is properly redacted.

- Flag control: Introduce a central configuration flag (e.g., ENABLE_VERBOSE_LOGGING) to toggle debug logging at runtime or deployment time. Default to disabled in production.

- Performance safeguards: Ensure verbose logging does not significantly degrade performance. Use asynchronous or buffered logging where feasible; cap log volume per request; implement log rotation and clustering-friendly patterns.

- Testing requirements: Add unit tests that confirm:
  - Debug logging is emitted when verbose mode is enabled.
  - Secrets/sensitive data are redacted in all logs.
  - Logging can be toggled off without impacting normal behavior.
  - Logging format remains consistent (structure/fields present).

This new requirement should be integrated into the existing "Logging Standards" section and reflected in all relevant development guidelines and test plans.

---

### **CRITICAL SAFETY AND OPERATIONS NOTES**

- Edge cases to handle explicitly: If an edit could affect protected sections or authentication code, stop and require explicit user confirmation before proceeding.
- If tests fail after making a requested change, revert the change locally, record the failure in the edit log, and present options to the user.
- Literal Command Execution Policy: When the user gives an instruction, follow it exactly as written. Do not simulate, anticipate, or add extra actions, output, or commentary. Do not perform any step not explicitly requested. Do not omit or alter the literal meaning of the user's command. Only do what is asked—nothing more, nothing less.

- Pre-edit commands (Edits and Safety Protocol): Always use these commands before ANY edit operation (not just major edits): Start edit session, Capture snapshot, Log edits, Validate. Mandatory: Edit tracking is required for every code, config, or documentation change—no exceptions.

- Button Requirement: For any suggested action, Copilot must provide a clickable button that allows the user to carry out the action directly.

- Patching Instruction: Before making any code edit, analyze the exact code block, ideate the intended edit, double-check syntax, compare proposed edits to the original, and apply only if it matches and does not corrupt unrelated code.

- Unlockingai.docs: Entry & History Safety (NO SECRETS): Secret-scan before commit, mask secrets, edit tracking, commit-only masked artifacts, verification, incident response. Use the edit tracking system for all changes touching this file or documentation.

- Edit Tracking & Rollback System example included above.

---

### **📋 Implementation Checklist (Updated)**

- [ ] Add explicit maximum debug logging requirement to Logging Standards
- [ ] Ensure runtime toggle for verbose logging is defined and used
- [ ] Add tests for debug logging behavior and redaction
- [ ] Review protected sections before applying edits
- [ ] Maintain edit tracking for all changes
- [ ] Keep secret-scan masking workflow intact for any document changes
- [ ] Ensure format remains consistent with the provided template


### 🛠️ EDIT SAFETY PROTOCOL (pre-edit commands)
```bash
# ALWAYS use these commands before ANY edit operation (not just major edits):
# Terminal profiles auto-activate .venv - use simplified commands:
1. Start edit session: python3 -c "from utils.edit_tracker import start_edit_session; start_edit_session('description')"
2. Capture snapshot: python3 -c "from utils.edit_tracker import capture_snapshot; capture_snapshot('file_path')" 
3. Log edits: python3 -c "from utils.edit_tracker import log_edit; log_edit(...)"
4. Validate: python3 -c "from utils.edit_tracker import validate_edit; validate_edit('edit_id', 'status')"
```

**MANDATORY:** Edit tracking is required for every code, config, or documentation change—no exceptions.

### BUTTON REQUIREMENT
For any suggested action, Copilot must provide a clickable button that allows the user to carry out the action directly.

### PATCHING INSTRUCTION
Before making any code edit, Copilot must:
1. Analyze the exact code block requiring changes.
2. Ideate and prepare the intended edit.
3. Doublecheck syntax and indentation.
4. Compare the proposed edit against the original code to ensure only the intended change is made.
5. Apply the edit only if it matches the intended change and does not corrupt or remove unrelated code.

### How Copilot Should Use This Library
1. Treat `unlockingai.docs` at the project root as a primary reference for diagnosis, technical questions, and historical context.
2. Use the indexed folder structure (by subsystem/topic) to make queries direct and efficient.
3. Cross-reference bug reports, closure summaries, and implementation guides from this library when troubleshooting or proposing solutions.
4. Leverage chat summaries and technical docs to provide context-aware, historically informed answers and fixes.

### 🔐 unlockingai.docs: Entry & History Safety (NO SECRETS)
All additions or updates to `unlockingai.docs` MUST follow these rules to prevent secrets from being inserted into the document library or its history:

1. Secret-scan before commit: run the project's secret-scan utility (or an approved equivalent) against any file intended for `unlockingai.docs`. The scan must detect common token patterns (API keys, session keys, tokens, `AstraCS:`, `AIzaSy`, `sk-`/`sk_`, `ASSEMBLY_AI_API_KEY`, `ASTRA_DB_TOKEN`, etc.).

2. Mask found values: any matched secret MUST be replaced with the mask string `****8` in the content that will be committed to `unlockingai.docs` (do not leave raw tokens). Do not commit the unmasked original file into `unlockingai.docs`.

3. Edit tracking and snapshot: start an edit session and capture a snapshot before making any change that will touch `unlockingai.docs` (see Edit Safety Protocol). Log the intent and include which files were scanned and which values (masked) were replaced.

4. Commit-only masked artifacts: only commit masked versions of files into `unlockingai.docs`. If an unmasked sensitive file exists elsewhere in the repo (e.g., app `.env`), do not copy it into `unlockingai.docs`.

5. Historical secrets handling: if a secret is discovered in existing history for `unlockingai.docs`, escalate: create an audit entry noting the commit(s) and backup path, then follow the documented history-remediation workflow (git-filter-repo replace-text with a verified replace-map, backup mirror, verify, and force-push) under an explicit edit session. Do not attempt history rewriting without capturing backups and logging the edit session.

6. Verification: after commit and push, run the secret-scan again on the remote mirror (or local refs) to confirm no secrets remain in HEAD or `unlockingai.docs` history. Record verification output in the edit log.

7. Incident response: any confirmed exposure of active credentials requires immediate rotation of the exposed credentials and an entry in the audit log describing the rotation and remediation steps.

### Edit Tracking & Rollback System (usage example)
```python
# Start edit session
session_id = start_edit_session("JWT SSO implementation")
capture_snapshot("app/routes/auth.py")

# Log edit with full context
edit_id = log_edit(
    file_path="app/routes/auth.py",
    operation_type="replace",
    content_removed="[exact old content]",
    content_added="[exact new content]", 
    edit_intent="Add JWT token generation for SSO",
    copilot_request_id="REQ_20250812_143022_001"
)

# Validate and close session
validate_edit(edit_id, "success")
end_edit_session()
```

