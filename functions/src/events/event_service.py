"""Event service for handling event-related operations."""

import os
import uuid
from urllib.parse import urlparse, unquote
from typing import Optional, Dict, Any

from firebase_functions import https_fn
from firebase_admin import storage
from google.cloud.firestore_v1.document import DocumentReference

from ..utils.firestore_client import get_firestore_client
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EventService:
    """Service for handling event-related operations."""
    
    def __init__(self):
        """Initialize the event service."""
        self.db = get_firestore_client()
        self.bucket = storage.bucket()
    
    def duplicate_event_associations(
        self, 
        old_event_ref: DocumentReference, 
        new_event_ref: DocumentReference
    ) -> https_fn.Response:
        """
        Duplicate event associations (questions and media) from old event to new event.
        
        Args:
            old_event_ref: Reference to the original event
            new_event_ref: Reference to the new event
            
        Returns:
            HTTP response indicating success or failure
        """
        if not old_event_ref or not new_event_ref:
            logger.error("Missing event references")
            return https_fn.Response("Missing event references", 400)
        
        try:
            logger.info("Starting event association duplication")
            
            # Verify both events exist
            if not old_event_ref.get().exists:
                logger.error(f"Old event {old_event_ref.id} not found")
                return https_fn.Response("Old event not found", 404)
            
            if not new_event_ref.get().exists:
                logger.error(f"New event {new_event_ref.id} not found")
                return https_fn.Response("New event not found", 404)
            
            old_event_data = old_event_ref.get().to_dict()
            new_event_data = new_event_ref.get().to_dict()
            
            logger.info(f"Duplicating from event '{old_event_data.get('name')}' to '{new_event_data.get('name')}'")
            
            # Duplicate questions
            questions_duplicated = self._duplicate_questions(old_event_ref, new_event_ref)
            
            # Duplicate media
            media_duplicated = self._duplicate_media(old_event_ref, new_event_ref)
            
            logger.info(f"Duplication completed: {questions_duplicated} questions, {media_duplicated} media items")
            return https_fn.Response("Event associations duplicated successfully", 200)
            
        except Exception as e:
            error_msg = f"Error duplicating event associations: {str(e)}"
            logger.error(error_msg)
            return https_fn.Response(error_msg, 500)
    
    def delete_event_associations(
        self, 
        event_ref: DocumentReference, 
        event_data: Dict[str, Any]
    ) -> https_fn.Response:
        """
        Delete all associations (questions and media) for an event.
        
        Args:
            event_ref: Reference to the event to delete associations for
            event_data: Event data dictionary
            
        Returns:
            HTTP response indicating success or failure
        """
        if not event_ref:
            logger.error("Missing event reference")
            return https_fn.Response("Missing event reference", 400)
        
        try:
            event_name = event_data.get("name", "Unknown")
            logger.info(f"Deleting associations for event '{event_name}' (ID: {event_ref.id})")
            
            # Delete questions
            questions_deleted = self._delete_questions(event_ref)
            
            # Delete media
            media_deleted = self._delete_media(event_ref)
            
            logger.info(f"Deletion completed: {questions_deleted} questions, {media_deleted} media items")
            return https_fn.Response("Event associations deleted successfully", 200)
            
        except Exception as e:
            error_msg = f"Error deleting event associations: {str(e)}"
            logger.error(error_msg)
            return https_fn.Response(error_msg, 500)
    
    def _duplicate_questions(
        self, 
        old_event_ref: DocumentReference, 
        new_event_ref: DocumentReference
    ) -> int:
        """Duplicate survey questions from old event to new event."""
        questions = list(
            self.db.collection("event_survey_question")
            .where("event", "==", old_event_ref)
            .stream()
        )
        
        logger.info(f"Found {len(questions)} questions to duplicate")
        duplicated_count = 0
        
        for question in questions:
            try:
                data = question.to_dict()
                logger.info(f"Duplicating question: {question.id} - {data.get('questionText', 'No text')}")
                
                # Update event reference
                data["event"] = new_event_ref
                
                # Create new question
                question_ref = self.db.collection("event_survey_question").document()
                question_ref.set(data)
                
                if question_ref.get().exists:
                    logger.info(f"Question duplicated with ID: {question_ref.id}")
                    duplicated_count += 1
                else:
                    logger.error(f"Failed to duplicate question: {question.id}")
                    
            except Exception as e:
                logger.error(f"Error duplicating question {question.id}: {str(e)}")
        
        return duplicated_count
    
    def _duplicate_media(
        self, 
        old_event_ref: DocumentReference, 
        new_event_ref: DocumentReference
    ) -> int:
        """Duplicate media files from old event to new event."""
        medias = list(
            self.db.collection("event_media")
            .where("event", "==", old_event_ref)
            .stream()
        )
        
        logger.info(f"Found {len(medias)} media items to duplicate")
        duplicated_count = 0
        
        for media in medias:
            try:
                data = media.to_dict()
                original_path = data.get("path")
                
                if not original_path:
                    logger.warning(f"Media {media.id} has no path, skipping")
                    continue
                
                logger.info(f"Duplicating media: {media.id} - {original_path}")
                
                # Duplicate the media file
                new_media_path = self._duplicate_media_file(original_path)
                if not new_media_path:
                    logger.error(f"Failed to duplicate media file: {original_path}")
                    continue
                
                # Update data with new path and event reference
                data["path"] = new_media_path
                data["event"] = new_event_ref
                
                # Create new media document
                media_ref = self.db.collection("event_media").document()
                media_ref.set(data)
                
                if media_ref.get().exists:
                    logger.info(f"Media duplicated with ID: {media_ref.id}")
                    duplicated_count += 1
                else:
                    logger.error(f"Failed to create media document for: {original_path}")
                    
            except Exception as e:
                logger.error(f"Error duplicating media {media.id}: {str(e)}")
        
        return duplicated_count
    
    def _delete_questions(self, event_ref: DocumentReference) -> int:
        """Delete all questions associated with an event."""
        questions = list(
            self.db.collection("event_survey_question")
            .where("event", "==", event_ref)
            .stream()
        )
        
        logger.info(f"Found {len(questions)} questions to delete")
        deleted_count = 0
        
        for question in questions:
            try:
                question_text = question.to_dict().get("questionText", "No text")
                logger.info(f"Deleting question: {question.id} - {question_text}")
                
                question.reference.delete()
                
                if not question.reference.get().exists:
                    logger.info(f"Question {question.id} deleted successfully")
                    deleted_count += 1
                else:
                    logger.error(f"Failed to delete question: {question.id}")
                    
            except Exception as e:
                logger.error(f"Error deleting question {question.id}: {str(e)}")
        
        return deleted_count
    
    def _delete_media(self, event_ref: DocumentReference) -> int:
        """Delete all media files and documents associated with an event."""
        medias = list(
            self.db.collection("event_media")
            .where("event", "==", event_ref)
            .stream()
        )
        
        logger.info(f"Found {len(medias)} media items to delete")
        deleted_count = 0
        
        for media in medias:
            try:
                data = media.to_dict()
                media_path = data.get("path")
                
                logger.info(f"Deleting media: {media.id} - {media_path}")
                
                # Delete the media file from storage
                if media_path and self._delete_media_file(media_path):
                    logger.info(f"Media file deleted: {media_path}")
                else:
                    logger.warning(f"Failed to delete media file: {media_path}")
                
                # Delete the media document
                media.reference.delete()
                
                if not media.reference.get().exists:
                    logger.info(f"Media document {media.id} deleted successfully")
                    deleted_count += 1
                else:
                    logger.error(f"Failed to delete media document: {media.id}")
                    
            except Exception as e:
                logger.error(f"Error deleting media {media.id}: {str(e)}")
        
        return deleted_count
    
    def _duplicate_media_file(self, original_path: str) -> Optional[str]:
        """Duplicate a media file in storage."""
        try:
            logger.info(f"Duplicating media file: {original_path}")
            
            bucket_path = self._extract_file_path(original_path)
            folder_path = self._extract_folder_path(bucket_path)
            filename = self._extract_filename(bucket_path)
            
            new_file_path = f"{folder_path}/duplicated/{uuid.uuid4().hex}/{filename}"
            
            # Download original file
            blob = self.bucket.blob(bucket_path)
            file_contents = blob.download_as_bytes()
            
            # Upload to new location
            new_blob = self.bucket.blob(new_file_path)
            new_blob.upload_from_string(file_contents)
            
            # Generate signed URL (50 years expiration)
            new_url = new_blob.generate_signed_url(expiration=3600 * 24 * 7 * 30 * 12 * 50)
            
            logger.info(f"Media duplicated successfully: {new_url}")
            return new_url
            
        except Exception as e:
            logger.error(f"Error duplicating media file {original_path}: {str(e)}")
            return None
    
    def _delete_media_file(self, path: str) -> bool:
        """Delete a media file from storage."""
        try:
            logger.info(f"Deleting media file: {path}")
            
            bucket_path = self._extract_file_path(path)
            blob = self.bucket.blob(bucket_path)
            blob.delete()
            
            logger.info(f"Media file deleted successfully: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting media file {path}: {str(e)}")
            return False
    
    def _extract_file_path(self, url: str) -> str:
        """Extract file path from storage URL."""
        parsed_url = urlparse(url)
        path_with_encoded_slashes = parsed_url.path.split('/o/')[1]
        file_path = unquote(path_with_encoded_slashes)
        return file_path.split('?')[0]
    
    def _extract_folder_path(self, file_path: str) -> str:
        """Extract folder path from file path."""
        return os.path.dirname(file_path)
    
    def _extract_filename(self, file_path: str) -> str:
        """Extract filename from file path."""
        return os.path.basename(file_path)


