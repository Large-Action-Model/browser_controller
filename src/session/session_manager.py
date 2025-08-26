"""
Session Manager for tracking and managing browser sessions.

This class provides session lifecycle management, monitoring,
and resource cleanup for the Browser Controller.
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from ..utils import get_logger
from ..types import SessionMetadata
from .browser_session import BrowserSession


@dataclass
class SessionStats:
    """Statistics for session tracking."""
    total_sessions: int = 0
    active_sessions: int = 0
    closed_sessions: int = 0
    failed_sessions: int = 0
    average_duration: float = 0.0
    longest_session: float = 0.0
    shortest_session: float = float('inf')
    total_duration: float = 0.0


class SessionManager:
    """
    Manager for browser sessions with monitoring and cleanup capabilities.
    
    This class provides:
    - Session registration and tracking
    - Session lifecycle monitoring
    - Resource cleanup and management
    - Session statistics and metrics
    - Automatic cleanup of stale sessions
    """
    
    def __init__(self, max_sessions: int = 10, session_timeout: float = 300.0):
        """
        Initialize session manager.
        
        Args:
            max_sessions: Maximum number of concurrent sessions
            session_timeout: Session timeout in seconds
        """
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        
        # Session tracking
        self._sessions: Dict[str, BrowserSession] = {}
        self._session_metadata: Dict[str, SessionMetadata] = {}
        self._session_start_times: Dict[str, float] = {}
        self._session_end_times: Dict[str, float] = {}
        
        # Statistics
        self._stats = SessionStats()
        
        # Logger
        self.logger = get_logger("SessionManager")
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
        
        self.logger.info("Session Manager initialized", {
            "max_sessions": max_sessions,
            "session_timeout": session_timeout
        })
    
    async def register_session(self, session: BrowserSession) -> bool:
        """
        Register a new session.
        
        Args:
            session: Browser session to register
            
        Returns:
            True if registered successfully, False if limit exceeded
        """
        # Check session limit
        if len(self._sessions) >= self.max_sessions:
            self.logger.warning("Session limit reached", {
                "current_sessions": len(self._sessions),
                "max_sessions": self.max_sessions,
                "session_id": session.session_id
            })
            return False
        
        # Register session
        self._sessions[session.session_id] = session
        self._session_start_times[session.session_id] = time.time()
        
        # Create metadata
        metadata = SessionMetadata(
            session_id=session.session_id,
            browser_type=session.config.browser_type,
            created_at=time.time(),
            current_url=None,
            title=None,
            user_agent=session.config.user_agent,
            cookies=[],
            local_storage={},
            session_storage={}
        )
        
        self._session_metadata[session.session_id] = metadata
        
        # Update statistics
        self._stats.total_sessions += 1
        self._stats.active_sessions += 1
        
        self.logger.info("Session registered", {
            "session_id": session.session_id,
            "total_active": len(self._sessions),
            "browser_type": session.config.browser_type.value if hasattr(session.config.browser_type, 'value') else str(session.config.browser_type)
        })
        
        return True
    
    async def unregister_session(self, session_id: str) -> bool:
        """
        Unregister and cleanup session.
        
        Args:
            session_id: Session ID to unregister
            
        Returns:
            True if unregistered successfully
        """
        if session_id not in self._sessions:
            self.logger.warning("Session not found for unregistration", {"session_id": session_id})
            return False
        
        # Record end time
        self._session_end_times[session_id] = time.time()
        
        # Calculate session duration
        if session_id in self._session_start_times:
            duration = self._session_end_times[session_id] - self._session_start_times[session_id]
            
            # Update statistics
            self._stats.total_duration += duration
            self._stats.longest_session = max(self._stats.longest_session, duration)
            if self._stats.shortest_session == float('inf'):
                self._stats.shortest_session = duration
            else:
                self._stats.shortest_session = min(self._stats.shortest_session, duration)
            
            if self._stats.closed_sessions > 0:
                self._stats.average_duration = self._stats.total_duration / self._stats.closed_sessions
        
        # Remove session
        del self._sessions[session_id]
        
        # Update statistics
        self._stats.active_sessions -= 1
        self._stats.closed_sessions += 1
        
        self.logger.info("Session unregistered", {
            "session_id": session_id,
            "duration": duration if 'duration' in locals() else None,
            "remaining_active": len(self._sessions)
        })
        
        return True
    
    async def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    async def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self._sessions.keys())
    
    async def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self._sessions)
    
    async def get_session_metadata(self, session_id: str) -> Optional[SessionMetadata]:
        """Get session metadata."""
        return self._session_metadata.get(session_id)
    
    async def update_session_metadata(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update session metadata."""
        if session_id not in self._session_metadata:
            return False
        
        metadata = self._session_metadata[session_id]
        
        # Update fields if provided
        if 'current_url' in updates:
            metadata.current_url = updates['current_url']
        if 'title' in updates:
            metadata.title = updates['title']
        if 'cookies' in updates:
            metadata.cookies = updates['cookies']
        if 'local_storage' in updates:
            metadata.local_storage = updates['local_storage']
        if 'session_storage' in updates:
            metadata.session_storage = updates['session_storage']
        
        self.logger.debug("Session metadata updated", {
            "session_id": session_id,
            "updated_fields": list(updates.keys())
        })
        
        return True
    
    async def get_session_stats(self) -> SessionStats:
        """Get session statistics."""
        # Update current statistics
        self._stats.active_sessions = len(self._sessions)
        return self._stats
    
    async def cleanup_stale_sessions(self) -> int:
        """
        Cleanup stale sessions that have exceeded timeout.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        stale_sessions = []
        
        for session_id, session in self._sessions.items():
            start_time = self._session_start_times.get(session_id, current_time)
            session_age = current_time - start_time
            
            if session_age > self.session_timeout:
                stale_sessions.append(session_id)
        
        cleanup_count = 0
        for session_id in stale_sessions:
            try:
                session = self._sessions.get(session_id)
                if session:
                    await session.close()
                await self.unregister_session(session_id)
                cleanup_count += 1
                
                self.logger.info("Cleaned up stale session", {
                    "session_id": session_id,
                    "age_seconds": current_time - self._session_start_times.get(session_id, current_time)
                })
                
            except Exception as e:
                self.logger.error("Error cleaning up stale session", {
                    "session_id": session_id
                }, exception=e)
        
        if cleanup_count > 0:
            self.logger.info("Stale session cleanup completed", {
                "cleaned_count": cleanup_count,
                "remaining_active": len(self._sessions)
            })
        
        return cleanup_count
    
    async def close_all_sessions(self) -> int:
        """
        Close all active sessions.
        
        Returns:
            Number of sessions closed
        """
        session_ids = list(self._sessions.keys())
        closed_count = 0
        
        for session_id in session_ids:
            try:
                session = self._sessions.get(session_id)
                if session:
                    await session.close()
                await self.unregister_session(session_id)
                closed_count += 1
            except Exception as e:
                self.logger.error("Error closing session", {"session_id": session_id}, exception=e)
        
        self.logger.info("All sessions closed", {"closed_count": closed_count})
        return closed_count
    
    def _start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(60)  # Run cleanup every minute
                    await self.cleanup_stale_sessions()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error("Error in cleanup loop", exception=e)
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def shutdown(self) -> None:
        """Shutdown session manager."""
        self.logger.info("Shutting down session manager")
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all sessions
        await self.close_all_sessions()
        
        # Log final statistics
        final_stats = await self.get_session_stats()
        self.logger.info("Session manager shutdown complete", {
            "total_sessions": final_stats.total_sessions,
            "average_duration": final_stats.average_duration,
            "longest_session": final_stats.longest_session
        })
    
    @asynccontextmanager
    async def session_context(self, session: BrowserSession):
        """Context manager for automatic session lifecycle management."""
        try:
            # Register session
            if not await self.register_session(session):
                raise RuntimeError("Failed to register session - limit exceeded")
            
            yield session
            
        finally:
            # Always cleanup session
            await self.unregister_session(session.session_id)
    
    def __del__(self):
        """Destructor to cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            try:
                self._cleanup_task.cancel()
            except:
                pass
