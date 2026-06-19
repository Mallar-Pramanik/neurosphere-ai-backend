"""
Google API Service - Integration with Gmail, Drive, and Cloud NLP
"""

import logging
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
# from google.cloud import language_v1
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import json
import os

from config import settings

logger = logging.getLogger(__name__)

class GoogleAPIService:
    """Service for Google APIs integration"""
    
    def __init__(self):
        self.gmail_service = None
        self.drive_service = None
        self.nlp_client = None
        self.is_initialized = False
        self.user_credentials = {}
    
    def initialize(self):
        """Initialize Google API services"""
        try:
            logger.info("Initializing Google APIs...")
            
            # Check if credentials file exists
            if not os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
                logger.warning(f"Google credentials not found at {settings.GOOGLE_CREDENTIALS_PATH}")
                logger.info("To enable Google APIs:")
                logger.info("1. Download credentials from Google Cloud Console")
                logger.info("2. Place in: " + settings.GOOGLE_CREDENTIALS_PATH)
                return
            
            # Initialize services based on available credentials
            self._init_gmail_service()
            self._init_drive_service()
            self._init_nlp_service()
            
            self.is_initialized = True
            logger.info("✅ Google APIs initialized successfully")
            
        except Exception as e:
            logger.warning(f"Google APIs initialization warning: {str(e)}")
            self.is_initialized = False
    
    def _init_gmail_service(self):
        """Initialize Gmail service"""
        try:
            # Load credentials
            credentials = self._get_credentials(settings.GOOGLE_GMAIL_SCOPES)
            if credentials:
                self.gmail_service = build('gmail', 'v1', credentials=credentials)
                logger.info("✅ Gmail service initialized")
        except Exception as e:
            logger.warning(f"Gmail service init error: {str(e)}")
    
    def _init_drive_service(self):
        """Initialize Google Drive service"""
        try:
            credentials = self._get_credentials(settings.GOOGLE_DRIVE_SCOPES)
            if credentials:
                self.drive_service = build('drive', 'v3', credentials=credentials)
                logger.info("✅ Google Drive service initialized")
        except Exception as e:
            logger.warning(f"Drive service init error: {str(e)}")
    
    def _init_nlp_service(self):
        """Initialize Google Cloud NLP service"""
        try:
            # Create NLP client using service account credentials
            if os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
                self.nlp_client = language_v1.LanguageServiceClient()
                logger.info("✅ Google Cloud NLP service initialized")
        except Exception as e:
            logger.warning(f"NLP service init error: {str(e)}")
    
    def _get_credentials(self, scopes: List[str]):
        """Get Google API credentials"""
        try:
            if not os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
                return None
            
            # Try loading as service account
            try:
                credentials = ServiceAccountCredentials.from_service_account_file(
                    settings.GOOGLE_CREDENTIALS_PATH,
                    scopes=scopes
                )
                return credentials
            except:
                # Try loading as OAuth credentials
                credentials = Credentials.from_authorized_user_file(
                    settings.GOOGLE_CREDENTIALS_PATH,
                    scopes
                )
                return credentials
        except Exception as e:
            logger.warning(f"Credential loading error: {str(e)}")
            return None
    
    def get_emails(
        self,
        user_id: int,
        max_results: int = 10,
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get emails from Gmail
        
        Args:
            user_id: User ID (for logging)
            max_results: Maximum emails to fetch
            query: Gmail search query
        
        Returns:
            List of emails
        """
        if not self.gmail_service:
            logger.warning("Gmail service not initialized")
            return []
        
        try:
            logger.info(f"Fetching emails for user {user_id}")
            
            # Get message IDs
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            # Fetch full message details
            for message in messages:
                try:
                    msg = self.gmail_service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    headers = msg['payload']['headers']
                    email_data = {
                        'id': msg['id'],
                        'from_email': next(
                            (h['value'] for h in headers if h['name'] == 'From'),
                            'Unknown'
                        ),
                        'subject': next(
                            (h['value'] for h in headers if h['name'] == 'Subject'),
                            '(No Subject)'
                        ),
                        'date': next(
                            (h['value'] for h in headers if h['name'] == 'Date'),
                            ''
                        ),
                    }
                    email_list.append(email_data)
                except Exception as e:
                    logger.warning(f"Error fetching message details: {str(e)}")
            
            logger.info(f"✅ Fetched {len(email_list)} emails")
            return email_list
            
        except HttpError as error:
            logger.error(f'Gmail API error: {error}')
            return []
        except Exception as e:
            logger.error(f"Error getting emails: {str(e)}")
            return []
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        user_id: int,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Send email via Gmail
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            user_id: User ID (for logging)
            cc: CC recipients
            bcc: BCC recipients
        
        Returns:
            Message ID or None
        """
        if not self.gmail_service:
            logger.warning("Gmail service not initialized")
            return None
        
        try:
            logger.info(f"Sending email from user {user_id} to {to}")
            
            import base64
            from email.mime.text import MIMEText
            
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_message = {'raw': raw_message}
            result = self.gmail_service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            logger.info(f"✅ Email sent: {result['id']}")
            return result['id']
            
        except HttpError as error:
            logger.error(f'Gmail API error: {error}')
            return None
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return None
    
    def get_drive_files(
        self,
        user_id: int,
        max_results: int = 10,
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get files from Google Drive
        
        Args:
            user_id: User ID (for logging)
            max_results: Maximum files to fetch
            query: Drive search query
        
        Returns:
            List of files
        """
        if not self.drive_service:
            logger.warning("Drive service not initialized")
            return []
        
        try:
            logger.info(f"Fetching Drive files for user {user_id}")
            
            results = self.drive_service.files().list(
                pageSize=max_results,
                fields='files(id, name, mimeType, size, createdTime, modifiedTime, owners)',
                q=query
            ).execute()
            
            files = results.get('files', [])
            
            file_list = []
            for file in files:
                owner = file.get('owners', [{}])[0]
                file_data = {
                    'id': file['id'],
                    'name': file.get('name', 'Unknown'),
                    'mime_type': file.get('mimeType', ''),
                    'size': file.get('size', 0),
                    'created_time': file.get('createdTime', ''),
                    'modified_time': file.get('modifiedTime', ''),
                    'owner': owner.get('displayName', 'Unknown'),
                }
                file_list.append(file_data)
            
            logger.info(f"✅ Fetched {len(file_list)} Drive files")
            return file_list
            
        except HttpError as error:
            logger.error(f'Drive API error: {error}')
            return []
        except Exception as e:
            logger.error(f"Error getting Drive files: {str(e)}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze text sentiment using Google Cloud NLP
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment analysis results
        """
        if not self.nlp_client:
            logger.warning("NLP service not initialized")
            return {"error": "NLP service not available"}
        
        try:
            logger.info("Analyzing sentiment...")
            
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            sentiment = self.nlp_client.analyze_sentiment(
                request={'document': document}
            )
            
            document_sentiment = sentiment.document_sentiment
            
            result = {
                'score': document_sentiment.score,  # -1.0 to 1.0
                'magnitude': document_sentiment.magnitude,
                'sentences': []
            }
            
            # Analyze each sentence
            for sentence in sentiment.sentences:
                result['sentences'].append({
                    'text': sentence.text.content,
                    'score': sentence.sentiment.score,
                    'magnitude': sentence.sentiment.magnitude
                })
            
            logger.info("✅ Sentiment analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"error": str(e)}
    
    def analyze_entities(self, text: str) -> Dict[str, Any]:
        """
        Analyze entities in text
        
        Args:
            text: Text to analyze
        
        Returns:
            Entity analysis results
        """
        if not self.nlp_client:
            logger.warning("NLP service not initialized")
            return {"error": "NLP service not available"}
        
        try:
            logger.info("Analyzing entities...")
            
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            response = self.nlp_client.analyze_entities(
                request={'document': document}
            )
            
            entities = []
            for entity in response.entities:
                entities.append({
                    'name': entity.name,
                    'type': language_v1.Entity.Type(entity.type_).name,
                    'salience': entity.salience,
                })
            
            logger.info(f"✅ Found {len(entities)} entities")
            return {'entities': entities}
            
        except Exception as e:
            logger.error(f"Entity analysis error: {str(e)}")
            return {"error": str(e)}
    
    def analyze_syntax(self, text: str) -> Dict[str, Any]:
        """
        Analyze syntax of text
        
        Args:
            text: Text to analyze
        
        Returns:
            Syntax analysis results
        """
        if not self.nlp_client:
            logger.warning("NLP service not initialized")
            return {"error": "NLP service not available"}
        
        try:
            logger.info("Analyzing syntax...")
            
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            response = self.nlp_client.analyze_syntax(
                request={'document': document}
            )
            
            tokens = []
            for token in response.tokens:
                tokens.append({
                    'text': token.text.content,
                    'part_of_speech': language_v1.PartOfSpeech.Tag(
                        token.part_of_speech.tag
                    ).name,
                })
            
            logger.info(f"✅ Analyzed {len(tokens)} tokens")
            return {'tokens': tokens}
            
        except Exception as e:
            logger.error(f"Syntax analysis error: {str(e)}")
            return {"error": str(e)}
