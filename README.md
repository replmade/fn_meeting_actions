# fn_meeting_actions
An AWS Lambda function triggered by an object creation in an S3 bucket that retrieves a meeting transcript and creates a list of action items from the meeting.

This AWS Lambda function is automatically triggered when a new meeting transcript is uploaded to a specified S3 bucket. It processes the transcript to identify action items and writes the resulting list of action items to another folder within the same S3 bucket. The function utilizes AWS Lambda for serverless compute, Amazon S3 for storage, and the Bedrock Runtime Converse API for generating action items from the transcript.

The default LLM is "anthropic.claude-3-5-sonnet-20240620-v1:0".