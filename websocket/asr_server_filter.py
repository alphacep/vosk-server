#!/usr/bin/env python3

import json
#import logging
from profanity_filter import ProfanityFilter
from profanity_check import predict

class Filter:

    def __init__(self):
        self.pf = ProfanityFilter()

    def filter(self, response: str):
        py_json_response = self.apply_filter(json.loads(response))
        return json.dumps(py_json_response)

    def apply_filter(self, response: dict):
        if "partial" in response:
            text_type = "partial"
        elif "text" in response:
            text_type = "text"
        transcript = response[text_type]
        has_profanity = predict([transcript])[0]
        #logging.info("Transcript is profane? %s", (transcript, has_profanity))
        if has_profanity:
            censored_transcript = self.pf.censor(transcript)
            response[text_type] = censored_transcript
        return response
