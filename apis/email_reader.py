# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
from django.conf import settings
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import os
import zipfile
import logging
import io
from django.http.response import HttpResponse
import fitz
import re
from pdfminer.high_level import extract_text
import subprocess
import docx2txt
import nltk
from apis.models import CandidateDetails                        
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (api_view,
                                       parser_classes,
                                       permission_classes,
                                       renderer_classes
                                       )
from rest_framework.parsers import JSONParser
from rest_framework.response import Response                  
from django.contrib.sites.shortcuts import get_current_site        
import sys
from nltk.tokenize import word_tokenize
from utils.common_functions import token_required
import re
import csv
from httplib2 import Http
import oauth2client
import google_auth_oauthlib
from oauth2client.tools import run_flow
from datetime import date, timedelta
from django.core.mail import (send_mail,
                              EmailMultiAlternatives,
                              EmailMessage
                              )
logger = logging.getLogger(__name__)
                    

nltk.download('stopwords') 
nltk.download('punkt') 
nltk.download('averaged_perceptron_tagger') 
nltk.download('maxent_ne_chunker') 
nltk.download('words')
                    
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

'''extract text from resume files'''
def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

def doc_to_text_catdoc(file_path):
    try:
        process = subprocess.Popen(
            ['catdoc', '-w', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (
        FileNotFoundError,
        ValueError,
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
    ) as err:
        return (None, str(err))
    else:
        stdout, stderr = process.communicate()
    
    return (stdout.strip(), stderr.strip())
'''extract text from resume files ends'''

@token_required
@parser_classes([JSONParser])
@api_view(['GET'])
def getEmails(request):
    current_site = get_current_site(request)
    scheme= 'https://' if request.is_secure() else 'http://'
    CREDENTIAL = settings.CREDENTIAL_FILE_PATH[0]
    TOKEN = settings.TOKEN_FILE_PATH[0]
    results = []
    creds = None
    
    if os.path.exists(TOKEN):
        with open(TOKEN, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIAL, SCOPES)
            creds = flow.run_local_server(host=settings.HOST, port=8080)

        with open(TOKEN, 'wb') as token:
            pickle.dump(creds, token)
            
    service = build('gmail', 'v1', credentials=creds)
    
    label_id_one = 'INBOX'
    label_id_two = 'UNREAD'
    
    today = date.today()
    todate = today + timedelta(1)
    yesterday = today - timedelta(1)
    
    # Dates have to formatted in YYYY/MM/DD format for gmail
    query = "after: {0}".format(yesterday.strftime('%Y/%m/%d'))
    
    data = 'in:inbox label:unread'+' '+query
    result = service.users().messages().list(userId='me', maxResults=600, q='in:inbox label:unread').execute()
    logged = 'Scheduler run on {cur_date} and Total number of mails read :{count} .'.format(cur_date=todate,
                                                                                    count=result.get('resultSizeEstimate'))
    logger.info(logged)
    
    messages = result.get('messages')
    if messages:
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            try:
                for part in txt['payload']['parts']:
                    if part['filename']:
                        user_json = {}
                        
                        if 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            att_id = part['body']['attachmentId']
                            att = service.users().messages().attachments().get(userId='me', messageId=msg['id'],id=att_id).execute()
                            data = att['data']
                        
                        subject = sender_email = receiver_email = None
                        
                        payload = txt['payload']
                        headers = payload['headers']

                        for d in headers:
                            if d['name'] == 'Subject':
                                subject = d['value']
                            if d['name'] == 'From':
                                sender_email = d['value']
                            if d["name"] == "To":
                                receiver_email = d["value"]
                                
                        '''To get the mail from email address'''
                        try:
                            s1 = sender_email.find("<") + len("<")
                            e1 = sender_email.find(">")
                            from_email = sender_email[s1:e1]
                        except:
                            from_email = None
                        
                        try:
                            s2 = receiver_email.find("<") + len("<")
                            e2 = receiver_email.find(">")
                            to_email = receiver_email[s2:e2]
                        except:
                            to_email = None
                        '''To get the prefix from email before @'''
                        try:
                            start = sender_email.find("<") + len("<")
                            end = sender_email.find("@")
                            sender_email_name = sender_email[start:end]
                        except:
                            sender_email_name = None
                        
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        file_names = sender_email_name+'_'+part['filename']
                        path = '{media_root}/{folder_name}/{file_name}'.format(
                                                media_root=settings.MEDIA_ROOT,
                                                folder_name='mail_attachments',
                                                file_name=file_names
                                            )
                        with open(path, 'wb') as f:
                            f.write(file_data)
                        
                        try: 
                            candidate_name = get_name(request, path)   
                        except Exception as e:
                            candidate_name = None
                        try: 
                            candidate_email = get_email(request, path)   
                        except Exception as e:
                            candidate_email = None
                        try: 
                            candidate_number = get_number(request, path)   
                        except Exception as e:
                            candidate_number = None
                            
                        resume_url = 'mail_attachments/'+str(file_names)
                        if candidate_name and candidate_email and candidate_number:
                            CandidateDetails.objects.create(name=candidate_name,
                                                email=candidate_email,
                                                mobile_no=candidate_number,
                                                to_email=to_email,
                                                from_email=from_email,
                                                email_subject=subject,
                                                resume=resume_url)
                        user_json['name'] = candidate_name
                        user_json['email'] = candidate_email
                        user_json['mobile_no'] = candidate_number
                        user_json['email_subject'] = subject
                        user_json['from_email'] = from_email
                        user_json['to_email'] = to_email
                        user_json['resume_path'] = scheme + str(current_site) + settings.MEDIA_URL + resume_url
                        results.append(user_json)
                        
                        service.users().messages().modify(userId='me', id=msg['id'],body={ 'removeLabelIds': ['UNREAD']}).execute() 
            
            except Exception as e:
                pass
        if settings.SEND_MAIL_ALL_PLACE:
            subject = "Mail Agent Cron Job Status"
            from_email, to = settings.ADMIN_EMAIL, ['manish.kumar@baryons.net', 'kshitij@baryons.net', 'shweta@baryons.net']
            msg = logged+'. Kindly login to Admin portal in order to check the list of Resume.'
            email = EmailMultiAlternatives(subject,
                                            msg,
                                            from_email,
                                            to)
            email.content_subtype = 'html'
            email.send()
        
    return Response(results)

'''Extracting Name from resumes'''
def get_name(request, path):
    name, extension = os.path.splitext(path)
    if extension == '.pdf':
        txt = extract_text(path)
    elif extension == '.docx':
        txt = extract_text_from_docx(path)
    elif extension == '.doc':
        txt = doc_to_text_catdoc(path)
        
    person_names = []
    if txt:
        for sent in nltk.sent_tokenize(str(txt)):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                    person_names.append(
                        ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                    )
        if person_names:
            return person_names[0]
'''Extracting Name from resumes --Ends'''
        
'''Extracting email addresses from resumes'''
def get_email(request, path):
    EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
    name, extension = os.path.splitext(path)
    if extension == '.pdf':
        text = extract_text(path)
    elif extension == '.docx':
        text = extract_text_from_docx(path)
    elif extension == '.doc':
        text = doc_to_text_catdoc(path)
    emails = re.findall(EMAIL_REG, str(text))
    return emails[0]
'''Extracting email addresses from resumes --Ends'''
    
'''Extracting number from resumes'''
def get_number(request, path):
    PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
    name, extension = os.path.splitext(path)
    if extension == '.pdf':
        text = extract_text(path)
    elif extension == '.docx':
        text = extract_text_from_docx(path)
    elif extension == '.doc':
        text = doc_to_text_catdoc(path)
    number = re.findall(PHONE_REG, str(text))
    return number[0]
'''Extracting number from resumes --Ends'''
