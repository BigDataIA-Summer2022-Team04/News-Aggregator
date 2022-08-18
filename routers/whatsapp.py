import os
import logging
from typing import Union
from fastapi import APIRouter, HTTPException, Response, status, Query, Depends
import schemas
from routers.oaut2 import get_current_user
from twilio.rest import Client 
from custom_functions import logfunc

router = APIRouter(
    prefix="/notify",
    tags=['WhatsApp']
)

@router.post('/send_link', status_code=status.HTTP_200_OK)
async def personalized_section( news_title: str,
                                news_url: str,
                                mobile: str = "8572694998",
                                get_current_user: schemas.ServiceAccount = Depends(get_current_user)
                        ):
    """Gets and prints the spreadsheet's header columns
        http://wa.me/+14155238886?text=join%20needs-those

    Parameters
    ----------
    news_title : str
        News Title
    news_url : str
        News Article URL
    mobile: str
        User mobile number
    
    Returns
    -------
    None
    """
    account_sid = os.environ['TWILIO_SID']
    auth_token  = os.environ['TWILIO_TOKEN']
    twilio_client = Client(account_sid, auth_token )
    
    logging.debug(news_title)
    logging.debug(news_url)
    logging.debug(mobile)
    
    try:
        message = twilio_client.messages.create( 
                                    from_='whatsapp:+14155238886',  
                                    body=f"""
                                    *{news_title}* \n{news_url}
                                    """,
                                    to=f"whatsapp:+1{mobile}")
        logfunc(get_current_user.email, "/NA/whatsApp/send_link", 200)
    except:
        logfunc(get_current_user.email, "/NA/whatsApp/send_link", 400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot Sent Whatsapp Message")

