import os
import logging
from typing import Union
from fastapi import APIRouter, HTTPException, Response, status, Query, Depends
import schemas
from routers.oaut2 import get_current_user
from twilio.rest import Client 

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
    file_loc : str
        The file location of the spreadsheet
    print_cols : bool, optional
        A flag used to print the columns to the console (default is
        False)

    Returns
    -------
    list
        a list of strings used that are the header columns
    """
    twilio_client = Client({os.environ['TWILIO_SID']}, {os.environ['TWILIO_TOKEN']})
    # logging.debug(get_current_user.mobile)
    try:
        message = twilio_client.messages.create( 
                                    from_='whatsapp:+14155238886',  
                                    body=f"""
                                    *{news_title}* \n{news_url}
                                    """,
                                    to=f"whatsapp:+1{mobile}") 
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot Sent Whatsapp Message")

