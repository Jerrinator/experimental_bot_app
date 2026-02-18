# utils/edit_tracker.py
# Comprehensive edit tracking system for preventing file corruption and enabling precise rollbacks

import logging
import json
import os
import hashlib
import difflib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler

@dataclass
class EditRecord:
    """Detailed record of a single code edit operation"""
    timestamp: str
    file_path: str
    operation_type: str  # 'replace', 'insert', 'delete', 'full_rewrite'
    line_range_before: Tuple[int, int]  # (start_line, end_line) before edit
    line_range_after: Tuple[int, int]   # (start_line, end_line) after edit
    content_removed: str
    content_added: str
    edit_intent: str
    file_hash_before: str
    file_hash_after: str
    edit_id: str
    session_id: str
    copilot_request_id: Optional[str] = None
    validation_status: str = "pending"  # pending, success, failed, corrupted
    rollback_available: bool = True

class EditTracker:
    """
    🔒 CUSTOM_PROMPT_PREFIX - RESPECT_PROTECTED_SECTIONS
    This edit tracking system is critical for preventing file corruption
    and enabling precise rollbacks. Any modifications must maintain
    the complete audit trail and rollback capabilities.
    END_CUSTOM_PROMPT_PREFIX
    """
    
    def __init__(self, logs_dir: str = "./logs"):
        self.logs_dir = logs_dir
        os.makedirs(logs_dir, exist_ok=True)
        
        # Set up specialized edit logging
        self.edit_logger = logging.getLogger("EditTracker")
        self.edit_logger.setLevel(logging.DEBUG)
        
        # Rotating file handler for edit logs (larger files for detailed tracking)
        edit_handler = RotatingFileHandler(
            f'{logs_dir}/edit_tracker.log',
            maxBytes=5*1024*1024,  # 5MB per file for detailed edit history
            backupCount=10,        # Keep 10 files = 50MB total
            encoding='utf-8'
        )
        
        # Custom formatter for edit tracking
        edit_formatter = logging.Formatter(
            '%(asctime)s [EDIT_%(levelname)s] %(message)s'
        )
        edit_handler.setFormatter(edit_formatter)
        self.edit_logger.addHandler(edit_handler)
        
        # In-memory session tracking
        self.current_session_id = self._generate_session_id()
        self.session_edits: List[EditRecord] = []
        self.file_snapshots: Dict[str, str] = {}
        
        self.edit_logger.info(f"=== EDIT TRACKING SESSION STARTED: {self.current_session_id} ===")
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"SESSION_{timestamp}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
    
    def _generate_edit_id(self) -> str:
        """Generate unique edit identifier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"EDIT_{timestamp}_{len(self.session_edits):04d}"
    
    def _calculate_file_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of file content for integrity verification"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _read_file_safely(self, file_path: str) -> Optional[str]:
        """Safely read file content with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.edit_logger.error(f"Failed to read file {file_path}: {str(e)}")
            return None
    
    def _get_line_range_from_content(self, full_content: str, target_content: str) -> Tuple[int, int]:
        """Determine line range for specific content within full file"""
        lines = full_content.split('\n')
        target_lines = target_content.split('\n')
        
        # Find the starting line
        for i in range(len(lines) - len(target_lines) + 1):
            if lines[i:i+len(target_lines)] == target_lines:
                return (i + 1, i + len(target_lines))  # 1-indexed
        
        return (1, len(lines))  # Fallback to entire file
    
    def start_edit_session(self, description: str = "Code edit session") -> str:
        """Start a new edit session with description"""
        self.current_session_id = self._generate_session_id()
        self.session_edits = []
        self.file_snapshots = {}
        
        session_info = {
            "session_id": self.current_session_id,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "edit_count": 0
        }
        
        self.edit_logger.info(f"=== EDIT SESSION START ===")
        self.edit_logger.info(f"SESSION_INFO: {json.dumps(session_info, indent=2)}")
        
        return self.current_session_id
    
    def capture_file_snapshot(self, file_path: str) -> bool:
        """Capture pre-edit snapshot of file for rollback capability"""
        content = self._read_file_safely(file_path)
        if content is not None:
            self.file_snapshots[file_path] = content
            file_hash = self._calculate_file_hash(content)
            
            snapshot_info = {
                "file_path": file_path,
                "snapshot_time": datetime.now().isoformat(),
                "file_hash": file_hash,
                "line_count": len(content.split('\n'))
            }
            
            self.edit_logger.info(f"FILE_SNAPSHOT_CAPTURED: {json.dumps(snapshot_info, indent=2)}")
            return True
        return False
    
    def log_edit_operation(self, 
                          file_path: str,
                          operation_type: str,
                          content_removed: str,
                          content_added: str,
                          edit_intent: str,
                          copilot_request_id: Optional[str] = None) -> str:
        """
        Log a detailed edit operation with full context for rollback capability
        
        Args:
            file_path: Path to the file being edited
            operation_type: Type of operation (replace, insert, delete, full_rewrite)
            content_removed: Exact content that was removed
            content_added: Exact content that was added
            edit_intent: Human-readable description of why this edit was made
            copilot_request_id: Optional Copilot request identifier
            
        Returns:
            edit_id: Unique identifier for this edit operation
        """
        
        # Generate unique edit ID
        edit_id = self._generate_edit_id()
        
        # Capture file state before and after
        content_before = self.file_snapshots.get(file_path, self._read_file_safely(file_path) or "")
        
        # Calculate file hash before edit
        hash_before = self._calculate_file_hash(content_before)
        
        # Determine line ranges
        if content_removed:
            line_range_before = self._get_line_range_from_content(content_before, content_removed)
        else:
            line_range_before = (1, 1)
        
        # Read file after edit to get updated state
        content_after = self._read_file_safely(file_path) or ""
        hash_after = self._calculate_file_hash(content_after)
        
        if content_added:
            line_range_after = self._get_line_range_from_content(content_after, content_added)
        else:
            line_range_after = line_range_before
        
        # Create edit record
        edit_record = EditRecord(
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            operation_type=operation_type,
            line_range_before=line_range_before,
            line_range_after=line_range_after,
            content_removed=content_removed,
            content_added=content_added,
            edit_intent=edit_intent,
            file_hash_before=hash_before,
            file_hash_after=hash_after,
            edit_id=edit_id,
            session_id=self.current_session_id,
            copilot_request_id=copilot_request_id
        )
        
        # Add to session tracking
        self.session_edits.append(edit_record)
        
        # Log comprehensive edit information
        edit_summary = {
            "edit_id": edit_id,
            "session_id": self.current_session_id,
            "file_path": file_path,
            "operation": operation_type,
            "lines_before": f"{line_range_before[0]}-{line_range_before[1]}",
            "lines_after": f"{line_range_after[0]}-{line_range_after[1]}",
            "intent": edit_intent,
            "hash_before": hash_before,
            "hash_after": hash_after,
            "copilot_request": copilot_request_id
        }
        
        self.edit_logger.info(f"=== EDIT OPERATION LOGGED ===")
        self.edit_logger.info(f"EDIT_SUMMARY: {json.dumps(edit_summary, indent=2)}")
        
        # Log detailed content changes
        self.edit_logger.info(f"CONTENT_REMOVED_{edit_id}:")
        self.edit_logger.info(f"```\n{content_removed}\n```")
        
        self.edit_logger.info(f"CONTENT_ADDED_{edit_id}:")
        self.edit_logger.info(f"```\n{content_added}\n```")
        
        # Generate and log diff for easy comparison
        if content_removed and content_added:
            diff_lines = list(difflib.unified_diff(
                content_removed.splitlines(keepends=True),
                content_added.splitlines(keepends=True),
                fromfile=f"{file_path} (before)",
                tofile=f"{file_path} (after)",
                lineterm=''
            ))
            
            self.edit_logger.info(f"DIFF_{edit_id}:")
            for line in diff_lines:
                self.edit_logger.info(f"DIFF_LINE: {line.rstrip()}")
        
        return edit_id
    
    def validate_edit_result(self, edit_id: str, validation_status: str, error_details: Optional[str] = None):
        """Update edit record with validation results"""
        for edit_record in self.session_edits:
            if edit_record.edit_id == edit_id:
                edit_record.validation_status = validation_status
                
                validation_info = {
                    "edit_id": edit_id,
                    "validation_status": validation_status,
                    "validation_time": datetime.now().isoformat(),
                    "error_details": error_details
                }
                
                self.edit_logger.info(f"EDIT_VALIDATION: {json.dumps(validation_info, indent=2)}")
                
                if validation_status == "failed" or validation_status == "corrupted":
                    self.edit_logger.error(f"EDIT_FAILED_{edit_id}: {error_details}")
                    self._log_rollback_instructions(edit_id)
                
                break
    
    def _log_rollback_instructions(self, edit_id: str):
        """Log detailed rollback instructions for failed edit"""
        edit_record = next((e for e in self.session_edits if e.edit_id == edit_id), None)
        if not edit_record:
            return
        
        rollback_info = {
            "edit_id": edit_id,
            "rollback_type": "content_restoration",
            "target_file": edit_record.file_path,
            "restore_lines": f"{edit_record.line_range_after[0]}-{edit_record.line_range_after[1]}",
            "restore_content": edit_record.content_removed,
            "remove_content": edit_record.content_added,
            "original_intent": edit_record.edit_intent
        }
        
        self.edit_logger.info(f"=== ROLLBACK INSTRUCTIONS ===")
        self.edit_logger.info(f"ROLLBACK_INFO: {json.dumps(rollback_info, indent=2)}")
        self.edit_logger.info(f"ROLLBACK_RESTORE_CONTENT_{edit_id}:")
        self.edit_logger.info(f"```\n{edit_record.content_removed}\n```")
    
    def generate_session_summary(self) -> Dict:
        """Generate comprehensive summary of edit session"""
        successful_edits = [e for e in self.session_edits if e.validation_status == "success"]
        failed_edits = [e for e in self.session_edits if e.validation_status in ["failed", "corrupted"]]
        
        files_modified = list(set(e.file_path for e in self.session_edits))
        
        summary = {
            "session_id": self.current_session_id,
            "total_edits": len(self.session_edits),
            "successful_edits": len(successful_edits),
            "failed_edits": len(failed_edits),
            "files_modified": files_modified,
            "session_status": "SUCCESS" if len(failed_edits) == 0 else "PARTIAL_FAILURE",
            "end_time": datetime.now().isoformat()
        }
        
        self.edit_logger.info(f"=== EDIT SESSION SUMMARY ===")
        self.edit_logger.info(f"SESSION_SUMMARY: {json.dumps(summary, indent=2)}")
        
        # Log failed edits for analysis
        if failed_edits:
            self.edit_logger.error(f"FAILED_EDITS_ANALYSIS:")
            for edit in failed_edits:
                failure_analysis = {
                    "edit_id": edit.edit_id,
                    "file_path": edit.file_path,
                    "operation_type": edit.operation_type,
                    "edit_intent": edit.edit_intent,
                    "validation_status": edit.validation_status,
                    "lines_affected": f"{edit.line_range_after[0]}-{edit.line_range_after[1]}"
                }
                self.edit_logger.error(f"FAILED_EDIT: {json.dumps(failure_analysis, indent=2)}")
        
        return summary
    
    def end_edit_session(self) -> Dict:
        """End current edit session and generate summary"""
        summary = self.generate_session_summary()
        
        self.edit_logger.info(f"=== EDIT SESSION END: {self.current_session_id} ===")
        
        return summary

# Global edit tracker instance
edit_tracker = EditTracker()

# Convenience functions for easy integration
def start_edit_session(description: str = "Code edit session") -> str:
    """Start a new edit session"""
    return edit_tracker.start_edit_session(description)

def capture_snapshot(file_path: str) -> bool:
    """Capture file snapshot before editing"""
    return edit_tracker.capture_file_snapshot(file_path)

def log_edit(file_path: str, 
            operation_type: str,
            content_removed: str, 
            content_added: str,
            edit_intent: str,
            copilot_request_id: Optional[str] = None) -> str:
    """Log an edit operation with full tracking"""
    return edit_tracker.log_edit_operation(
        file_path, operation_type, content_removed, 
        content_added, edit_intent, copilot_request_id
    )

def validate_edit(edit_id: str, status: str, error_details: Optional[str] = None):
    """Validate edit result"""
    return edit_tracker.validate_edit_result(edit_id, status, error_details)

def end_edit_session() -> Dict:
    """End current edit session"""
    return edit_tracker.end_edit_session()