# Global event service instance
_event_service: Optional[EventService] = None


def get_event_service() -> EventService:
    """Get or create the event service instance."""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service


def duplicate_event_associations(
    old_event_ref: DocumentReference, 
    new_event_ref: DocumentReference
) -> https_fn.Response:
    """
    Convenience function to duplicate event associations.
    
    Args:
        old_event_ref: Reference to the original event
        new_event_ref: Reference to the new event
        
    Returns:
        HTTP response indicating success or failure
    """
    try:
        event_service = get_event_service()
        return event_service.duplicate_event_associations(old_event_ref, new_event_ref)
    except Exception as e:
        logger.error(f"Error in duplicate_event_associations: {str(e)}")
        return https_fn.Response(f"Error duplicating event associations: {str(e)}", 500)


def delete_event_associations(
    event_ref: DocumentReference, 
    event_data: Dict[str, Any]
) -> https_fn.Response:
    """
    Convenience function to delete event associations.
    
    Args:
        event_ref: Reference to the event
        event_data: Event data dictionary
        
    Returns:
        HTTP response indicating success or failure
    """
    try:
        event_service = get_event_service()
        return event_service.delete_event_associations(event_ref, event_data)
    except Exception as e:
        logger.error(f"Error in delete_event_associations: {str(e)}")
        return https_fn.Response(f"Error deleting event associations: {str(e)}", 500)
