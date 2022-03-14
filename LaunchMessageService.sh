#!/bin/bash
export PYTHONPATH='.'
if [ $USER == 'piyushgarg' ]
then
source ~/Desktop/AmoreFlask/amore_flask_venv/bin/activate
# elif [ $USER == 'kshitizsharma' ]
# then
# source ~/Desktop/AmoreFlask/amore_flask_venv/bin/activate
else
echo No Virtual Environment to activate
fi
python ~/Desktop/AmoreFlask/Services/MessagingService/RecentChatService.py